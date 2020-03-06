import sys
import logging

#logging.basicConfig(level=logging.DEBUG)
domain = 'ki_auto'

def get_logger(name):
    return logging.getLogger(domain+'.'+name) if name else logging.getLogger(domain)

def set_domain(name):
    global domain
    domain = name

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    if sys.stderr.isatty():
       grey = "\x1b[38;21m"
       yellow = "\x1b[33;21m"
       red = "\x1b[31;21m"
       bold_red = "\x1b[31;1m"
       cyan = "\x1b[36;1m"
       reset = "\x1b[0m"
    else:
       grey = ""
       yellow = ""
       red = ""
       bold_red = ""
       cyan = ""
       reset = ""
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(levelname)s:%(message)s (%(name)s - %(filename)s:%(lineno)d)"
    format_simple = "%(levelname)s:%(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format_simple + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
