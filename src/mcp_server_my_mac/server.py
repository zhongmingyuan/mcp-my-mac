from mcp.server.fastmcp import FastMCP

from .readers.load_conda_info import (
    load_conda_env_list,
    load_conda_env_package_list,
    load_conda_info,
    load_gpu_available_mac_tensorflow_benchmarks,
    load_gpu_available_mac_torch,
)
from .readers.load_system_profiler import load_system_profiler

# Initialize the MCP server
mcp = FastMCP("mcp-server-mac-info")

# Define the tools


@mcp.tool(name="mcp_call_conda_info")
async def mcp_call_conda_info(env_name=None) -> str:
    """Get comprehensive information about the Conda installation on this
    system.

    If env_name is provided, it will return the information for the specified
    environment as well.

    Returns detailed information including:
    - Conda version and configuration
    - Python version and virtual packages
    - Base environment location
    - Channel URLs and package cache locations
    - Platform and system details
    - Complete list of all Conda environments with their paths
    - Complete list of all packages in the specified environment and their versions

    This is useful for diagnosing Conda-related issues or understanding
    the Python environment configuration on this system.
    """
    conda_info = load_conda_info()
    conda_env_list = load_conda_env_list()
    # check None and if it is a string
    if env_name and isinstance(env_name, str):
        conda_env_package_list = load_conda_env_package_list(env_name)
        return f"{conda_info}\n\n{conda_env_list}\n\nPackages in {env_name}:\n\n{conda_env_package_list}"

    return conda_info + "\n\n" + conda_env_list


@mcp.tool(name="mcp_call_mac_system_profiler")
async def mcp_call_mac_system_profiler(datatype: str) -> str:
    """
    Call the system_profiler with the given datatype. Allow LLM to deepdive into the
    system information.
    This function is used to get the system information to help user to understand the
    system and potentially debug.

    Allowed datatypes:
        - SPAirPortDataType - Airport/WiFi information
        - SPApplicationsDataType - Application information
        - SPAudioDataType - Audio device information
        - SPBluetoothDataType - Bluetooth information
        - SPCameraDataType - Camera information
        - SPDiagnosticsDataType - Diagnostic information
        - SPDisplaysDataType - Display and graphics information
        - SPFirewallDataType - Firewall settings
        - SPHardwareDataType - Hardware specifications
        - SPLocationDataType - Location services information
        - SPMemoryDataType - Memory information
        - SPNetworkDataType - Network settings and interfaces
        - SPNVMeDataType - NVMe storage details
        - SPPCIDataType - PCI devices information
        - SPPowerDataType - Battery and power information
        - SPSoftwareDataType - Software and OS information
        - SPStorageDataType - Storage devices and volumes
        - SPThunderboltDataType - Thunderbolt ports and connections
        - SPUSBDataType - USB devices and connections
    """
    return load_system_profiler(datatype)


@mcp.tool(name="mcp_call_gpu_available")
async def mcp_call_gpu_available(env_name: str, framework: str = "torch") -> dict:
    """
    Check if GPU is available in torch for a specific conda environment.
    Input: torch or tensorflow
    if framework is not provided, it will default to torch.

    Returns a detailed dictionary with the following information:
    - "torch_version": PyTorch version string
    - "python_version": Python version string
    - "platform": Platform information string
    - "processor": Processor type
    - "architecture": CPU architecture
    - "mps_available": True if MPS (Metal Performance Shaders) is available
    - "mps_built": True if PyTorch was built with MPS support
    - "mps_functional": True if MPS is functional, False otherwise
    - "benchmarks": A list of benchmark results for different matrix sizes, each containing:
      - "size": Matrix size used for benchmark
      - "cpu_time": Time taken on CPU (seconds)
      - "mps_time": Time taken on MPS (seconds)
      - "speedup": Ratio of CPU time to MPS time (higher means MPS is faster)

    This helps determine if GPU acceleration via Apple's Metal is properly configured
    and functioning, with performance benchmarks for comparison.
    """
    if framework == "torch":
        return load_gpu_available_mac_torch(env_name)
    elif framework == "tensorflow":
        return load_gpu_available_mac_tensorflow_benchmarks(env_name)
    return {"error": "Framework not supported"}


def start_server():
    # Initialize and run the server
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    print("Starting MCP Server for MacOS System and Conda Information")
    start_server()
