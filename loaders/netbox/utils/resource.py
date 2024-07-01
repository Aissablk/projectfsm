class Resource:
    def __init__(self, netbox_session, resource_data):
        """
        Initialize the Resource class with the provided NetBox session, resource data, and endpoint.

        Args:
            netbox: An instance of the pynetbox API class.
            data (dict): The resource data for creation.
        """
        self.netbox_session = netbox_session
        self.resource_data = resource_data
    def create(self, endpoint1, endpoint2, logger):
        """
        Create a resource in the NetBox instance.

        Args:
            endpoint1 (str): The first part of the endpoint (e.g., 'dcim', 'ipam').
            endpoint2 (str): The second part of the endpoint (e.g., 'devices', 'interfaces').
            log (CustomLogger): An instance of CustomLogger for logging information and errors.

        Returns:
            dict or None: A dictionary containing information about the created resource,
            or None if an error occurs.
        """

        # Access the endpoint directly using the endpoint name
        endpoint = getattr(self.netbox_session.netbox, endpoint1)
        resource = getattr(endpoint, endpoint2)
   
            # Creating the resource
        resource_create = resource.create(self.resource_data)
            # Log the successful creation of the resource
        logger.info(f"Resource '{endpoint2}' created, data: {self.resource_data}")

        # Return all the data of the created resource
        return resource_create

    def update(self, endpoint1, endpoint2, logger):
        """
        update a resource in the NetBox instance.

        Args:
            endpoint1 (str): The first part of the endpoint (e.g., 'dcim', 'ipam').
            endpoint2 (str): The second part of the endpoint (e.g., 'devices', 'interfaces').
            log (CustomLogger): An instance of CustomLogger for logging information and errors.

        Returns:
            dict or None: A dictionary containing information about the update resource,
            or None if an error occurs.
        """

        # Access the endpoint directly using the endpoint name
        endpoint = getattr(self.netbox_session.netbox, endpoint1)
        resource = getattr(endpoint, endpoint2)

            #updationg the resource
        resource_update = resource.update([self.resource_data])
            # Log the successful update of the resource
        logger.info(f"Resource '{endpoint2}' updated, data: {self.resource_data}")


        # Return all the data of the updated resource
        return resource_update
    
    