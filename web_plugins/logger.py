import logging
import sys

logger_handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger("web_plugins.logger")
logger.addHandler(logger_handler)
logger.setLevel(logging.DEBUG)

#debug
#info
#warning
#error
#critial
