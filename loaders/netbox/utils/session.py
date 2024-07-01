import pynetbox

class NetBoxAPI:
    """summary
    """
    def __init__(self, netbox_url, netbox_token, http_session, logger):
        """
        Initialize the NetBoxAPI class with the provided NetBox URL and API token.

        Args:
            netbox_url (str): The URL of the NetBox instance.
            netbox_token (str): The API token for authentication.
            http_session (bool):  Enables or disables HTTPS certificate validation for requests made using this Pynetbox API instance.
        """
        # Initialize the NetBox API session with the provided URL and token
        self.netbox = pynetbox.api(url=netbox_url, token=netbox_token)
        self.netbox.http_session.verify = http_session


