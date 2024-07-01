from .config_parser import ConfigParser
from error_handling import  PersistentError
from transformers import Transformer




class ACIParser(ConfigParser):
    """
    A class for parsing ACI configuration data(dict) returend from the APIC (the collector).

    This class extends the base `ConfigParser` class and implements the `parse` method to extract relevant
    information from a configuration dictionary and create a `list of dictionaries` containing extracted device information.

    Attributes:
        None

    Methods:
        parse(config_dict: dict) -> DeviceDataModel:
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
            self.parsed_items (list) : a list of dictionaries.
        """
    # Status maping from Fabirc Status to Netbox Status
        apic_to_netbox_status = {
            'unknown': 'inventory',
            'active': 'active',
            'inactive': 'offline',
            'undiscovered': 'planned',
            'discovering': 'staged',
            'disabled': 'decommissioning',
            'unsupported': 'failed'
        }
    # Getting releavent attributes
        site = config_data.get("site", "")
        tenant = config_data.get("device_tenant")
        location = config_data.get("device_location")
        region = config_data.get("region")
        config = config_data.get("nodes", [])
        if config == []:
            raise PersistentError(f"Device: {config_data.get('device_name')} returned empty data")
        
    # Lopping through the nodes
        for conf in config:
            
            # If the fabricnode return empty continue parsing
            keys = conf.get('fabricNode', {}).get('attributes', {})
            if keys == {}:
                continue
            
            # Getting attributes items
            config = conf.get("fabricNode").get("attributes", {})
            
            # When the admin state ('adSt': 'off') of node is set to off that nodes's Type,Interface Name, Platform Version return an empty values.
            # Thus it prevent Population of the node in Netbox, All these Values have been set to N/A
            management_ipv4 = config.get("topSystem", {}).get("oobMgmtAddr") or "0.0.0.0" 
            interface = config.get("mgmtMgmtIf", {}).get("id") or "N/A"
            speed = config.get("mgmtMgmtIf", {}).get("speed") or "N/A"
            interface_type = Transformer.return_standard(interface_value=speed)
            Type = config.get("model") or "N/A"
            version = config.get("version") or "N/A"
            
            # Setting the os_type based on the role
            if config.get('role') == 'leaf' or config.get('role') == 'spine':
                os_type = "cisco_nxos"
            elif config.get('role') == 'controller':
            # Controller node returns an empty Type (Type = '') value,thus it will prevent populating in Netbox.
            # Assuming that the the controller (apic) is responding to api requests, Type value was set to 'controller'  
                Type = "controller"
                os_type = 'apic'
            else:
                os_type = "N/A"
            
            
            parsed_item = self.build_device_data(
                Site=site,
                os_type=os_type,
                Type=Type,
                Platform_Version=version,
                Management_IPV4=management_ipv4,
                Interface=interface,
                Interface_Type=interface_type,
                Device_Name=config.get("name"),
                Device_Role=config.get("role"),
                # We get the Status, then map it to the appropriate Netbox Value.
                Status=apic_to_netbox_status.get(config.get("fabricSt")),
                Serial_Number=config.get("serial"),
                Tenant = tenant,
                Location = location,
                Region = region,
                Manufacturer="Cisco",    
            )
            
            self.parsed_items.append(parsed_item)

        return self.parsed_items
