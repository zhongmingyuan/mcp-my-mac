# Call system_profiler with the allowed datatypes for Mac OS
import os

# limit the datatypes to enhance security
# TODO: revisit the datatypes
ALLOWED_DATATYPES = set(
    [
        "SPAirPortDataType",
        "SPApplicationsDataType",
        "SPAudioDataType",
        "SPBluetoothDataType",
        "SPCameraDataType",
        "SPDiagnosticsDataType",
        "SPDisplaysDataType",  # Display information (resolution, graphics)
        "SPFirewallDataType",
        "SPHardwareDataType",
        "SPLocationDataType",
        "SPMemoryDataType",
        "SPNetworkDataType",
        "SPNVMeDataType",  # NVMe storage details
        "SPPCIDataType",  # PCI devices information
        "SPPowerDataType",  # Battery and power information
        "SPSoftwareDataType",
        "SPStorageDataType",
        "SPThunderboltDataType",  # Thunderbolt connections
        "SPUSBDataType",  # USB devices
    ]
)


def load_system_profiler(datatype: str):
    if datatype not in ALLOWED_DATATYPES:
        raise ValueError(
            f"Invalid datatype: {datatype}. Allowed datatypes are: {ALLOWED_DATATYPES}"
        )
    return os.popen(f"system_profiler {datatype}").read()
