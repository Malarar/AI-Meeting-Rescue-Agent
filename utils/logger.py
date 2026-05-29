"""
Logging utility for AI Meeting Rescue Agent
Configures structured logging for the application
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from config import Config


def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    Setup and configure a logger with both file and console handlers
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Optional custom log file path
        level: Optional custom log level
        
    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or Config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    # Console formatter (human-readable)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File formatter (JSON for structured logging)
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    log_file_path = log_file or Config.LOG_FILE
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return setup_logger(name)

# Made with Bob
