from .utils import NetBoxAPI, Resource
from error_handling import PersistentError, TransientError, central_error_handler
import json
from transformers import Transformer




@central_error_handler()
def manage_resource(netbox_session, resource_data, endpoint1, endpoint2, logger,action):
    """
    Create or update a resource in Netbox.

    This function creates or updates a resource object with the provided network and resource_data.
    It then uses this object to create a resource instance in Netbox by calling the 'create' method
    with the specified endpoints if 'action' is 'create'.
    If 'action' is 'update', it updates the existing resource with the new data.
    
    Args: 
        netbox_session (NetBoxAPI): The Netbox session.
        resource_data (dict): The data for the resource to be created or updated.
        endpoint1 (str): The first endpoint for the resource.
        endpoint2 (str): The second endpoint for the resource.
        logger (Logger): The logger instance.
        action (str): Action to perform, either 'create' or 'update'.

    Returns:
        int or pynetbox.core.response.RecordSet: The ID of the created or updated resource,
        or the created resource object.
    """
    # Create a new Resource object with the provided network and resource_data.
    resource = Resource(netbox_session, resource_data) 
    # Use the Resource object to create a resource instance by calling the 'create' method
    # with the specified endpoints.
    if action == 'create':
        resource = resource.create(endpoint1, endpoint2, logger)

    # Check if the 'created_resource' object has an attribute called 'id'.
        if hasattr(resource, "id"):
            return resource.id
        else:
            return resource 
        
    elif action == 'update' or action == 'selective_update':
         # Use the Resource object to create a resource instance by calling the 'update' method
         # some specified endpoints use the create method to avoid updating conflicts.
        if endpoint2 in ["tenants","device_types","regions","sites","locations","device_roles","platforms","custom-fields","manufacturers"]:
            resource = resource.create(endpoint1, endpoint2, logger)
        else:
            resource = resource.update(endpoint1, endpoint2, logger)
            
@central_error_handler()    
def load_and_fill_template(template_path, device_data, template_name, new_device_id, new_interface_id,old_id, old_int, old_ip, action):
    """
    Load a template and fill it with device data based on the specified action.

    This function reads a template from a file, replaces placeholders in the template with actual values,
    and then fills the template with additional data based on the template_name and action.
    
    Args:
        template_path (str): The path to the template file.
        device_data (dict): The data for the device.
        template_name (str): The name of the template.
        new_device_id (int): The ID of the new device (for 'create' action).
        new_interface_id (int): The ID of the new interface (for 'create' action).
        old_id (int): The ID of the existing resource (for 'update' action).
        old_int (int): The ID of the existing interface (for 'update' action).
        old_ip (str): The IP address of the existing resource (for 'update' action).
        action (str): The action to perform, either 'create' or 'update'.

    Returns:
        dict: The filled template.
    """
    with open(template_path, 'r') as file:
        template = file.read()

        # Replace placeholders with actual values
        for key, value in device_data.items():
            template = template.replace(f"{{{{ {key} }}}}", value)
            template = template.replace(f"{{{{ {key}_slug }}}}", Transformer.sanitize_slug(value))

        # Convert the template string to a Python object
        filled_template = json.loads(template)
        
        # Fill templates with additional data based on 'action'
        
        if action == 'create':
            # if panos device pop tenant and location because they are not used
            if device_data['os_type'] == 'panos' and template_name == 'device_template':
                filled_template['resource_data'].pop('location')
                filled_template['resource_data'].pop('tenant') 
                             
            if template_name == 'interface_template' and new_device_id:
                filled_template['resource_data']["device"]["id"] = new_device_id
                
            if template_name == 'ip_template':
                filled_template['resource_data']["assigned_object_id"] = new_interface_id
                               
                
        if action == 'update' or action == 'selective_update':
            if device_data['os_type'] == 'panos' and template_name == 'device_template':
                filled_template['resource_data'].pop('location')
                filled_template['resource_data'].pop('tenant') 
            if template_name == 'device_template':
                filled_template['resource_data']["id"] = old_id
                # Removing not needed keys for update
                filled_template['resource_data'].pop('name')
                filled_template['resource_data'].pop('device_type')
                filled_template['resource_data'].pop('site')
                filled_template['resource_data'].pop('serial')
                filled_template['resource_data'].pop('custom_fields')
                
                
                
            
            if template_name == 'ip_template':
                filled_template['resource_data']["id"] = old_ip
                filled_template['resource_data']["assigned_object_id"] = old_int
                filled_template['resource_data']["address"] = device_data['Management_IPV4']
                
            
            if template_name == 'interface_template':
                filled_template['resource_data']["id"] = old_int
                filled_template['resource_data']["name"] = device_data['Interface']
                filled_template['resource_data']["device"]["id"] = old_id
                filled_template['resource_data']["type"] = device_data['Interface_Type']       
        return filled_template
    
@central_error_handler()
def manage_resource_from_template(netbox_session, filled_template, action, logger):
    """
    Manage a resource in Netbox using a filled template.

    This function manages a resource in Netbox by calling the 'manage_resource' function
    with the provided filled_template, action, and logger. It then returns the managed resource.

    Args:
        netbox_session (NetBoxAPI): The Netbox session.
        filled_template (dict): The filled template containing resource data and endpoints.
        action (str): Action to perform, either 'create' or 'update'.
        logger (Logger): The logger instance.

    Returns:
        int or pynetbox.core.response.RecordSet: The ID of the managed resource or the managed resource object,
        or None if an error occurs.
    """
    try:
        created_resource = manage_resource(
            netbox_session=netbox_session,
            resource_data=filled_template['resource_data'],
            action=action,
            endpoint1=filled_template['endpoint1'],
            endpoint2=filled_template['endpoint2'],
            logger=logger,
        )
        return created_resource
    except (TransientError, PersistentError):
        return None

@central_error_handler()
def configure_device(netbox_session, device_data, resource_templates, logger,action):
    """
    Configure a device in Netbox based on provided templates and action.

    This function configures a device in Netbox by processing each template in the 'resource_templates' list.
    It loads the template based on the provided 'action' and 'template_name', fills it with device_data,
    and then manages the resource in Netbox using 'manage_resource_from_template' function.


    Args:
        netbox_session (NetBoxAPI): The Netbox session.
        device_data (dict): The data for the device.
        resource_templates (list): A list of template names to process.
        logger (Logger): The logger instance.
        action (str): Action to perform, either 'create' or 'update'.

    Returns:
        None
    """
  
    global new_device_id
    global new_ip_id
    global device_key
    global device_tenant
    device_key = f"{device_data['Device_Name']}@{device_data['Site']}"
    new_interface_id = None
    new_device_id = None
    new_ip_id = None
    device_tenant = None
    old_id = None
    old_int = None
    old_ip = None

    if action == 'update' or action == 'selective_update':
        device, interface, ip = get_existing_devices(netbox_api=netbox_session,device_key=device_key)
        old_id = device.id
        old_int = interface.id
        old_ip = ip.id 
   
    for template_name in resource_templates:
        template_path = f'loaders/netbox/templates/{template_name}'
        filled_template = load_and_fill_template(template_path, device_data, template_name, new_device_id, new_interface_id,old_id, old_int, old_ip, action)
        created_resource = manage_resource_from_template(netbox_session, filled_template, action, logger)

        if action == 'create':
            if template_name == 'device_template':
                new_device_id = created_resource
            if template_name == 'interface_template':
                new_interface_id = created_resource
            if template_name == 'ip_template':
                new_ip_id = created_resource
                

                
                

            

                
            
        
@central_error_handler()
def determine_resource_templates(device_data,netbox_api, action):
    """
    Determine the resource templates based on the device data and action.

    This function determines the list of resource templates to be used based on the provided 'device_data'
    and the action ('create' or 'update'). It constructs a list of template names to process
    for configuring the device in Netbox.

    Args:
        device_data (dict): The data for the device.
        netbox_api (NetBoxAPI): The Netbox session.
        action (str): Action to perform, either 'create' or 'update'.

    Returns:
        list: A list of template names to process for configuring the device.
    """
    
    device_key = f"{device_data['Device_Name']}@{device_data['Site']}"
    interface_name =  f"{device_data['Interface']}"
    ip = device_data['Management_IPV4']
    
    resource_templates = ['tenant_template','region_template','site_template','location_template','manufacturer_template', 'type_template','os_type_custom_field_template','role_template','platform_template']
    # if panos device remove tenant and location templates
    if device_data['os_type'] == 'panos':
        resource_templates.remove('location_template')
        resource_templates.remove('tenant_template')
    if action == 'create':
        resource_templates.extend(['device_template','interface_template','ip_template'])
      
    if action == 'update' or action == 'selective_update':
        device,interface,ip_address = get_existing_devices(netbox_api=netbox_api,device_key=device_key)
        
        if interface.name == interface_name and ip_address.address == f'{ip}/32':
            resource_templates.extend(['device_template'])
        
        if interface.name != interface_name:    
            resource_templates.extend(['device_template','interface_template'])
            
        if ip_address.address != f'{ip}/32':
            resource_templates.extend(['device_template','ip_template'])
            
    
    return resource_templates

@central_error_handler()     
def get_existing_devices(netbox_api,device_key):
    """
    Get existing device, interface, and IP address from Netbox for updating.

    This function retrieves the existing device, interface, and IP address
    information from Netbox based on the provided 'device_key'.
    It is used when the action is set to 'update'.

    Args:
        netbox_api (NetBoxAPI): The Netbox session.
        device_key (str): The key for the device in the format "Device_Name@Site".

    Returns:
        tuple: A tuple containing the device, interface, and IP address objects.
    """
    
    name, site = device_key.split('@')
    site = Transformer.sanitize_slug(site)
    device = netbox_api.netbox.dcim.devices.get(name=name,site=site)
    
    interface = netbox_api.netbox.dcim.interfaces.get(device_id=device.id)
    
    ip_address = netbox_api.netbox.ipam.ip_addresses.get(interface_id=interface.id)  
 
    return device,interface,ip_address  




class Populate_netbox:
    """
    A class for populating data in NetBox.

    Args:
        netbox_conf (dict): Configuration settings for NetBox.
        logger: Logger object for logging messages.
        http_session (bool, optional): Flag indicating whether to use an existing HTTP session. Defaults to False.
    """

    def __init__(self, netbox_conf, logger, http_session=False):
        self.logger = logger
        self.netbox_session = NetBoxAPI(
            netbox_url=netbox_conf["netbox_url"],
            netbox_token=netbox_conf["netbox_token"],
            http_session=http_session,
            logger=self.logger,
        )

    @central_error_handler()
    def check_connection(self):      
        self.netbox_session.netbox.dcim.sites.count()
    
    @central_error_handler()
    def populate(self, devices_data,action):
        for data in devices_data:            
            
            try:
                resource_templates = determine_resource_templates(data,self.netbox_session,action)  
                configure_device(
                    netbox_session=self.netbox_session,
                    device_data=data,
                    resource_templates=resource_templates,
                    logger=self.logger,
                    action=action
                )
                if action=='create':
                    name, site = device_key.split('@')
                    site = Transformer.sanitize_slug(site)
                    device = self.netbox_session.netbox.dcim.devices.get(name=name,site=site)
                    if new_ip_id !=None:
                        device.primary_ip4 = new_ip_id
                        device.save()
                    else:
                        pass
                                      
            except (TransientError, PersistentError):
                continue
    
    
