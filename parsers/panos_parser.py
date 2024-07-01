from .config_parser import ConfigParser
from error_handling import PersistentError, log_setup

logger=log_setup()

class PANOSParser(ConfigParser):
    """
    A class for parsing Panorma Management System configuration data from a dictionary.

    This class extends the base `ConfigParser` class and implements the `parse` method to extract relevant
    information from a configuration dictionary and create a `list of dictionaries` containing extracted device information.

    Attributes:
        None

    Methods:
        parse(config_dict: dict) -> list:
            Parse the dictionary containing device configuration data and return a `list`
            of dictionaries containing extracted information.
    """
    def __init__(self):
        self.parsed_items = []
        
    def parse(self, config_data: dict) -> list:
        """
        Parse the dictionary containing device configuration data and return a `list of dictionaries` containing extracted device information.

        Args:
            config_dict (dict): A dictionary containing device configuration data.

        Returns:
            self.parsed_items (list) : A list populated with extracted data dictionaries.
        """
        os_type = config_data.get('os_type') 
        region = config_data.get('region') or "N/A"
        location = config_data.get('location') or "N/A"
        config = config_data.get('nodes',{})
        if config == {}:
            raise PersistentError(f"Device: {config_data.get('device_name')} returned empty data")
        for conf in  config.keys():
            device = config.get(conf)
            if not device.get('Hostname'):
                logger.error(f'Device Skipped: Device Does Not Have a Name')
                continue
            parsed_item = self.build_device_data(
                # Some Device have a null site
                        Site = device.get('Location') or "N/A",
                        Device_Name = device.get('Hostname'),
                        Device_Role = device.get('Type') or "N/A",
                        Type= device.get('Model') or "N/A",
                        Platform_Version = device.get('SW Version') or "N/A",
                        Management_IPV4 = device.get('IP Address') or "0.0.0.0",
                        Status = 'active',
                        Interface_Type="other",
                        Manufacturer = "Palo Alto",
                        os_type = os_type,
                # Empty Devices attributes are defaulted to N/A
                        Serial_Number = 'N/A',
                        Interface = 'N/A',
                        Region= region,
                        Location = location
                        
                        
                )
            parsed_item.pop('Tenant')
            
             
            self.parsed_items.append(parsed_item)

    
        return self.parsed_items
    
    

        