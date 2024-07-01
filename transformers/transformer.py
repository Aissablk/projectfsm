import re
from socket import gethostbyname
from ipaddress import ip_address
from error_handling import central_error_handler

class Transformer:

    @staticmethod
    def sanitize_slug(slug):
        """
        Generate a slug for a resource from a name by replacing non-alphanumeric characters with underscores.

        Args:
            slug (str): The input slug.

        Returns:
            str: The sanitized slug.
        """
        # Replace all characters not matching the criteria with an empty string
        return re.sub("[^a-zA-Z0-9_-]", "", slug.lower())
    
    @staticmethod
    def sanitize_collector_device_type(type):
        """_summary_

        Args:
            type (string): device type

        Returns:
            string: correct form of device type
        """

        return str(type).upper()
    
    @staticmethod
    @central_error_handler()
    def return_host(host):
    
    
        """
        Return the IP address for the given domain name, or returns the IP address back if it is given an IP address.
        This method is used for IOS and IOSXE devices, to resolve the domain name of a device to an ip address or if given an IP address it just return it, to be used later to get the assosiated interface with it.
    
        Args:
            domain (str): The host name to resolve to IP address, or just return an IP address if given an IP address
    
        Returns:
        str: The IP address
        """
    
        try:
            verify_if_ip = ip_address(host)
            return verify_if_ip.__str__()
        except ValueError:
            return gethostbyname(host)
    
    @staticmethod
    @central_error_handler()
    def return_standard(interface_value):
        
        
        """
        Return the interface standard based on interface name or speed.
    
        Args:
            interface (str, optional): The interface name. Values like 'Ethernet', 'GigabitEthernet', etc.
            speed (str, optional): The interface speed. Values like  '100M', '1G', etc.
            
        Returns:
            str: The interface standard, e.g. '100base-tx', '10gbase-t', etc  or 'other' if no match.
        """
        interface_types = {
                # ios/iosxe
                'Ethernet': '100base-tx',
                'FastEthernet': '100base-tx',
                'GigabitEthernet': '1000base-t',
                'TenGigabitEthernet': '10gbase-t',
                'Loopback':'virtual',
                'Vlan':'virtual',
                'N/A': 'other',       
                
                # apic
                '10M': '100base-tx',
                '100M': '100base-tx',
                '1G': '1000base-t',
                '10G': '10gbase-t',
        }
        pattern_map = {
            'interface': '(Ethernet|FastEthernet|GigabitEthernet|TenGigabitEthernet|Loopback|Vlan|N/A)',
            'speed': '(10M|100M|1G|10G|N/A)'
        }
        standard = ''
        if interface_value:
            
            match = re.search(fr"{pattern_map['interface']}|{pattern_map['speed']}", interface_value)
            
            if match:
                standard = match.string[match.start():match.end()]
            else:
                standard = 'other'
        return interface_types.get(standard)
         
            
            
            
        
