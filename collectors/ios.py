from .device import SSHDevice

class IOSDevice(SSHDevice):
    """
    Collector class for devices running Cisco IOS operating system.
    """
    def __init__(self, device_name, ip, username, password, logger,device_type, device_role,device_tenant):
        super().__init__(device_name, ip, username, password, logger)
        self.device_type = device_type
        self.device_role = device_role
        self.logger = logger
        self.device_tenant = device_tenant
        

    def connect(self):
        """
        Establishes a connection to the IOS devices using the provided device details.

        Returns:
        - bool: True if the connection is successfully established, False otherwise.

        Raises:
        - PersistentError: If there's an authentication error or other persistent issues.
        - TransientError: If there's a temporary issue like a timeout.
        """
        self.connection = self.connection(device_type=self.device_type, ip=self.ip, username=self.username, password=self.password)
        self.logger.info(f"Successfully logged into {self.device_name}")
        return True

    def retrieve_data(self):
        """
        Retrieves data from the device using a set of commands.
        Fetches specific data from the IOS device using a set of commands.

        The following commands are executed on the device:
        - 'show version'
        - 'show platform status'
        - 'show interfaces'
        - 'show module'
        Attempts to use 'show platform status' and falls back to 'show module' if necessary.
        

        Returns:
            
        - bool: True if data is successfully retrieved, False otherwise.

        Raises:
        - PersistentError: If there's an error executing the commands on the device.
        """
        commands = [
            "show version",
            "show interfaces"
        ]

        try:
            output = self.send_command(["show platform status"])
            if "Invalid input detected" not in output["show platform status"]:
                commands.append("show platform status")     
            else:
                commands.append("show module")
        except Exception as e:
            self.logger.warning(f"Unable to execute 'show platform status' on {self.device_name}: {str(e)}")
            commands.append("show module")
            
            self.logger.warning(f"Unable to execute 'show module' on {self.device_name}: {str(e)}")

        self.data = self.send_command(commands)
        self.logger.info(f"{self.device_name} Data retrieved successfully")
        return True
