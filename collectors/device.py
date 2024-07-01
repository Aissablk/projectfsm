from abc import ABC, abstractmethod
from error_handling import central_error_handler
from netmiko import ConnectHandler
import requests

class Device(ABC):

    def __init__(self, device_name, ip=None, username=None, password=None, logger=None):
        self.device_name = device_name
        self.ip = ip
        self.username = username
        self.password = password 
        self.data = None
        self.logger= logger
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def retrieve_data(self):
        pass

    def run(self):
        """Template method to interact with the device."""
        self.connect()
        self.retrieve_data()

class RestDevice(Device):
    @central_error_handler()
    def post(self, endpoint, data=None, headers={"Content-Type": "application/json"}):
            requests.packages.urllib3.disable_warnings()
            response = requests.post(endpoint, headers=headers, json=data, verify=False,timeout=10)
            response.raise_for_status()
            return response
    
    @central_error_handler()
    def get(self, endpoint, data=None, headers={"Content-Type": "application/json"}):
        requests.packages.urllib3.disable_warnings()
        response = requests.get(endpoint, headers=headers, params=data, verify=False,timeout=10)
        response.raise_for_status()
        return response



class SSHDevice(Device):
    @central_error_handler()
    def connection(self, device_type, ip, username, password):
            return ConnectHandler(device_type=device_type, host=ip, username=username, password=password)
    
    @central_error_handler()
    def send_command(self, commands):
        data_dict = {}
        for command in commands:
            output = self.connection.send_command(command)
            data_dict[command] = output
        return data_dict


