from abc import ABC, abstractmethod
from .device_data_model import DeviceDataModel
from .templates import NativeHandler
from error_handling import central_error_handler


class ConfigParser(ABC):
    """
    Base class for Parsers.
    
    Methods:
    ----------
    build_device_data(self, **kwargs) -> dict:
        Parse the provided keyword arguments and return a dictionary representation of the data.
    
    parse(self, config_data: dict)
        This method is an abstract method to be implemented in child parsers.
        It is responsible for parsing configuration data provided as a dictionary.
    
          
    
    """
    @central_error_handler()
    @abstractmethod
    def parse(self, config_data: dict):
        pass
    
        
    def build_device_data(self, **kwargs) -> dict:
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if value is not None
        }
        parsed_data = DeviceDataModel(**filtered_kwargs)
        return parsed_data.dict()
    
    def native_to_dict(self,config_data: dict):
        templater_instance = NativeHandler(config_data)  
        extracted_data = templater_instance.extract_data()
        return extracted_data
        
    
    
    


    

    
