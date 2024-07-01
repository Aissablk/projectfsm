import time
import functools
import requests
import json
from netmiko import (NetmikoAuthenticationException, NetmikoTimeoutException)
import pynetbox
import socket

from .log_config import log_setup

default_logger = log_setup()

# Custom error classes
class CustomError(Exception):
    """Base class for custom errors."""
    pass

class TransientError(CustomError):
    """For errors that can potentially be resolved by retrying."""
    pass

class PersistentError(CustomError):
    """For errors that cannot be resolved by retrying."""
    pass

class ValidationError(CustomError):
    """For validation erros."""
    pass

# Define exceptions that are considered transient and persistent
TRANSIENT_EXCEPTIONS = (
    requests.Timeout,
    requests.ConnectionError,
    requests.TooManyRedirects,
    requests.exceptions.ChunkedEncodingError,
    NetmikoTimeoutException,
    requests.exceptions.ConnectTimeout
)
PERSISTENT_EXCEPTIONS = (
    requests.HTTPError,
    requests.URLRequired,
    requests.exceptions.MissingSchema,
    requests.exceptions.InvalidURL,
    requests.exceptions.InvalidHeader,
    requests.exceptions.ContentDecodingError,
    NetmikoAuthenticationException,
    json.JSONDecodeError,
    KeyError,
    TypeError,
    AttributeError,
    pynetbox.RequestError,
    UnboundLocalError,
    IndexError,
    ValueError,
    ValidationError,
    socket.gaierror
)

def central_error_handler(retries=3, delay=2, logger=default_logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            func_name =func.__name__
            while attempts <= retries:
                try:
                    return func(*args, **kwargs)
                except TRANSIENT_EXCEPTIONS as e:
                    if attempts < retries:
                        if logger:
                            attempted=attempts+1
                            logger.warning(f"{func_name} - Transient Error (Attempt {attempted}/{retries}): {e}")
                        attempts += 1
                        if attempts!=retries:
                            time.sleep(delay)
                    else:
                        if logger:
                            logger.error(f"{func_name} - Transient Error: {e}")
                        else:
                            print(f"{func_name} - Transient Error: {e}")
                        raise TransientError(str(e))  
                except PERSISTENT_EXCEPTIONS as e:
                    if logger:
                        logger.error(f"{func_name} - Persistent Error: {e}")
                    else:
                        print(f"{func_name} - Persistent Error: {e}")
                    raise PersistentError(str(e))  
        return wrapper
    return decorator
