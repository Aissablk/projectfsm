from .config_parser import ConfigParser
from .aci_parser import ACIParser
from .iosxe_parser import IOSXEParser
from .ios_parser import IOSParser
from .panos_parser import PANOSParser

from error_handling import central_error_handler

class ParserFactory:
    """
    A factory class for creating configuration parsers based on the operating system type.

    Attributes:
        None

    Methods:
        get_parser(os_type: str) -> ConfigParser:
            Create and return a configuration parser based on the specified operating system type.
    """

    @staticmethod
    @central_error_handler()
    def get_parser(os_type) -> ConfigParser:
        """
        Create and return a configuration parser based on the specified operating system type.

        Args:
            os_type (str): The operating system type for which to create a parser.

        Returns:
            ConfigParser: An instance of a configuration parser based on the specified OS type.
        """

        os = {
            'cisco_xe': IOSXEParser(),
            'cisco_ios': IOSParser(),
            'aci': ACIParser(),
            'panos': PANOSParser()
        }
        
        if os_type in os:
            return os[os_type]
        else:
            raise KeyError(f'Parsing for OS:{os_type} has not been implemented yet. OS supported are {list(os.keys())}')

