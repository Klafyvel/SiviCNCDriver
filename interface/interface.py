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
from serial_manager import SerialManager

from .main_window import Ui_MainWindow

__all__ = ['MainWindow']

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.list_serials()
        self.list_configs()
        self.set_serial_mode("manual")

        self.serial_manager = SerialManager(serial.Serial(timeout=0), self.print)

        s = """Welcome to SiviCNCDriver, by Klafyvel from sivigik.com"""
        self.print(s, msg_type="info")

        self.connectUi()

    def connectUi(self):
        logger.debug("Connecting Ui.")
        self.btn_serial_ports_list.clicked.connect(self.list_serials)

        self.btn_y_plus.pressed.connect(self.serial_manager.start_continuous_y_forward)
        self.btn_y_minus.pressed.connect(self.serial_manager.start_continuous_y_backward)
        self.btn_x_plus.pressed.connect(self.serial_manager.start_continuous_x_forward)
        self.btn_x_minus.pressed.connect(self.serial_manager.start_continuous_x_backward)
        self.btn_z_plus.pressed.connect(self.serial_manager.start_continuous_z_forward)
        self.btn_z_minus.pressed.connect(self.serial_manager.start_continuous_z_backward)

        self.btn_y_plus.released.connect(self.serial_manager.stop_continuous_y)
        self.btn_y_minus.released.connect(self.serial_manager.stop_continuous_y)
        self.btn_x_plus.released.connect(self.serial_manager.stop_continuous_x)
        self.btn_x_minus.released.connect(self.serial_manager.stop_continuous_x)
        self.btn_z_plus.released.connect(self.serial_manager.stop_continuous_z)
        self.btn_z_minus.released.connect(self.serial_manager.stop_continuous_z)

        self.btn_set_origin.clicked.connect(self.serial_manager.set_origin)
        self.btn_go_to_zero.clicked.connect(self.serial_manager.goto_origin)

        self.auto_cmd_type.currentIndexChanged.connect(self.manage_auto_cmd_number)
        self.btn_run_auto_cmd.clicked.connect(self.auto_cmd)
        self.manage_auto_cmd_number(self.auto_cmd_type.currentIndex())

        self.chk_fake_serial.stateChanged.connect(self.manage_emulate_serial_port)


    def list_serials(self):
        logger.debug("Listing available serial ports.")
        l = serial_ports()
        for i in range(self.serial_ports_list.count()):
            self.serial_ports_list.removeItem(0)
        for i in l:
            logger.info("Found {}".format(i))
            self.serial_ports_list.addItem(i)

    def list_configs(self):
        for _ in range(self.config_list.count()):
            self.config_list.removeItem(0)
        logger.debug("Listing available configurations.")
        config_dir = os.path.join(settings.APP_DIR, "configs", "")
        for f in os.listdir(config_dir):
            if f.endswith(".json"):
                logger.debug("Found {}".format(f))
                self.config_list.addItem(f[:-5])
        self.config_list.addItem("Nouvelle configuration")

    def set_serial_mode(self, mode):
        """
        Change serial mode.
        mode can be "manual" or "file"
        """
        if mode == "manual":
            logger.debug("Setting manual mode.")
            self.btn_set_origin.setEnabled(True)
            self.grp_cmd.setEnabled(True)
            self.grp_auto.setEnabled(True)
            # self.btn_y_plus.pressed.connect()
        elif mode == "file":
            logger.debug("Setting file mode.")
            self.btn_set_origin.setEnabled(False)
            self.grp_cmd.setEnabled(False)
            self.grp_auto.setEnabled(False)

    def print(self, txt, msg_type="operator"):
        msg = "{}"
        if msg_type == "operator":
            msg = "\n<br /><span style='color:orange;'> <strong>&gt;&gt;&gt;</strong> {}</span>"
        elif msg_type == "machine":
            msg = "\n<br /><span style='color:yellow;'>{}</span>"
        elif msg_type == "error":
            msg = "\n<br /><span style='color:red;'><strong>{}</strong></span>"
        elif msg_type == "info":
            msg = "\n<br /><span style='color:DarkOrange;'><strong>{}</strong></span>"
        self.serial_monitor.moveCursor(QTextCursor.End)
        self.serial_monitor.insertHtml(msg.format(txt))
        self.serial_monitor.moveCursor(QTextCursor.End)

    # Slots
    @pyqtSlot(int)
    def manage_auto_cmd_number(self, n):
        self.auto_cmd_number.setValue(1)
        self.auto_cmd_number.setEnabled(n != 0)

    @pyqtSlot()
    def auto_cmd(self):
        axis = self.auto_cmd_axis.currentText()
        n = self.auto_cmd_number.value()
        step = self.auto_cmd_step.value()
        if self.auto_cmd_type.currentIndex() == 0:
            self.serial_manager.auto_cmd(axis, step)
        else:
            self.serial_manager.auto_cmd(axis, step, "complex", n)

    @pyqtSlot(int)
    def manage_emulate_serial_port(self, s):
        st = bool(s)
        self.serial_manager.fake_mode = st
        self.baudrate.setEnabled(not st)
        self.serial_ports_list.setEnabled(not st)
        self.btn_serial_ports_list.setEnabled(not st)
        self.btn_connect.setEnabled(not st)
        if st:
            self.tabWidget.setCurrentIndex(1)
            self.print("Emulating serial port.", "info")
        else:
            self.print("Exiting serial port emulation.", "info")

    @pyqtSlot()
    def send_file(self):
        gcode = self.code_edit.toPlainText().split('\n')
        for l in gcode:
            self.serial_manager.sendMsg(l)
            if not self.serial_manager.waitForConfirm():
                break