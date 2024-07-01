
# Transformer Module

This module contains the `transformer.py` script, which is responsible for transforming data into a format suitable for use with the Netbox API.

The `Transformer` class in the `transformer.py` script provides several static methods for data transformation:

- `sanitize_slug(slug)`: Generates a slug for a resource from a name by replacing non-alphanumeric characters with underscores and converting all characters to lowercase.
- `sanitize_collector_device_type(type)`: Converts the device type to uppercase.
- `return_host(host)`: Returns the IP address for the given domain name or just the IP address if given an IP address. This method is used for IOS and IOSXE devices, to resolve the domain name of a device to an IP address, to be used later to get the associated interface with it.
- `return_standard(interface_value)`: Returns the interface standard based on interface name or speed. The interface standard can be '100base-tx', '10gbase-t', etc., or 'other' if no match.

## Usage

To use the `transformer.py` script, import the `Transformer` class and use its static methods:

```python
from transformer import Transformer

slug = "Example Slug"
sanitized_slug = Transformer.sanitize_slug(slug)

type = "device type"
sanitized_type = Transformer.sanitize_collector_device_type(type)

domain = "example.com"
ip = Transformer.return_host(domain)



interface_value = "GigabitEthernet"
standard = Transformer.return_standard(interface_value)
```

## Dependencies

The `transformer.py` script depends on the `re` and `socket` modules from the Python Standard Library, and the `central_error_handler` from the `error_handling` module.
