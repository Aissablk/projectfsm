import re
from error_handling import central_error_handler, ValidationError

class FieldValidator:
    def __init__(self, config='config.json'):
        self.config = config
        
    @central_error_handler()
    def validate(self, data):
        for field, details in self.config.get("fields", {}).items():
            value = data.get(field)
            validation_type = details.get("type", "")
            
            if validation_type == "string":
                is_valid, message = self._validate_string(value, details)
            elif validation_type == "ip_address":
                is_valid, message = self._validate_ip_address(value, details)
            else:
                raise ValidationError(f"Validation type {validation_type} not recognized")

            if not is_valid:
                raise ValidationError(f"Error in field '{field}': {message}")

        return True

    def _validate_string(self, value, validation_details):
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"

        if "maxLength" in validation_details and len(value) > validation_details["maxLength"]:
            return False, f"String length exceeds {validation_details['maxLength']} characters"

        if "mandatory" in validation_details and validation_details["mandatory"] and not value:
            return False, "Value is mandatory and cannot be empty"

        if "allowedValues" in validation_details and value not in validation_details["allowedValues"]:
            return False, f"Value not among allowed values"

        return True, "Valid"

    def _validate_ip_address(self, value, validation_details):
        if not re.match(validation_details.get("pattern", ""), value):
            return False, f"Value {value} doesn't match the expected IP address format"
        return True, "Valid"