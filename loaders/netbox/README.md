# NetBox API Integration

This Python module provides a foundation for integrating with the NetBox API to create and manage resources. It includes three main components:

1. `NetBoxAPI` class in `session.py`: Initializes the NetBoxAPI with the provided NetBox URL, API token, and HTTP session configuration.

2. `Resource` class in `resource.py`: Provides methods for creating and updating resources in the NetBox instance.

3. `netbox.py` Script: Orchestrates the creation and update of resources in the NetBox instance using the `NetBoxAPI` and `Resource` classes.

## Prerequisites

Before using this module, ensure that you have the following dependencies installed:

- The `pynetbox` library (`pip install pynetbox`)
- Custom dependencies for logging and error handling

## Project Structure
```
loader
├── README.md
├── init.py
└── netbox
├── init.py
├── netbox.py
├── templates
│ ├── device_template
│ ├── interface_template
│ ├── ip_template
│ ├── manufacturer_template
│ ├── os_type_custom_field_template
│ ├── platform_template
│ ├── role_template
│ ├── site_template
│ ├── type_template
│ ├── location_template
│ └── region_template
└── utils
├── init.py
├── resource.py
└── session.py
```
## Classes and Scripts

### `NetBoxAPI` Class in `session.py`

#### `__init__(self, netbox_url, netbox_token)`

- **Description**: Initializes the `NetBoxAPI` class with the provided NetBox URL, API token, and HTTP session configuration.

- **Parameters**:
  - `netbox_url` (str): The URL of the NetBox instance.
  - `netbox_token` (str): The API token for authentication.
  - `http_session` (bool): Enables or disables HTTPS certificate validation for requests made using this Pynetbox API instance.

### `Resource` Class in `resource.py`

#### `__init__(self, netbox_session, resource_data)`

- **Description**: Initializes the `Resource` class with the provided NetBox session and resource data. It is used as a base class for creating specific types of resources.

- **Parameters**:
  - `netbox_session` (pynetbox.api): An instance of the pynetbox API class, representing the NetBox session.
  - `resource_data` (dict): The resource data used for creating the resource.

#### `create(self, endpoint1, endpoint2, logger)`

- **Description**: Creates a resource in the NetBox instance using the Factory Method Pattern. It dynamically constructs the endpoint and sends the resource data for creation.

- **Parameters**:
  - `endpoint1` (str): The first part of the endpoint (e.g., 'dcim', 'ipam').
  - `endpoint2` (str): The second part of the endpoint (e.g., 'devices', 'interfaces').
  - `logger` (Logger): An instance of the logger class used for logging information and errors related to resource creation.

- **Returns**:
  - `dict or None`: If the resource is successfully created, this method returns a dictionary containing information about the created resource. If an error occurs during creation, it returns `None`.

#### `update(self, endpoint1, endpoint2, logger)`

- **Description**: Updates a resource in the NetBox instance using the Factory Method Pattern. It dynamically constructs the endpoint and sends the updated resource data.

- **Parameters**:
  - `endpoint1` (str): The first part of the endpoint (e.g., 'dcim', 'ipam').
  - `endpoint2` (str): The second part of the endpoint (e.g., 'devices', 'interfaces').
  - `logger` (Logger): An instance of the logger class used for logging information and errors related to resource update.

- **Returns**:
  - `dict or None`: If the resource is successfully updated, this method returns a dictionary containing information about the updated resource. If an error occurs during update, it returns `None`.

### `netbox.py` Script

- **Description**: Orchestrates the creation and update of resources in the NetBox instance using the `NetBoxAPI` and `Resource` classes. It utilizes templates from the `templates` folder based on the action (create or update).

- **Usage**: The script reads data, determines the appropriate resource templates from the `templates` folder (either `create` or `update`), fills them with data, and then creates or updates resources accordingly.

- **Templates**:
  - The templates are located in the `/templates/` folder in the `loaders` directory.
  - The script dynamically loads the appropriate template based on the action (`create` or `update`).

