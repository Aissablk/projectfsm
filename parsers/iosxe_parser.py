from .config_parser import ConfigParser
from error_handling import  PersistentError
from transformers import Transformer



class IOSXEParser(ConfigParser):
    
    def __init__(self):
        self.parsed_items = []

    
    def parse(self, config_data: dict) -> list:
        """
        Parse the IOSXE configuration data and return a dict populated with extracted relevant data.

        Args:
            config_data (dict): configuration data dictionary.

        Returns:
            self.parsed_items(list): A list populated with extracted data dictionaries.
            
            
        """
        extracted_data = self.native_to_dict(config_data)
        conf = extracted_data.get('nodes',{})
        if conf == {}:
            raise PersistentError(f"Device: {extracted_data.get('device_name')} returned empty data")
        

        # Dictionary to map IOS XE status to Netbox status
        ios_xe_to_netbox_status = {
            'ok': 'active',
            'ok, active': 'active',
            'booting': 'staged',
            'init': 'staged',
            'disabled': 'offline',
            'unknown': 'offline',
            'shutdown': 'offline',
            'ok, standby': 'planned',
            'init, standby': 'planned',
            # i added the new state for the new device when excuting show platform command 
            'Ready': 'Active'
        }
        status = conf.get('Status')
        status = ios_xe_to_netbox_status.get(status, '')
        # Getting the interface type based on interface name
        interface = conf.get('Interface')
        interface_type = Transformer.return_standard(interface_value=interface)
        
        parsed_item = self.build_device_data(
            os_type = extracted_data.get('os_type'),
            Site = extracted_data.get('site'),
            Device_Role =  extracted_data.get('device_role'),
            Platform_Version = conf.get('Platform_Version'),
            Device_Name = conf.get('Device_Name'),
            Serial_Number = conf.get('Serial_Number'),
            Type = conf.get('Type'),
            Management_IPV4 = conf.get('Management_IPV4'),
            Interface = interface,
            Interface_Type = interface_type,    
            Status = status, 
            Manufacturer = "Cisco",
            Tenant = extracted_data.get('device_tenant'),
            Location = extracted_data.get('device_location'),
            Region = extracted_data.get('region')
            
            )
        
        self.parsed_items.append(parsed_item)
    
        return self.parsed_items
