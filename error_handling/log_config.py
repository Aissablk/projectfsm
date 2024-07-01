import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os
def log_setup(name='global_logger', format='%(asctime)s - %(levelname)s - %(message)s'):
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Check if the format has changed
    if not hasattr(logger, 'log_format') or logger.log_format != format:
        # Update the format attribute
        logger.log_format = format

        formatter = logging.Formatter(format)
        
        # Get current date to create a log file for the day
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_dir = 'logs'
        os.makedirs(log_dir,exist_ok=True)
        log_filename = f"{log_dir}/{current_date}_logs.log"

        # Create a TimedRotatingFileHandler to rotate logs based on day
        file_handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1) 
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add new handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
