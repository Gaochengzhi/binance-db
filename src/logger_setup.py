import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(config):
    """
    Setup logging configuration based on config settings
    """
    # Create logs directory if it doesn't exist
    log_dir = config.get('log_directory', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Get logging configuration
    logging_config = config.get('logging', {})
    log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
    console_output = logging_config.get('console_output', True)
    file_output = logging_config.get('file_output', True)
    max_file_size = logging_config.get('max_log_file_size', '10MB')
    backup_count = logging_config.get('backup_count', 5)
    
    # Convert max_file_size to bytes
    size_multiplier = {'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
    size_unit = max_file_size[-2:].upper()
    size_value = int(max_file_size[:-2])
    max_bytes = size_value * size_multiplier.get(size_unit, 1024*1024)
    
    # Create logger
    logger = logging.getLogger('binance_downloader')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Main log file handler with rotation
    if file_output:
        log_filename = os.path.join(log_dir, f'binance_downloader_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Separate error log handler
        error_log_filename = os.path.join(log_dir, f'binance_downloader_errors_{datetime.now().strftime("%Y%m%d")}.log')
        error_handler = RotatingFileHandler(
            error_log_filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger

def get_logger():
    """
    Get the configured logger instance
    """
    return logging.getLogger('binance_downloader')