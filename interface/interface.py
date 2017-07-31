import serial
from math import asin, acos, sqrt, pi
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import settings
from settings import logger
import gcode
from serial_list import serial_ports

from .main_window import Ui_MainWindow

__all__ = ['MainWindow']

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.list_serials()
        self.list_configs()
        self.connectUi()

    def connectUi(self):
        logger.info("Connectiong Ui.")
        self.btn_serial_ports_list.clicked.connect(self.list_serials)

    def list_serials(self):
        logger.info("Listing available serial ports.")
        l = serial_ports()
        for i in range(self.serial_ports_list.count()):
            self.serial_ports_list.removeItem(0)
        for i in l:
            logger.info("Found {}".format(i))
            self.serial_ports_list.addItem(i)

    def list_configs(self):
        for _ in range(self.config_list.count()):
            self.config_list.removeItem(0)
        logger.info("Listing available configurations.")
        config_dir = os.path.join(settings.APP_DIR, "configs", "")
        for f in os.listdir(config_dir):
            if f.endswith(".json"):
                logger.info("Found {}".format(f))
                self.config_list.addItem(f[:-5])
        self.config_list.addItem("Nouvelle configuration")
