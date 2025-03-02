import logging
import os
import sys
import time
import socket
import uuid
import inspect

from pythonjsonlogger import jsonlogger

LOG_LEVELS = {
    10: "DEBUG",
    20: "INFO",
    30: "WARN",
    40: "ERROR",
    50: "FATAL"
}

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        # Time and Level
        log_record['level'] = LOG_LEVELS.get(log_record.pop('levelno'), "INFO")
        log_record['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S.', time.gmtime(time.time())) + str(int((time.time() * 1000) % 1000)).zfill(3) + 'Z'

         # Process Information
        log_record['pid'] = os.getpid()
        log_record['service'] = os.environ.get('SERVICE_NAME', 'KrogerMX-gen-ai')  # Service name from environment variable
        log_record['host'] = socket.gethostname()  # Hostname

        # Request/Transaction/Session
        log_record['request_id'] = log_record.get('request_id', str(uuid.uuid4()))  # Request ID, generate if not provided
        log_record['transaction_id'] = log_record.get('transaction_id', str(uuid.uuid4()))  # Transaction ID (if applicable)
        log_record['span_id'] = log_record.get('span_id', str(uuid.uuid4()))  # Transaction ID (if applicable)
        log_record['session_id'] = log_record.get('session_id', 'unknown')  # Session ID (if applicable)
        log_record['user_id'] = log_record.get('user_id', 'unknown')  # User ID (if applicable)
        log_record['user_role'] = log_record.get('user_role', 'unknown')  # User ID (if applicable)

        # Request/Response Data
        log_record['request_payload_size'] = log_record.get('request_payload_size', None)  # Transaction ID (if applicable)
        log_record['response_payload_size'] = log_record.get('response_payload_size', None)  # Transaction ID (if applicable)

        # Event and Message (Message last)
        log_record['event'] = log_record.get('event', 'unknown')  # Transaction ID (if applicable)

        # Location Information
        log_record['filename'] = log_record.get('filename', 'unknown')  # File where logger was called
        log_record['pathname'] = log_record.get('pathname', 'unknown')  # File where logger was called
        log_record['line'] = log_record.pop('lineno', 'unknown')  # Line number
        log_record["funcName"] = self.getFuncName(log_record)

        # Extra Data and Error
        log_record['data'] = log_record.get('data', None) # extra information if needed
        log_record['error'] = log_record.get('error', None) # extra information if needed

        log_record['message'] = log_record.pop('message')

        return super().process_log_record(log_record)
    
    def getFuncName(self, log_record):
        if log_record.get("funcName") != "<module>":
            log_record.get("funcName", "unkown") 
        stack = inspect.stack()
        if len(stack) > 2:  # Ensure there's a caller function
            return stack[2].function
        return "unknown"
        


def get_logger(logger_name='mialogger'):    
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logger = logging.getLogger(logger_name)
    log_level = os.environ.get('LOG_LEVEL', logging.INFO)
    logging.root.setLevel(log_level)
    logger.setLevel(log_level)

    formatter = CustomJsonFormatter(fmt='%(pid)s %(levelno)s %(message)s %(filename)s %(lineno)s %(funcName)s %(pathname)s',)

    # Create a new handler with a filter
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(lambda record: record.name.startswith(logger_name))
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False

    return logger