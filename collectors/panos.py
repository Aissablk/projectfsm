from .device import RestDevice

class PANOSDevice(RestDevice):
    """
    A class to interact with Panorma Management System.

    Attributes:
        device_name (str): The name of the device.
        ip (str): The IP address or URL of the Panorma Management System.
        logger (logging.Logger): Logger instance to log messages.
        data (dict): The data retrieved from the Panorma Management System.  after a successful connection.
    """
    def __init__(self, device_name, ip,logger):
        """
        Initializes an instance of the PANOSDevice class.

        Args:
            ip (str): The IP address or URL of the Panorma Management System..
        """
        super().__init__(device_name, ip,logger)
        self.logger = logger


    def connect(self):
         
        """
        In case there is an authentication process.
        """
        pass
    
        
 
    def retrieve_data(self):
        """
        Fetches device data from the Panorma Management System

        """
        
        self.data = {}
        endpoint = f"{self.ip}/paloalto/pa_devices.json"
        response = self.get(endpoint,None)
        data = response.json()
        self.data.update(data)
        self.logger.info(f"{self.device_name} Data retrieved successfully")
        return True