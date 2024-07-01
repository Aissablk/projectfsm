from .device import RestDevice

class ACIDevice(RestDevice):
    """
    A class to interact with Cisco ACI.

    Attributes:
        device_name (str): The name of the device.
        ip (str): The IP address or URL of the APIC.
        username (str): The username for APIC authentication.
        password (str): The password for APIC authentication.
        logger (logging.Logger): Logger instance to log messages.
        token (str): Authentication token obtained after successful connection to the APIC.
        data (dict): The data retrieved from the APIC after a successful connection.
    """
    def __init__(self, device_name, ip, username, password,device_tenant,logger):
        """
        Initializes an instance of the APIC class with the given IP address, username, and password.

        Args:
            ip (str): The IP address or URL of the APIC.
            username (str): The username for APIC authentication.
            password (str): The password for APIC authentication.
        """
        super().__init__(device_name, ip, username, password,logger)
        self.token = None
        self.logger = logger
        self.device_tenant = device_tenant
        
        
    def get_node_attribute(self,node, node_dn, attribute_key, headers):
        """
        This method queries the APIC for device interface data, specifically from the target subtree classes 'mgmtMgmtIf' and 'topSystem'.
        class mgmtMgmtIf: we get from it the interface name and speed(we use speed to determine the interface type).
        class topSystem:  we get from it the interface ip address (out-of-bound management ip address)
        
        all the data recieved will be be appnedend to the previous response that we got from the the 'fabricNode' class:
        
        {
            'fabricNode':
            {
              'attribute':
              {
                  'name': 'leaf'
                  'mgmtMgmtIf': {
                      'speed': '1G',
                      'id': 'mgmt0'
                  },
                  'topSystem': {
                      'oobMgmtAddr': '10.0.0.1'
                  }
              }  
            }
        }
        
        Args:
            node (dict): before this function is called, a for loop through all nodes, each node is a  dict, which is send updates with interface data keys and values.
            node_dn (str): this is extracted from the each node dict, and passed to this function, then to each endpoint reaquest to get its individual interface data.
            attribute_key (str): the target subtree classes 'mgmtMgmtIf' and 'topSystem'.
            headers (dict): requests headers.
        
        """
        
        endpoint = f"{self.ip}/api/node/mo/{node_dn}/sys.json?query-target=subtree&target-subtree-class={attribute_key}"
        response = self.get(endpoint, None, headers)
        if response.json()["imdata"]:
            attribute_data = response.json()["imdata"][0]
            node["fabricNode"]["attributes"][attribute_key] = attribute_data[attribute_key]["attributes"]
            
    def connect(self):
        """
        Authenticates with the APIC and retrieves an authentication token.

        This method attempts to log in to the APIC at the specified IP address using the provided
        username and password. If successful, it retrieves and stores an authentication token for
        subsequent requests.
        """
        
        endpoint = f"{self.ip}/api/aaaLogin.json"
        headers = {"Content-Type": "application/json"}
        data = {
            "aaaUser": {"attributes": {"name": self.username, "pwd": self.password}}
        }

        response = self.post(endpoint, data,headers)
        
        self.token = response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        if self.token:
            self.logger.info("Token retrieved successfully")
        else:
            raise self.logger.error("Token retrieval failed. Token is None or empty.")

    def retrieve_data(self):
        """
        Fetches device data from the APIC using the previously obtained authentication token.

        This method queries the APIC for device data, specifically from the 'fabricNode' class.
        The request uses the authentication token stored in the instance to authenticate the request.
        """
        headers = {
            "Cookie": "APIC-cookie=" + self.token,
            "Content-Type": "application/json",
        }
        self.data = []


        endpoint = f"{self.ip}/api/node/class/fabricNode.json"
        response = self.get(endpoint,None,headers)
        node_data = response.json()["imdata"]

        if node_data:
            
            for node in node_data:
                # In the case of admin state is off ('adSt':'off'), the inerface value will be empty ('').
                # to avoid error regarding fetching the interface name in the next code block, we continue.
                if node["fabricNode"]["attributes"]["adSt"] == 'off': 
                    self.data.append(node)  
                    continue
                 
                node_dn = node["fabricNode"]["attributes"]["dn"]  
                
                self.get_node_attribute(node, node_dn,"mgmtMgmtIf",headers)

                self.get_node_attribute(node, node_dn,"topSystem",headers)

                self.data.append(node)

            self.logger.info(f"{self.device_name} Data retrieved successfully")
            return True