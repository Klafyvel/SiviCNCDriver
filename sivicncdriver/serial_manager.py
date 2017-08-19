"""
The serial_manager module
=========================

Provides a class to handle the CNC machine through a serial object.
"""

import serial
import time

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from sivicncdriver.settings import logger

__all__ = ["SerialManager"]

class SerialManager(QObject):
    send_print = pyqtSignal(str, str)
    send_confirm = pyqtSignal(bool)

    def __init__(self, serial, fake_mode=False):
        super(SerialManager, self).__init__()
        self.serial = serial
        self.fake_mode = fake_mode
        self.is_open = self.serial.isOpen()
        self.something_sent = False

    def open(self, baudrate, serial_port):
        logger.info("Opening {} with baudrate {}".format(repr(serial_port), baudrate))
        self.send_print.emit("Opening {} with baudrate {}".format(repr(serial_port), baudrate), "info")
        self.serial.port = serial_port
        self.serial.baudrate = baudrate
        self.serial.timeout = None
        try :
            self.serial.open()
            self.is_open = True
        except serial.serialutil.SerialException:
            self.is_open = False
            logger.error("Could not open serial port.")
            self.send_print.emit("Could not open serial port.", "error")
            return False
        logger.debug(self.serial.timeout)
        return True

    def close(self):
        logger.info("Closing serial port.")
        self.send_print.emit("Closing serial port.", "info")
        self.is_open = False
        self.serial.close()

    def sendMsg(self, msg):
        if not self.fake_mode and not (self.serial and self.serial.isOpen()):
            self.send_print.emit("Error, no serial port to write.", "error")
            logger.error("Serial manager has no serial opened to send data.")
        elif self.fake_mode:
            self.send_print.emit(msg, "operator")
            logger.info("Sending {} through fake serial port".format(repr(msg)))
            self.something_sent = True
        else:
            logger.info("Sending {} through {}".format(repr(msg),self.serial))
            self.send_print.emit(msg, "operator")
            if msg[-1] != '\n':
                msg += '\n'
            self.serial.write(bytes(msg, encoding='utf8'))


    @pyqtSlot()
    def readMsg(self):
        if self.fake_mode:
            if self.something_sent:
                logger.info("Received {}".format(repr("ok")))
                self.send_print.emit("ok", "machine")
                self.something_sent = False
                self.send_confirm.emit(True)
            return
        elif not (self.serial and self.serial.isOpen()):
            self.send_print.emit("Error, no serial port to read.", "error")
            logger.error("Serial manager has no serial opened to read data.")
            self.send_confirm.emit(False)
            return
        elif not self.serial.in_waiting:
            return
        logger.debug("Reading...");
        txt = ""
        try:
            txt = self.serial.readline().decode('ascii')
        except serial.serialutil.SerialException as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")
        except UnicodeDecodeError as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")

        if txt:
                if "error" in txt.lower():
                    self.send_print.emit(txt, "error")
                else:
                    self.send_print.emit("m> {}".format(txt), "machine")
                self.send_confirm.emit("ok" in txt.lower())
