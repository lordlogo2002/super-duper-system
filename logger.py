import logging
import colorlog
import os

class glob:
    """store global loggers in here"""

# Get the filename of the calling script (assuming this custom_logger.py is imported)
calling_filename = os.path.basename(os.path.abspath(os.path.dirname(__file__)))

# Create a file handler for each logger to save log messages in separate files
def create_file_handler(log_file, log_formatter):
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    return file_handler

# Function to create a new logger with specified log level and log file
def create_logger(name, log_file, log_level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Add colored output to the logger
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s - %(funcName)s()] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red"
        }
    )

    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(color_formatter)

    # Check if the logger is being created in global scope
    # If it is, customize the log formatter for global logging
    if "<module>" in logger.findCaller():
        global_log_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [{calling_filename}:{lineno} - {calling_filename}/global] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler = create_file_handler(log_file, global_log_formatter)
    else:
        file_handler = create_file_handler(log_file, color_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    logger1 = create_logger("Logger1", "logger1.log", log_level=logging.INFO)
    logger2 = create_logger("Logger2", "logger2.log", log_level=logging.DEBUG)

    logger1.info("This is an info message")
    logger2.debug("This is a debug message")
    logger1.warning("This is a warning message")
    logger2.error("This is an error message")
    logger1.critical("This is a critical message")
