## Templates Directory

This directory contains TextFSM templates for parsing the output of native commands on network devices. The templates are organized by the operating system type of the network devices.

## Directory Structure

```


```
├── cisco_ios
│   ├── show_interfaces.textfsm
│   ├── show_platform_status.textfsm
│   ├── show_version.textfsm
│   ├── show_module.textfsm
│   └── show_module_status.textfsm
├── cisco_xe
│   ├── show_interfaces.textfsm
│   ├── show_platform.textfsm
│   └── show_version.textfsm
├── __init__.py
└── native_templater.py
```

## TextFSM Templates

The TextFSM templates are used to parse the output of native commands on network devices. Each template is named after the command it is designed to parse. For example, the `show_version.textfsm` template is used to parse the output of the `show version` command.

The templates are organized by the operating system type of the network devices. For example, the `cisco_ios` directory contains templates for Cisco IOS devices, and the `cisco_xe` directory contains templates for Cisco IOS XE devices.
# NativeHandler Class

The `NativeHandler` class is responsible for handling native commands on network devices and extracting structured data using TextFSM templates.

## Attributes

- `base_dir (str)`: The base directory for storing TextFSM templates.
- `templates (dict)`: A dictionary to store loaded TextFSM templates.
- `config_data (dict)`: Configuration data containing information about the device.
- `os_type (str)`: The operating system type of the network device.
- `site (str)`: The site information of the network device.
- `templates_dir (str)`: The directory path where TextFSM templates for the specific operating system are stored.

## Methods

### `__init__(self, config_data: dict)`

Initializes a new `NativeHandler` instance with the given configuration data.

### `load_templates(self)`

Loads TextFSM templates from the specified directory and stores them in the templates dictionary.

### `extract_data(self)`

Extracts structured data from the provided configuration data using TextFSM templates. Returns a dictionary containing the extracted data.

## Example Usage

```python
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
```
In the above example, config_data is a dictionary containing information about the network device. The os_type key should match one of the subdirectories in the templates directory (e.g., cisco_ios or cisco_xe). The nodes key should contain the output of the native commands to be parsed.

The extract_data method extracts structured data from the provided configuration data using the TextFSM templates and returns a dictionary containing the extracted data. 