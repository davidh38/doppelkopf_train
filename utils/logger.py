"""
Logger utility for the Doppelkopf AI training program.
"""

import os
import logging
from datetime import datetime

# Global logger instance
_logger = None

def setup_logger(log_dir: str) -> str:
    """
    Set up the logger.
    
    Args:
        log_dir: Directory to save log files
        
    Returns:
        Path to the log file
    """
    global _logger
    
    # Create the log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a unique log file name based on the current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"training_{timestamp}.log")
    
    # Configure the logger
    _logger = logging.getLogger("doppelkopf_ai")
    _logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in _logger.handlers[:]:
        _logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)
    
    info(f"Logger initialized. Logging to {log_file}")
    return log_file

def info(message: str):
    """
    Log an info message.
    
    Args:
        message: The message to log
    """
    if _logger:
        _logger.info(message)

def warning(message: str):
    """
    Log a warning message.
    
    Args:
        message: The message to log
    """
    if _logger:
        _logger.warning(message)

def error(message: str):
    """
    Log an error message.
    
    Args:
        message: The message to log
    """
    if _logger:
        _logger.error(message)

def debug(message: str):
    """
    Log a debug message.
    
    Args:
        message: The message to log
    """
    if _logger:
        _logger.debug(message)
