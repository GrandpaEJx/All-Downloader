"""
Logging configuration for YTDL application
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str = 'ytdl', level: int = logging.INFO) -> logging.Logger:
    """Setup and configure logger for the application"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    try:
        log_dir = Path.home() / '.ytdl' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / 'ytdl.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def get_logger(name: str = 'ytdl') -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)
