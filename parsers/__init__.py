from error_handling import PersistentError, central_error_handler
from .parser_factory import ParserFactory


class Parser:
    def __init__(self, data, logger):
        self.data = data
        self.logger = logger
    
    @central_error_handler()
    def parse(self):
        results = []
        for data_dict in self.data:
            os_type = data_dict.get("os_type")            
            try:
                parser_instance = ParserFactory.get_parser(os_type = os_type)
                parsed_data = parser_instance.parse(data_dict)
                results += parsed_data or []
                self.logger.info(f"Data Processed Successfully! for Device: {data_dict.get('device_name')} in Site: {data_dict.get('site') or 'no site available'}")
            except PersistentError as e:
                self.logger.error(f"Data Processing Faild! for Device: {data_dict.get('device_name')} in Site: {data_dict.get('site')}, error : {e}")
                continue
        return results

