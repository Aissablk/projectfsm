from .aci import ACIDevice
from .iosxe import IOSXEDevice
from .ios import IOSDevice
from .panos import PANOSDevice
from error_handling import central_error_handler
from error_handling import log_setup
from transformers import Transformer


class DeviceFactory:
    """Factory class to create device instances.

    This class contains a create_device method that takes in kwargs
    and returns an instance of a Device subclass based on the 
    device_type kwarg.

    Supported device types:
        - ACI
        - PANOS
        - cisco_xe
        - cisco_ios
    """
    @staticmethod
    @central_error_handler()
    def create_device(logger=log_setup(), **kwargs):
        device_type = Transformer.sanitize_slug(kwargs.get('device_type'))
        if device_type == "aci":
            kwargs.pop('device_type', None)
            return ACIDevice(logger=logger, **kwargs)
        elif device_type == "panos":
            # Remove username and password as PANOSDevice doesn't need them
            kwargs.pop('username', None)
            kwargs.pop('password', None)
            kwargs.pop('device_type', None)
            kwargs.pop('device_tenant', None)
            kwargs.pop('device_location', None)
            
            return PANOSDevice(logger=logger, **kwargs)
        elif device_type == "cisco_xe":
            return IOSXEDevice(logger=logger, **kwargs)
        
        elif device_type =="cisco_ios":
            return IOSDevice(logger=logger, **kwargs)
        #... more devices
        else:
            raise ValueError(f"Unsupported device type: {device_type}")
