# Imports
import logging


# Variables
LOG_FILE_PATH = "log_file.log"


# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE_PATH)
formatter = logging.Formatter("%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s | %(funcName)s | %(message)s", ("%d/%m/%Y %H:%M:%S"))

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Functions
def LoggerExamples():
	"""Writes example logs for each log level."""

	logger.debug("This is a debug message.")
	logger.info("This is an info message.")
	logger.warning("This is a warning message.")
	logger.error("This is an error message.")
	logger.critical("This is a critical message.")
