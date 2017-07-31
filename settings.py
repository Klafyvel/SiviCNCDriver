import os
import sys
import logging
 
from logging.handlers import RotatingFileHandler


APP_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False


## Logger stuff
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# File log
file_handler = RotatingFileHandler(os.path.join(APP_DIR, 'log.txt'), 'a', 1000000, 1)

if DEBUG:
    file_handler.setLevel(logging.DEBUG)
else:
    file_handler.setLevel(logging.INFO)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


