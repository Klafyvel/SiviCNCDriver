import serial

from PyQt5.QtCore import QObject, pyqtSlot

from settings import logger

__all__ = ["SerialManager"]

class SerialManager(QObject):
    def __init__(self, serial, printer, fake_mode=True):
        super(SerialManager, self).__init__()
        self.serial = serial
        self.printer = printer
        self.fake_mode = fake_mode

    def sendMsg(self, msg):
        if not self.fake_mode and not (self.serial and self.serial.isOpen()):
            self.printer("Error, no serial port.")
            logger.error("Serial manager has no serial opened to send data.")
        elif self.fake_mode:
            self.printer(msg)
            logger.info("Sending {} through fake serial port".format(repr(msg)))
        else:
            logger.info("Sending {} through {}".format(repr(msg),self.serial))
            self.printer(msg)
            self.serial.write(bytes(msg, encoding='utf8'))

    def waitForConfirm(self):
        if self.fake_mode:
            logger.info("Received {}".format(repr("ok")))
            self.printer("ok", "machine")
            return True
        txt = self.serial.readline().decode('ascii').lower()
        if not "ok" in txt:
            logger.error("Machine could not perform task.")
            self.printer(txt, "error")
            return False
        else:
            logger.info("Received {}".format(repr(txt)))
            self.printer(txt, "machine")
            return True

    def step(self, axis, n):
        self.sendMsg("S0 {}{}\n".format(axis,n))
        self.waitForConfirm()

    @pyqtSlot(int)
    def step_y(self, n):
        self.step("Y",n)

    @pyqtSlot(int)
    def step_x(self, n):
        self.step("X",n)

    @pyqtSlot(int)
    def step_z(self, n):
        self.step("Z",n)

    def start_continuous(self, axis, direction="forward"):
        if direction == "forward":
            self.sendMsg("S1 {}\n".format(axis))
        else:
            self.sendMsg("S2 {}\n".format(axis))
        self.waitForConfirm()

    @pyqtSlot()
    def start_continuous_x_forward(self):
        self.start_continuous("X")

    @pyqtSlot()
    def start_continuous_y_forward(self):
        self.start_continuous("Y")

    @pyqtSlot()
    def start_continuous_z_forward(self):
        self.start_continuous("Z")

    @pyqtSlot()
    def start_continuous_x_backward(self):
        self.start_continuous("X", "backward")

    @pyqtSlot()
    def start_continuous_y_backward(self):
        self.start_continuous("Y", "backward")

    @pyqtSlot()
    def start_continuous_z_backward(self):
        self.start_continuous("Z", "backward")

    def stop_continuous(self, axis):
        self.sendMsg("S3 {}\n".format(axis))
        self.waitForConfirm()

    @pyqtSlot()
    def stop_continuous_x(self):
        self.stop_continuous("X")

    @pyqtSlot()
    def stop_continuous_y(self):
        self.stop_continuous("Y")

    @pyqtSlot()
    def stop_continuous_z(self):
        self.stop_continuous("Z")

    @pyqtSlot()
    def set_origin(self):
        self.sendMsg("G92 X000 Y000 Z000\n")
        self.waitForConfirm()

    @pyqtSlot()
    def goto_origin(self):
        self.sendMsg("G28\n")
        self.waitForConfirm()

    def auto_cmd(self, axis, step, move="simple", n=0):
        if move == "simple":
            self.step(axis, step)
        else:
            for _ in range(n):
                self.step(axis, step)
                self.step(axis,-step)
