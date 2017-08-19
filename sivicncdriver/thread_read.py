import serial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from sivicncdriver import settings
from sivicncdriver.settings import logger


class ReadThread(QThread):
    """
    A thread to read the serial link.
    """

    read = pyqtSignal()

    def __init__(self):
        """
        The __init__ method.
        """
        QThread.__init__(self)
        self.user_stop = False
        self.read_allowed = True

    def __del__(self):
        self.wait()

    @pyqtSlot(bool)
    def set_read_allowed(self, st):
        """
        Allows or not the thread to read.

        :param st: Is it allowed ?
        """
        logger.debug("Set reading allowed to {}".format(st))
        self.read_allowed = st

    @pyqtSlot()
    def stop(self):
        """
        A simple slot to tell the thread to stop.
        """
        self.user_stop = True

    def run(self):
        """
        Runs the thread.

        The commands are sent using the serial manager. If an error occurs or if
        the thread is stopped by the user, then it quits.
        """
        while not self.user_stop:
            if self.read_allowed:
                self.read.emit()
            self.msleep(50)
