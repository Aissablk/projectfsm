# FieldValidator Module

## Overview

The `FieldValidator` module is designed to validate a set of data fields against a predefined configuration. It ensures that each field in the given data meets the criteria specified in the configuration, such as type, length, mandatory status, and allowed values. The module is versatile and can be used to validate various types of fields, including strings and IP addresses.

## Configuration

The module relies on a JSON configuration file (`config.json`) to define the validation rules for each field. This file must specify the field name, data type, mandatory status, maximum length (for strings), and any specific patterns or allowed values.

Example of `config.json` structure:

```json
{
    "fields": {
        "Field_Name": {
            "type": "string", // or "ip_address"
            "mandatory": true, // or false
            "maxLength": 50, // for strings
            "pattern": "regex_pattern", // for ip_address
            "allowedValues": ["value1", "value2"] // for strings
        },
        // ... more fields ...
    }
}
```

## Usage

1. Import the `FieldValidator` class.
2. Create an instance of `FieldValidator` .
3. Call the `validate` method with the data to be validated.

Example:

```python
from field_validator import FieldValidator
from error_handling import PersistentError


# Create a FieldValidator instance
validator = FieldValidator(config)

# Data to be validated
data = {
    "Field_Name": "value",
    // ... other fields ...
}

# Validate data
try:
    result = validator.validate(data)
    if result:
        print("Validation successful")
except PersistentError as e:
    print(f"Validation error: {e}")
```

## Customization

- The validation logic can be extended or modified by editing the `_validate_string` and `_validate_ip_address` methods in the `FieldValidator` class.
- Additional field types can be added by implementing corresponding validation methods and updating the `validate` method.

## Error Handling

Validation errors are managed through the `ValidationError` exception. When a validation fails, `ValidationError` is raised with details about the specific field and the nature of the error.

The `central_error_handler` decorator can be used to handle these exceptions in a centralized manner, providing a uniform response format or logging mechanism.
