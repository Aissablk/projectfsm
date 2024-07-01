# Device Configuration Parser

## Description
This project is a Python library designed to parse configurations of network equipment from different types and operating systems according to a Data Model.

## Project Tree
```
parsers/
├── README.md
├── templates
|   ├── cisco_ios
│   |   ├── show_interfaces.textfsm
│   |   ├── show_platform_status.textfsm
│   |   ├── show_version.textfsm
│   |   ├── show_module.textfsm
│   |   └── show_module_status.textfsm    
|   ├── cisco_xe
|   |   ├── show_interfaces.textfsm
|   |   ├── show_platform_status.textfsm
|   |   └── show_version.textfsm 
|   ├── __init__.py 
|   └── native_templater 
├── __init__.py
├── parser_factory.py 
├── config_parser.py
├── device_data_model.py
├── ios_parser.py
├── iosxe_parser.py
├── aci_parser.py
└── panos_parser.py
        
```
### Files  and Directories Descriptions


- **`__init__.py`:** This script is main execution point of the parsering phase.

- **File:** `parser_factory.py`
- **Description:** This script contains the  ParserFactory class, which simplifies the process of obtaining the appropriate configuration parser based on the given operating system type, ensuring consistency and ease of use in the network configuration parsing workflow.

- **File:** `config_parser.py`
- **Description:** This script contains The ConfigParser class, which a base class for parsers that provide methods for parsing and extracting device configuration information from a dictionary. It is designed to be subclassed and extended with specific parsing logic

- **File:** `device_data_model.py`
- **Description:** This script contains The DeviceDataModel class, which is  is a Pydantic data model for representing device information. This class inherits from Pydantic's BaseModel and defines attributes for various device properties. You can use it to validate and parse device-related data.

- **File:** `ios_parser.py`
- **Description:** This script contains the IOSParser class, which is designed to parse IOS device configuration data from a dictionary and create a structured representation of the device.

- **File:** `iosxe_parser.py`
- **Description:** This script contains the IOSXEParser class, which is designed to parse IOS XR device configuration data from a dictionary and create a structured representation of the device.

- **File:** `aci_parser.py`
- **Description:** This script contains the ACIParser class, which is specialized in parsing APIC configuration data from a dictionary and producing a list of dictionaries containing extracted device information.

- **File:** `panos_parser.py`
- **Description:** This script contains the PANOSParser class, which is specialized in parsing Panorma Management System configuration data from a dictionary and producing a list of dictionaries containing extracted device information.

- **Directory:** `templates`
- **Description:** This Directory contains specific Class for handling native output and textfsm templates to do so based on the operation system of the device.

## Architecture 
```

                                        +----------------------------------------------------+
                                        |         ConfigParser                               |
                                        | + build_device_data(self, **kwargs) -> dict        |
                                        |                                                    |
                                        | + native_to_dict (self, config_data: dict) -> dict |
                                        |                                                    |
                                        |                                                    |
                                        |                                                    |
                                        |                                                    |
                                        |                                                    |
                                        |                                                    |
                                        +------------------+---------------------------------+
                                                           |
                                                           |
                 ------------------------------------------+----------------------------------------+------------------------------------+                                                          
                 |                                         |                                        |                                    |
+----------------+-----------------+       +---------------+----------------------+   +-------------+-------------------------+     +----+-----------------------------------+                                                 
|                                  |       |                                      |   |                                       |     |                                        |                                        
|           IOSParser              |       |             IOSXEParser              |   |             ACIParser                |     |   PANOS Parser                         |                                
|                                  |       |                                      |   |                                       |     |                                        |         
| + parse(conf_data: dict) -> :list|       | + parse(self,conf_data: dict) -> list|   | + parse(self, conf_data: dict) -> list|     | + parse(self, conf_data: dict) -> list |    
|                                  |       |                                      |   |                                       |     |                                        |    
|                                  |       |                                      |   |                                       |     |                                        |    
|                                  |       |                                      |   |                                       |     |                                        |       
|                                  |       |                                      |   |                                       |     |                                        |    
|                                  |       |                                      |   |                                       |     |                                        |    
+-------------------+--------------+       +---------------+----------------------+   +---------------+-----------------------+     +-----------+----------------------------+                    
                    |                                      |                                          |                                         |          
           Inherits |                                      | Inherits                                 | Inherits                                | Inherits          
                    |                                      |                                          |                                         |          
                    +--------------------------------------+------------------------------------------+-----------------------------------------+          
                                                           |
                                                           |
                                        +------------------+-------------+
                                        |                                |
                                        |         ParserFactory          |
                                        |                                |
                                        | + get_parser(os_type: str)     |
                                        |   : ConfigParser               |
                                        |                                |
                                        +--------------------------------+                          

```

In this diagram:

    IOSParser and IOSXEParser and ACIParser and PANOSParser inherit from ConfigParser.
    ParserFactory uses ConfigParser to generate a specific instance based on the os_type.
    main.py uses ParserFactory to obtain an appropriate parser and perform the parsing work.

## Error Handling and Logging
Done using the error_handling module

