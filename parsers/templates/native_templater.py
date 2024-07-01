import textfsm
import os
from error_handling import central_error_handler, PersistentError
from functools import reduce
from transformers import Transformer
import jinja2  
from io import StringIO

class NativeHandler:
    """
    The NativeHandler class is responsible for handling native commands on network devices
    and extracting structured data using TextFSM templates.

    Attributes:
        base_dir (str): The base directory for storing TextFSM templates.
        templates (dict): A dictionary to store loaded TextFSM templates.
        config_data (dict): Configuration data containing information about the device.
        os_type (str): The operating system type of the network device.
        site (str): The site information of the network device.
        templates_dir (str): The directory path where TextFSM templates for the specific
                            operating system are stored.

    Methods:
        __init__(self, config_data: dict):
            Initializes a new NativeHandler instance with the given configuration data.

        load_templates(self):
            Loads TextFSM templates from the specified directory.

        extract_data(self):
            Extracts structured data from the provided configuration data using TextFSM templates.
            Returns a dictionary containing the extracted data.

    Example Usage:
        config_data = {
            'device_name': 'Router1',
            'os_type': 'ios',
            'site': 'HQ',
            'nodes': {
                'show_version': '...',
                'show_platform': '...',
                ...
            }
        }
        native_handler = NativeHandler(config_data)
        extracted_data = native_handler.extract_data()
    """

    def __init__(self, config_data: dict):
        self.base_dir = 'parsers/templates'
        self.templates = {}
        self.config_data = config_data
        self.os_type = config_data.get('os_type')
        self.site = config_data.get('site')
        self.device_ip = config_data.get('device_ip')
        self.device_role = config_data.get('device_role')
        self.device_tenant = config_data.get('device_tenant')
        self.device_location = config_data.get('device_location')
        self.region = config_data.get('region')
        self.templates_dir = f'{self.base_dir}/{self.os_type}'

    @central_error_handler()
    def load_templates(self,Management_IPV4=''):
        """
        Loads TextFSM templates from the specified directory and stores them in the templates dictionary.
        """
        template_files = [
            'show_version.textfsm',
            'show_interfaces.textfsm', 
            'show_platform_status.textfsm'
        ]

        for template_file in template_files:
            template_key = template_file.split('.')[0].replace('_', ' ')
            if os.path.exists(f'{self.templates_dir}/{template_file}'):
                with open(f'{self.templates_dir}/{template_file}') as template:
                    if template_key == 'show interfaces':
                        j2_template = jinja2.Template(template.read())
                        rendered_template = j2_template.render(Management_IPV4=Management_IPV4)
                        template = StringIO(rendered_template)
                     
                    self.templates[template_key] = textfsm.TextFSM(template) 

    
    def parse_show_module(self,data: str):
        with open(f"{self.templates_dir}/show_module.textfsm") as show_module_fsm:    
            normal_show_module_template = textfsm.TextFSM(show_module_fsm)
        with open(f"{self.templates_dir}/show_module_status.textfsm") as show_module_status_fsm:    
            status_show_module_template = textfsm.TextFSM(show_module_status_fsm)

        parsed_results_first_part = normal_show_module_template.ParseTextToDicts(data)
        parsed_results_second_part = status_show_module_template.ParseTextToDicts(data)

        required_mod_number = 0
        for item in parsed_results_first_part:
            if item["CARDTYPE"] == "Supervisor Engine 720 10GE (Active)":
                    required_mod_number = item["MODULE"]
        status = None
        for item in parsed_results_second_part:
            if item["MODULE"] == required_mod_number:
                status = item["STATUS"]
        return {"Status" : status}
        
    def parse_show_platform(self,data: dict):
         
        with open(f"{self.templates_dir}/show_platform1.textfsm") as template_file:
         template = textfsm.TextFSM(template_file)
        with open(f"{self.templates_dir}/show_platform2.textfsm") as template_files:
         template1 = textfsm.TextFSM(template_files)
        parsed_output_1=template1.ParseTextToDicts(data['nodes']['show platform'])
        print(parsed_output_1)
        parsed_output_2=template.ParseTextToDicts(data['nodes']['show platform']) 
        print(parsed_output_2)
        with open(f"{self.templates_dir}/show_version.textfsm") as show_module_fsm:    
            show_version_template = textfsm.TextFSM(show_module_fsm)
        parsed_show_version=show_version_template.ParseTextToDicts(data['nodes']['show version']) 
        print(parsed_show_version)
        parse=parsed_show_version[0]['Platform_Version']
        number_switch=1
        
        if parse=='17.7.1':
            state=""
            for item in  parsed_output_2:
                if item['ROLE']=='Active':
                    number_switch=item['SWITCH']
                    state = item["STATE"]
            model=''
            for item in parsed_output_1:
                if item["SWITCH"] == number_switch:
                    model = item["MODEL"]
            print(f"this is :{model} and this is {state}")
            return {'Type':model,
                     'Status':state 
                     }
        else:
            with open(f"{self.templates_dir}/show_platform.textfsm") as template_fil: 
                template3 = textfsm.TextFSM(template_fil)
            parsed_output_3=template3.ParseTextToDicts(data['nodes']['show platform'])
            for item in parsed_output_3:
               if item['Status']=='ok, active':
                    type_required=item['Type']   
                
            return {'Type':type_required,
                    'Status':'ok, active' 
                    }
         
        
        
        

    @central_error_handler()
    def extract_data(self):
        """
        Extracts structured data from the provided configuration data using TextFSM templates.

        Returns:
            dict: A dictionary containing the extracted data, including device information and node data.
        """
        
        extracted_data = {"device_name": f"{self.config_data.get('device_name')}",
                          "os_type": f"{self.os_type}",
                          "site": f"{self.site}",
                          "device_ip":f"{self.device_ip}",
                          "device_role": f"{self.device_role}",
                          "device_tenant": f"{self.device_tenant}",
                          "device_location": f"{self.device_location}",
                          "region": f"{self.region}",
                          "nodes": {}} 
        
        #Management_IPV4 = Transformer.return_host(extracted_data['device_ip'])
        #self.load_templates(Management_IPV4)
        self.load_templates()


        
                
        for key, data in self.config_data['nodes'].items():
            
            if key in self.templates and key != "show module" and key !="show platfrom":
                value = self.templates[key].ParseTextToDicts(data)
                
               
                if value != []:
                    
                    extracted_data['nodes'][key] = value[0]

                else:
                    raise PersistentError(f"Parsed Value for Key:'{key}' Returned empty  value: {value}")
           
            elif key == "show module":
                value = self.parse_show_module(data) 
                
                extracted_data['nodes'][key] = value
            elif key =="show platform":
                if self.os_type=='cisco_xe':
                    value=self.parse_show_platform(self.config_data)
                    extracted_data['nodes'][key] = value 
                else:
                    value=self.templates[key].ParseTextToDicts(data)
                    
                    if value != []:
                    
                        extracted_data['nodes'][key] = value[0]

                    else:
                        raise PersistentError(f"Parsed Value for Key:'{key}' Returned empty  value: {value}")
                
            else:
                raise KeyError(f"Command key:'{key}' was not found in the collected data. required keys are: {list(self.templates.keys())}")
                
        extracted_data['nodes'] = reduce(lambda x, y: {**x, **y}, extracted_data['nodes'].values())
        return extracted_data


