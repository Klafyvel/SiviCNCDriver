import os
import sys
import logging
from pathlib import Path
import shutil
 
from logging.handlers import RotatingFileHandler


APP_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

TRANSLATE_DIR = os.path.join(APP_DIR, "ui", "translate")

if DEBUG:
    DATA_DIR = APP_DIR
else:
    DATA_DIR = os.path.join(str(Path.home()), "SiviCNCDriver", "")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

if DEBUG:
    CONFIG_DIR = os.path.join(APP_DIR, "configs", "")
else:
    CONFIG_DIR = os.path.join(DATA_DIR, "configs", "")
    if not os.path.exists(CONFIG_DIR):
        shutil.copytree(os.path.join(APP_DIR, "configs", ""), CONFIG_DIR)

if DEBUG:
    FILE_DIR = os.path.join(APP_DIR, 'gcodes', '')
else:
    FILE_DIR = str(Path.home())

## Logger stuff
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# File log

file_handler = RotatingFileHandler(os.path.join(DATA_DIR, 'log.txt'), 'a', 1000000, 1)


if DEBUG:
    file_handler.setLevel(logging.DEBUG)
else:
    file_handler.setLevel(logging.INFO)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if DEBUG:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
