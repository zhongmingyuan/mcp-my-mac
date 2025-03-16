from setuptools import find_packages, setup

# Read the contents of README.md file (with error handling)
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = (
        "No README.md file found. Please create one for package description."
    )

# Get version from __version__.py if it exists, otherwise use default
version = "0.1.0"

setup(
    # Package name - this is what users will use when installing with pip
    # Use lowercase and hyphens (not underscores) for PyPI
    name="mcp-my-mac",
    # Version from __version__.py or default
    version=version,
    # Author information
    author="Mingyuan Zhong",
    author_email="personalaitools2025@gmail.com",
    # Short description (shows on PyPI)
    description="A concise description of your package",
    # Long description (from README.md)
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Project URL (typically GitHub repository)
    url="https://github.com/zhongmingyuan/mcp-my-mac",
    # Find packages automatically (looks for __init__.py files)
    # The 'exclude' parameter helps prevent test packages from being included
    packages=find_packages(exclude=["tests", "tests.*"]),
    # Required dependencies
    install_requires=[
        # List your dependencies here, e.g.:
        # "requests>=2.25.1",
        # "numpy>=1.20.0",
    ],
    # Optional dependencies
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        # 'optional': ['some-package'],
    },
    # Include non-Python files (like data files)
    package_data={
        # 'your_package': ['data/*.json'],
    },
    # Ensures package data is included in wheel
    include_package_data=True,
    # Python version requirements - use a more modern version
    python_requires=">=3.10",
    # Project classification
    classifiers=[
        "Development Status :: 3 - Alpha",  # Options: Alpha, Beta, Production/Stable
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Change to your license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
    # Keywords for your package (helps with search)
    keywords="sample, package, setup",
    # Entry points - defines command-line scripts
    entry_points={
        "console_scripts": [
            "mcp-my-mac=mcp_server_my_mac.server:main",
        ],
    },
)
