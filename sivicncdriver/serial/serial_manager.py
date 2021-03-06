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
    """
    A class to manage the serial port.

    It will try to send what it receive and send via the send_print signal. When
    it receive a 'ok' from the serial it will send the send_confirm signal.
    """
    send_print = pyqtSignal(str, str)
    send_confirm = pyqtSignal(bool)
    serial_fatal_error = pyqtSignal()

    def __init__(self, serial, fake_mode=False):
        """
        The __init__ method.

        :param serial: The serial port.
        :param fake_mode: if True, then the manager will not use the serial
            object, and will always respond 'ok'.
        """
        super(SerialManager, self).__init__()
        self.serial = serial
        self.fake_mode = fake_mode
        self.is_open = self.serial.isOpen()
        self.something_sent = False

    def open(self, baudrate, serial_port, timeout):
        """
        Opens the serial port with the given parameters.

        :param baudrate: The baudrate.
        :param serial_port: The port to be used.
        :param timeout: Timeout for reading and writing.
        """
        logger.info("Opening {} with baudrate {}, timeout {}".format(
            repr(serial_port), baudrate, timeout))
        self.send_print.emit("Opening {} with baudrate {}, timeout {}".format(
            repr(serial_port), baudrate, timeout), "info")
        self.serial.port = serial_port
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout
        self.serial.write_timeout = timeout
        try:
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
        """
        Closes the serial port.
        """
        logger.info("Closing serial port.")
        self.send_print.emit("Closing serial port.", "info")
        self.is_open = False
        self.serial.close()

    def sendMsg(self, msg):
        """
        Sends a message using the serial port if fake_mode is False.

        :param msg: The message to be sent.
        :returns: True if no error occurred, else False.
        """
        if not self.fake_mode and not (self.serial and self.serial.isOpen()):
            self.send_print.emit("Error, no serial port to write.", "error")
            logger.error("Serial manager has no serial opened to send data.")
            return False
        elif self.fake_mode:
            self.send_print.emit(msg, "operator")
            logger.info(
                "Sending {} through fake serial port".format(repr(msg)))
            self.something_sent = True
            return True
        else:
            logger.info("Sending {} through {}".format(repr(msg), self.serial))
            self.send_print.emit(msg, "operator")
            if msg[-1] != '\n':
                msg += '\n'
            try:
                self.serial.write(bytes(msg, encoding='utf8'))
            except serial.serialutil.SerialException as e:
                logger.error("Serial error : {}".format(e))
                self.send_print.emit("Serial error while writing.", "error")
            except OSError as e:
                logger.error("Serial error : {}".format(e))
                self.send_print.emit("Serial error while writing.", "error")
                self.serial_fatal_error.emit()
            return True

    @pyqtSlot()
    def readMsg(self):
        """
        Reads a line from the serial port. And emit the send_print or
        send_confirm signals if necessary.
        """
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
        try:
            waiting  = self.serial.in_waiting
        except OSError as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")
            self.serial_fatal_error.emit()
            return
        if not waiting:
            return
        txt = ""
        try:
            txt = self.serial.readline().decode('ascii')
        except serial.serialutil.SerialException as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")
        except UnicodeDecodeError as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")
        except OSError as e:
            logger.error("Serial error : {}".format(e))
            self.send_print.emit("Serial error while reading.", "error")
            self.serial_fatal_error.emit()

        if txt:
            if "error" in txt.lower():
                self.send_print.emit(txt, "error")
            else:
                self.send_print.emit("m> {}".format(txt), "machine")
            self.send_confirm.emit("ok" in txt.lower())
