from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from sivicncdriver import settings
from sivicncdriver.settings import logger


class SendThread(QThread):
    """
    A thread to send a list of instructions without blocking the main thread.
    """
    update_progress = pyqtSignal(int)
    read_allowed = pyqtSignal(bool)

    def __init__(self, serial_manager, gcode):
        """
        The __init__ method.

        :param serial_manager: The main window's serial manager
        :param gcode: An iterable of gcode instructions
        :type serial_manager: SerialManager
        :type gcode: iterable
        """
        QThread.__init__(self)
        self.gcode = gcode
        self.serial_manager = serial_manager
        self.user_stop = False
        self.error = False
        self.confirmed = True

    def __del__(self):
        self.wait()

    @pyqtSlot()
    def stop(self):
        """
        A simple slot to tell the thread to stop.
        """
        self.user_stop = True

    @pyqtSlot(bool)
    def confirm(self, st):
        """
        Receive confirmation from the readThread.

        :param st: Everything ok ?
        """
        self.error = st
        self.confirmed = True
        logger.debug("Confirmation.")

    def run(self):
        """
        Runs the thread.

        The commands are sent using the serial manager. If an error occurs or if
        the thread is stopped by the user, then it quits.
        """
        for n, l in enumerate(self.gcode):
            if self.confirmed:
                self.read_allowed.emit(False)
                self.serial_manager.sendMsg(l)
                self.update_progress.emit(n)
                self.confirmed = False
                self.read_allowed.emit(True)
                while not self.confirmed:
                    pass

            if (not self.error) or self.user_stop:
                break