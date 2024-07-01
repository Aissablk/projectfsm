from pydantic import BaseModel

class DeviceDataModel(BaseModel):
    """
    A Pydantic data model representing device information.

    This class inherits from Pydantic's `BaseModel` and defines attributes for various device properties.

    Attributes:
        Site (str, optional): The site where the device is located.
        Type (str, optional): The device type.
        Device_Role (str, optional): The role or function of the device.
        Status (str, optional): The status or operational state of the device.
        Serial_Number (str, optional): The serial number of the device.
        Platform_Version (str, optional): The platform or hardware version of the device.
        Manufacturer (str, optional): The manufacturer of the device.
        Management_IPV4 (str, optional): IPv4 addresses used for device management.
        Interface(str, optional): Name of Interface.
        Interface_Type(str, optional): Type of the Interface
        os_type (str, optional): The operating system type running on the device.
        Tenant (str, optional): The Tenant of the device.
        Location (str, optional): The Location of the the device.
        Region (str, optional): The Region of the the device.
    """
    Site: str = ''
    Type: str = ''
    Device_Name: str = ''
    Device_Role: str = ''
    Status: str = ''
    Serial_Number: str = ''
    Platform_Version: str = ''
    Manufacturer: str = ''
    Management_IPV4: str = ''
    Interface : str = ''
    Interface_Type : str = '' 
    os_type: str = ''
    Tenant: str = ''
    Location: str = ''
    Region: str = ''