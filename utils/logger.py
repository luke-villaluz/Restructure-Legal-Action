import logging
import sys
from colorama import init, Fore, Style
from config.settings import LOG_LEVEL

# Initialize colorama for cross-platform colored output
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        # Add color to the log level
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger():
    """Set up the logger with colored output and proper formatting."""
    logger = logging.getLogger('legal_analyzer')
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def log_progress(current, total, company_name=""):
    """Log progress with percentage and company name."""
    percentage = (current / total) * 100
    logger = logging.getLogger('legal_analyzer')
    
    if company_name:
        logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - Processing: {company_name}")
    else:
        logger.info(f"Progress: {current}/{total} ({percentage:.1f}%)")

def log_error(error_msg, company_name=""):
    """Log errors with company context."""
    logger = logging.getLogger('legal_analyzer')
    
    if company_name:
        logger.error(f"Error processing {company_name}: {error_msg}")
    else:
        logger.error(f"Error: {error_msg}")

# Create the main logger instance
logger = setup_logger()
