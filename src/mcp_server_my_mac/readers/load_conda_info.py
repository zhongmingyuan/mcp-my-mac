import json
import logging
import os
import platform
import subprocess
import tempfile
from pathlib import Path


def find_conda_executable():
    """Find the conda executable path even when conda is not activated."""
    # Common paths where conda might be installed on macOS
    possible_conda_paths = [
        # Standard Anaconda/Miniconda locations
        os.path.expanduser("~/miniconda3/bin/conda"),
        os.path.expanduser("~/anaconda3/bin/conda"),
        os.path.expanduser("~/opt/miniconda3/bin/conda"),
        os.path.expanduser("~/opt/anaconda3/bin/conda"),
        "/opt/miniconda3/bin/conda",
        "/opt/anaconda3/bin/conda",
        # Add miniforge/mambaforge common paths
        os.path.expanduser("~/miniforge3/bin/conda"),
        os.path.expanduser("~/mambaforge/bin/conda"),
        # Applications directory on macOS
        "/Applications/anaconda3/bin/conda",
        "/Applications/miniconda3/bin/conda",
        # Add M1/M2 Mac specific paths
        "/opt/homebrew/anaconda3/bin/conda",
        "/opt/homebrew/miniconda3/bin/conda",
    ]

    found_paths = []

    # First check if conda is in PATH
    try:
        result = subprocess.run(["which", "conda"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            path = result.stdout.strip()
            found_paths.append(f"Found in PATH: {path}")

            # Extract the actual path if it's a function
            if "conda ()" in path:
                # Try to find the actual executable by inspecting shell aliases
                try:
                    alias_result = subprocess.run(["type", "conda"], capture_output=True, text=True, shell=True)
                    if alias_result.returncode == 0:
                        path_lines = alias_result.stdout.strip().split("\n")
                        for line in path_lines:
                            if "/conda" in line and ("bin/" in line or "Scripts/" in line):
                                potential_path = line.split("'")[-2] if "'" in line else line.split()[-1]
                                if os.path.isfile(potential_path):
                                    found_paths.append(f"Extracted from alias: {potential_path}")
                                    return potential_path
                except Exception as e:
                    found_paths.append(f"Error analyzing conda alias: {str(e)}")
            else:
                # Direct path found in PATH
                return path
    except Exception as e:
        found_paths.append(f"Error checking PATH: {str(e)}")

    # Check common installation paths
    for path in possible_conda_paths:
        if os.path.isfile(path):
            found_paths.append(f"Found in common paths: {path}")
            return path

    # Check for Conda installed via Homebrew
    try:
        result = subprocess.run(["brew", "--prefix", "conda"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            brew_path = os.path.join(result.stdout.strip(), "bin", "conda")
            if os.path.isfile(brew_path):
                found_paths.append(f"Found via Homebrew: {brew_path}")
                return brew_path
    except Exception as e:
        found_paths.append(f"Error checking Homebrew: {str(e)}")

    # Look for conda-related files in the home directory
    try:
        home = Path.home()
        for conda_dir in home.glob("*conda*"):
            if conda_dir.is_dir():
                bin_dir = conda_dir / "bin"
                if bin_dir.is_dir():
                    conda_path = bin_dir / "conda"
                    if conda_path.is_file():
                        found_paths.append(f"Found in home directory: {str(conda_path)}")
                        return str(conda_path)
    except Exception as e:
        found_paths.append(f"Error searching home directory: {str(e)}")

    # If we reach here, we didn't find conda
    return None


def load_conda_info():
    """Get basic conda info if available."""
    conda_path = find_conda_executable()
    if not conda_path:
        return "Conda not found"

    try:
        result = subprocess.run([conda_path, "info"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error getting conda info: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


def load_conda_env_list():
    """Get conda environment list with improved detection."""
    conda_path = find_conda_executable()

    if not conda_path:
        # Provide more detailed information about the system
        system_info = f"System: {platform.system()} {platform.release()} ({platform.machine()})\n"
        paths_info = "PATH directories:\n" + "\n".join([f"- {p}" for p in os.environ.get("PATH", "").split(":")])

        error_message = "Conda executable not found. Please ensure Conda is installed."

        return f"{error_message}\n{system_info}\n{paths_info}"

    try:
        # First try the JSON format for better parsing
        result = subprocess.run([conda_path, "env", "list", "--json"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            try:
                env_data = json.loads(result.stdout)
                output = f"Conda found at: {conda_path}\n\nConda Environments:\n"
                for env in env_data.get("envs", []):
                    env_name = os.path.basename(env) if not env.endswith("base") else "base"
                    output += f"- {env_name} ({env})\n"
                return output
            except json.JSONDecodeError:
                pass

        # Fallback to standard format if JSON fails
        result = subprocess.run([conda_path, "env", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            output = f"Conda found at: {conda_path}\n\n{result.stdout}"
            if not result.stdout.strip():
                return f"Conda found at: {conda_path}\n\nNo conda environments found."
            return output
        else:
            return f"Conda found at: {conda_path}\n\n" f"Error listing conda environments: {result.stderr}"
    except Exception as e:
        return f"Error retrieving conda environments: {str(e)}"


def load_conda_env_package_list(env_name: str):
    """Get the list of packages in the specified conda environment."""
    conda_path = find_conda_executable()

    # Validate environment name for security
    if not env_name:
        return "Environment name cannot be empty."

    # Sanitize input to prevent command injection
    if not (env_name.startswith("/") or env_name.isalnum() or all(c.isalnum() or c in "_-." for c in env_name)):
        return "Invalid environment name. Use alphanumeric characters, _, -, or . only."

    # Path validation for security
    if env_name.startswith("/"):
        # Extra validation for paths to prevent traversal attacks
        normalized_path = os.path.normpath(env_name)
        if ".." in normalized_path or not os.path.exists(normalized_path):
            return f"Invalid or non-existent environment path: {env_name}"

    if not conda_path:
        return "Conda executable not found. Please ensure Conda is installed."

    try:
        if env_name.startswith("/"):
            # Use --prefix for paths
            result = subprocess.run(
                [conda_path, "list", "--prefix", env_name],
                capture_output=True,
                text=True,
            )
        else:
            # Use --name for named environments
            result = subprocess.run([conda_path, "list", "--name", env_name], capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error listing packages in {env_name}: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


def load_gpu_available_mac_torch(env_name: str) -> dict:
    """Get detailed information about PyTorch and MPS capabilities on Mac in the specified conda environment."""
    conda_executable = find_conda_executable()
    if not conda_executable:
        return {"error": "Conda executable not found"}

    # Create a temporary Python script
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as f:
        f.write(
            "import torch\n"
            "import platform\n"
            "import sys\n"
            "import json\n"
            "import time\n"
            "\n"
            "info = {\n"
            "    'torch_version': torch.__version__,\n"
            "    'python_version': sys.version.split()[0],\n"
            "    'platform': platform.platform(),\n"
            "    'processor': platform.processor(),\n"
            "    'architecture': platform.machine(),\n"
            "    'mps_available': torch.backends.mps.is_available(),\n"
            "    'mps_built': torch.backends.mps.is_built(),\n"
            "    'benchmarks': []\n"
            "}\n"
            "\n"
            "# Try to get device information if MPS is available\n"
            "if torch.backends.mps.is_available():\n"
            "    try:\n"
            "        # Test MPS with a small tensor operation\n"
            "        device = torch.device('mps')\n"
            "        x = torch.ones(10, 10, device=device)\n"
            "        y = x + x\n"
            "        info['mps_functional'] = bool((y == 2).all().item())\n"
            "        \n"
            "        # GPU vs CPU benchmark\n"
            "        matrix_sizes = [5000]  # Test with different sizes\n"
            "        \n"
            "        for size in matrix_sizes:\n"
            "            benchmark = {'size': size}\n"
            "            \n"
            "            # CPU benchmark\n"
            "            a_cpu = torch.randn(size, size)\n"
            "            b_cpu = torch.randn(size, size)\n"
            "            start = time.time()\n"
            "            c_cpu = torch.matmul(a_cpu, b_cpu)\n"
            "            cpu_time = time.time() - start\n"
            "            benchmark['cpu_time'] = cpu_time\n"
            "            \n"
            "            # MPS benchmark\n"
            "            a_mps = torch.randn(size, size, device=device)\n"
            "            b_mps = torch.randn(size, size, device=device)\n"
            "            torch.mps.synchronize()\n"
            "            start = time.time()\n"
            "            c_mps = torch.matmul(a_mps, b_mps)\n"
            "            torch.mps.synchronize()\n"
            "            mps_time = time.time() - start\n"
            "            benchmark['mps_time'] = mps_time\n"
            "            \n"
            "            # Calculate speedup\n"
            "            benchmark['speedup'] = cpu_time / mps_time if mps_time > 0 else 0\n"
            "            info['benchmarks'].append(benchmark)\n"
            "        \n"
            "    except Exception as e:\n"
            "        info['mps_error'] = str(e)\n"
            "        info['mps_functional'] = False\n"
            "else:\n"
            "    # Get reason why MPS is not available\n"
            "    info['mps_not_available_reason'] = 'PyTorch not built with MPS support' "
            "if not torch.backends.mps.is_built() else 'Hardware/OS not supported'\n"
            "\n"
            "print(json.dumps(info))"
        )
        script_path = f.name

    try:
        # Create a clean environment without venv variables
        clean_env = os.environ.copy()

        # Remove virtual environment variables that might interfere
        for var in list(clean_env.keys()):
            if var.startswith("VIRTUAL_ENV") or var.startswith("PYTHONHOME"):
                clean_env.pop(var, None)

        # Update PATH to remove .venv entries
        if "PATH" in clean_env:
            path_parts = clean_env["PATH"].split(os.pathsep)
            clean_path = os.pathsep.join([p for p in path_parts if ".venv" not in p])
            clean_env["PATH"] = clean_path

        # Execute with clean environment
        command = f"{conda_executable} run -n {env_name} python {script_path}"
        logging.debug(f"Executing: {command}")

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=clean_env,  # Use the clean environment
        )

        if result.returncode == 0:
            try:
                gpu_info = json.loads(result.stdout.strip())
                logging.info(f"PyTorch MPS check: {gpu_info}")
                return gpu_info
            except json.JSONDecodeError:
                error_msg = f"Failed to parse PyTorch output: {result.stdout}"
                logging.error(error_msg)
                return {"error": error_msg, "raw_output": result.stdout}
        else:
            error_msg = f"Failed to check PyTorch MPS availability: {result.stderr}"
            logging.error(error_msg)
            return {"error": error_msg, "returncode": result.returncode}
    finally:
        # Clean up the temporary file
        os.remove(script_path)


def load_gpu_available_mac_tensorflow_benchmarks(env_name: str) -> dict:
    """Get detailed information about TensorFlow and MPS capabilities on Mac in the specified conda environment."""
    conda_executable = find_conda_executable()
    if not conda_executable:
        return {"error": "Conda executable not found"}

    # Create a temporary Python script
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as f:
        f.write(
            "import tensorflow as tf\n"
            "import platform\n"
            "import sys\n"
            "import json\n"
            "import time\n"
            "import numpy as np\n"
            "\n"
            "info = {\n"
            "    'tf_version': tf.__version__,\n"
            "    'python_version': sys.version.split()[0],\n"
            "    'platform': platform.platform(),\n"
            "    'processor': platform.processor(),\n"
            "    'architecture': platform.machine(),\n"
            "    'gpu_devices': tf.config.list_physical_devices('GPU'),\n"
            "    'benchmarks': []\n"
            "}\n"
            "\n"
            "try:\n"
            "    # Check if MPS is available\n"
            "    info['mps_available'] = len(tf.config.list_physical_devices('GPU')) > 0\n"
            "    \n"
            "    if info['mps_available']:\n"
            "        # Test with matrix multiplication benchmark\n"
            "        matrix_sizes = [5000]  # Test with different sizes\n"
            "        \n"
            "        for size in matrix_sizes:\n"
            "            benchmark = {'size': size}\n"
            "            \n"
            "            # CPU benchmark\n"
            "            with tf.device('/CPU:0'):\n"
            "                a_cpu = tf.random.normal([size, size])\n"
            "                b_cpu = tf.random.normal([size, size])\n"
            "                start = time.time()\n"
            "                c_cpu = tf.matmul(a_cpu, b_cpu)\n"
            "                _ = c_cpu.numpy()  # Force execution\n"
            "                cpu_time = time.time() - start\n"
            "                benchmark['cpu_time'] = cpu_time\n"
            "            \n"
            "            # GPU/MPS benchmark\n"
            "            with tf.device('/GPU:0'):\n"
            "                a_gpu = tf.random.normal([size, size])\n"
            "                b_gpu = tf.random.normal([size, size])\n"
            "                # Warmup run\n"
            "                _ = tf.matmul(a_gpu, b_gpu).numpy()\n"
            "                \n"
            "                start = time.time()\n"
            "                c_gpu = tf.matmul(a_gpu, b_gpu)\n"
            "                _ = c_gpu.numpy()  # Force execution\n"
            "                gpu_time = time.time() - start\n"
            "                benchmark['gpu_time'] = gpu_time\n"
            "            \n"
            "            # Calculate speedup\n"
            "            benchmark['speedup'] = cpu_time / gpu_time if gpu_time > 0 else 0\n"
            "            info['benchmarks'].append(benchmark)\n"
            "            \n"
            "        info['mps_functional'] = True\n"
            "except Exception as e:\n"
            "    info['error'] = str(e)\n"
            "    info['mps_functional'] = False\n"
            "\n"
            "print(json.dumps(info))"
        )
        script_path = f.name

    try:
        # Create a clean environment without venv variables
        clean_env = os.environ.copy()

        # Remove virtual environment variables that might interfere
        for var in list(clean_env.keys()):
            if var.startswith("VIRTUAL_ENV") or var.startswith("PYTHONHOME"):
                clean_env.pop(var, None)

        # Update PATH to remove .venv entries
        if "PATH" in clean_env:
            path_parts = clean_env["PATH"].split(os.pathsep)
            clean_path = os.pathsep.join([p for p in path_parts if ".venv" not in p])
            clean_env["PATH"] = clean_path

        # Execute with clean environment
        command = f"{conda_executable} run -n {env_name} python {script_path}"
        logging.debug(f"Executing: {command}")

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=clean_env,
        )

        if result.returncode == 0:
            try:
                gpu_info = json.loads(result.stdout.strip())
                logging.info(f"TensorFlow MPS check: {gpu_info}")
                return gpu_info
            except json.JSONDecodeError:
                error_msg = f"Failed to parse TensorFlow output: {result.stdout}"
                logging.error(error_msg)
                return {"error": error_msg, "raw_output": result.stdout}
        else:
            error_msg = f"Failed to check TensorFlow MPS availability: {result.stderr}"
            logging.error(error_msg)
            return {"error": error_msg, "returncode": result.returncode}
    finally:
        # Clean up the temporary file
        os.remove(script_path)
