from mcp.server.fastmcp import FastMCP

from .readers.load_conda_info import (
    load_conda_env_list,
    load_conda_env_package_list,
    load_conda_info,
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
        return (
            conda_info
            + "\n\n"
            + conda_env_list
            + "\n\n"
            + f"Packages in {env_name}: \n\n{conda_env_package_list}"
        )

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


@mcp.tool(name="mcp_call_gpu_available_torch")
async def mcp_call_gpu_available_torch(env_name: str) -> bool:
    """
    Check if GPU is available in torch for a specific conda environment.
    Return True if GPU (Metal for M1, M2, M3, etc.) is available
    and installed in PyTorch, False otherwise.
    """
    return load_gpu_available_mac_torch(env_name)


def start_server():
    # Initialize and run the server
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    print("Starting MCP Server for MacOS System and Conda Information")
    start_server()
