import serial
from math import asin, acos, sqrt, pi
import os
import json

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

        self.serial_manager = SerialManager(
            serial.Serial(timeout=0), self.print)

        s = """Welcome to SiviCNCDriver, by Klafyvel from sivigik.com"""
        self.print(s, msg_type="info")

        self.connectUi()
        self.update_config(self.config_list.currentIndex())

    def connectUi(self):
        logger.debug("Connecting Ui.")
        self.btn_serial_ports_list.clicked.connect(self.list_serials)

        self.btn_y_plus.pressed.connect(
            self.serial_manager.start_continuous_y_forward)
        self.btn_y_minus.pressed.connect(
            self.serial_manager.start_continuous_y_backward)
        self.btn_x_plus.pressed.connect(
            self.serial_manager.start_continuous_x_forward)
        self.btn_x_minus.pressed.connect(
            self.serial_manager.start_continuous_x_backward)
        self.btn_z_plus.pressed.connect(
            self.serial_manager.start_continuous_z_forward)
        self.btn_z_minus.pressed.connect(
            self.serial_manager.start_continuous_z_backward)

        self.btn_y_plus.released.connect(self.serial_manager.stop_continuous_y)
        self.btn_y_minus.released.connect(
            self.serial_manager.stop_continuous_y)
        self.btn_x_plus.released.connect(self.serial_manager.stop_continuous_x)
        self.btn_x_minus.released.connect(
            self.serial_manager.stop_continuous_x)
        self.btn_z_plus.released.connect(self.serial_manager.stop_continuous_z)
        self.btn_z_minus.released.connect(
            self.serial_manager.stop_continuous_z)

        self.btn_set_origin.clicked.connect(self.serial_manager.set_origin)
        self.btn_go_to_zero.clicked.connect(self.serial_manager.goto_origin)

        self.auto_cmd_type.currentIndexChanged.connect(
            self.manage_auto_cmd_number)
        self.btn_run_auto_cmd.clicked.connect(self.auto_cmd)
        self.manage_auto_cmd_number(self.auto_cmd_type.currentIndex())

        self.chk_fake_serial.stateChanged.connect(
            self.manage_emulate_serial_port)
        self.btn_send_current_file.clicked.connect(self.send_file)
        self.btn_command.clicked.connect(self.send_cmd)

        self.config_list.currentIndexChanged.connect(self.update_config)
        self.btn_save_config.clicked.connect(self.save_config)
        self.btn_save_config_as.clicked.connect(self.save_config_as)
        self.btn_send_config.clicked.connect(self.send_config)

        self.btn_connect.clicked.connect(self.manage_connection)

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

    def reset_config(self):
        self.drive_x.setCurrentIndex(0)
        self.drive_y.setCurrentIndex(0)
        self.drive_z.setCurrentIndex(0)

        self.ratio_x.setValue(1)
        self.ratio_y.setValue(1)
        self.ratio_z.setValue(1)

        self.play_x.setValue(0)
        self.play_y.setValue(0)
        self.play_z.setValue(0)

        self.reverse_x.setChecked(False)
        self.reverse_y.setChecked(False)
        self.reverse_z.setChecked(False)

        logger.info("Reset config.")

    def config_as_dict(self):
        return {
            "x_drive" : self.drive_x.currentIndex(),
            "x_ratio" : self.ratio_x.value(),
            "x_play" : self.play_x.value(),
            "x_reverse" : bool(self.reverse_x.checkState()),
            "y_drive" : self.drive_y.currentIndex(),
            "y_ratio" : self.ratio_y.value(),
            "y_play" : self.play_y.value(),
            "y_reverse" : bool(self.reverse_y.checkState()),
            "z_drive" : self.drive_z.currentIndex(),
            "z_ratio" : self.ratio_z.value(),
            "z_play" : self.play_z.value(),
            "z_reverse" : bool(self.reverse_z.checkState()),
        }

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

    @pyqtSlot()
    def send_cmd(self):
        gcode = self.command_edit.text()
        self.serial_manager.sendMsg(gcode)
        self.serial_manager.waitForConfirm()

    @pyqtSlot(int)
    def update_config(self, i):
        nb_config = self.config_list.count()
        if i==nb_config-1:
            self.reset_config()
        else:
            file = self.config_list.currentText() + ".json"
            file = os.path.join(settings.APP_DIR, "configs", file)
            logger.info("Loading config {}".format(file))
            config = {}
            with open(file) as f:
                config = json.load(f)
            self.drive_x.setCurrentIndex(config.get("x_drive", 0))
            self.drive_y.setCurrentIndex(config.get("y_drive", 0))
            self.drive_z.setCurrentIndex(config.get("z_drive", 0))

            self.ratio_x.setValue(config.get("x_ratio", 1))
            self.ratio_y.setValue(config.get("y_ratio", 1))
            self.ratio_z.setValue(config.get("z_ratio", 1))

            self.play_x.setValue(config.get("x_play", 0))
            self.play_y.setValue(config.get("y_play", 0))
            self.play_z.setValue(config.get("z_play", 0))

            self.reverse_x.setChecked(config.get("x_reverse", False))
            self.reverse_y.setChecked(config.get("y_reverse", False))
            self.reverse_z.setChecked(config.get("z_reverse", False))

    @pyqtSlot()
    def save_config(self, filename=None):
        logger.info("Saving configuration.")
        logger.debug("Filename given : {}".format(filename))
        current_config = self.config_list.currentIndex()
        nb_config = self.config_list.count()
        if current_config == nb_config-1 and not filename:
            self.save_config_as()
        else:
            if not filename:
                file = self.config_list.currentText() + ".json"
                file = os.path.join(settings.APP_DIR, "configs", file)
            else:
                file = filename
            config = self.config_as_dict()
            with open(file, "w") as f:
                json.dump(config, f)

    @pyqtSlot()
    def save_config_as(self):
        directory = os.path.join(settings.APP_DIR, "configs", "")
        f = QFileDialog.getSaveFileName(
            self, "Sélectionner un fichier",
            directory=directory,
            filter='JSON files (*.json)\nAll files (*)')[0]
        if f is not '':
            if not f.endswith(".json"):
                f = f + ".json"
            logger.info("Saving configuration as {}".format(f))
            self.save_config(f)
            self.list_configs()
            self.update_config(self.config_list.currentIndex())

    @pyqtSlot()
    def send_config(self):
        self.save_config()
        self.serial_manager.send_config(self.config_as_dict())

    @pyqtSlot()
    def manage_connection(self):
        if self.serial_manager.is_open :
            self.baudrate.setEnabled(True)
            self.serial_ports_list.setEnabled(True)
            self.btn_serial_ports_list.setEnabled(True)
            self.btn_connect.setText("Connecter")
            self.serial_manager.close()
        else :
            port = self.serial_ports_list.currentText()
            baudrate = int(self.baudrate.currentText())
            if self.serial_manager.open(baudrate, port):
                self.baudrate.setEnabled(False)
                self.serial_ports_list.setEnabled(False)
                self.btn_serial_ports_list.setEnabled(False)
                self.btn_connect.setText("Déconnecter")