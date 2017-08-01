import serial
from math import asin, acos, sqrt, pi
import os
import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from . import settings
from .settings import logger
from .gcode import parse
from .serial_list import serial_ports
from .serial_manager import SerialManager

from .main_window import Ui_MainWindow

__all__ = ['MainWindow']


class SendFileThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, serial_manager, gcode):
        QThread.__init__(self)
        self.gcode = gcode
        self.serial_manager = serial_manager
        self.user_stop = False

    def __del__(self):
        self.wait()

    @pyqtSlot()
    def stop(self):
        self.user_stop = True

    def run(self):
        for n, l in enumerate(self.gcode):
            self.serial_manager.sendMsg(l)
            self.update_progress.emit(n)
            if not self.serial_manager.waitForConfirm() or self.user_stop:
                break


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.list_serials()
        self.list_configs()

        self.set_serial_mode("manual")

        self.serial_manager = SerialManager(serial.Serial(timeout=0))

        s = """Welcome to SiviCNCDriver, by Klafyvel from sivigik.com"""
        self.print(s, msg_type="info")

        self.sc = QGraphicsScene(self.fileview)
        self.attach_icons()
        self.connectUi()
        self.update_config(self.config_list.currentIndex())

    def attach_icons(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "siviIcon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "load.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_file.setIcon(icon1)

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "reload.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_reload.setIcon(icon2)

        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "writing.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.redraw.setIcon(icon3)

        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "work.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_preprocessor.setIcon(icon4)

        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_save_as.setIcon(icon5)
        self.btn_save_file.setIcon(icon5)

        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "run.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_command.setIcon(icon6)

        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "upload.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_send_current_file.setIcon(icon7)

        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "connect.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_connect.setIcon(icon8)

        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "origin.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_set_origin.setIcon(icon9)

        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "right.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_x_plus.setIcon(icon10)

        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "up.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_y_plus.setIcon(icon11)

        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "down.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_y_minus.setIcon(icon12)

        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "left.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_x_minus.setIcon(icon13)

        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "up.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_z_plus.setIcon(icon14)

        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(os.path.join(settings.RC_DIR, "down.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_z_minus.setIcon(icon15)

        self.btn_go_to_zero.setIcon(icon9)
        self.btn_run_auto_cmd.setIcon(icon6)
        self.btn_send_config.setIcon(icon8)
        self.btn_save_config.setIcon(icon5)
        self.btn_save_config_as.setIcon(icon5)


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

        self.btn_file.clicked.connect(self.choose_file)
        self.btn_reload.clicked.connect(self.load_file)
        self.btn_save_file.clicked.connect(self.save_file)
        self.btn_save_as.clicked.connect(self.save_file_as)
        self.redraw.clicked.connect(self.draw_file)

        self.serial_manager.send_print.connect(self.print)

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
            "x_drive": self.drive_x.currentIndex(),
            "x_ratio": self.ratio_x.value(),
            "x_play": self.play_x.value(),
            "x_reverse": bool(self.reverse_x.checkState()),
            "y_drive": self.drive_y.currentIndex(),
            "y_ratio": self.ratio_y.value(),
            "y_play": self.play_y.value(),
            "y_reverse": bool(self.reverse_y.checkState()),
            "z_drive": self.drive_z.currentIndex(),
            "z_ratio": self.ratio_z.value(),
            "z_play": self.play_z.value(),
            "z_reverse": bool(self.reverse_z.checkState()),
        }

    # Slots
    @pyqtSlot(str, str)
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
        logger.info("Sending file.")
        self.print("Sending file.", "info")
        gcode = self.code_edit.toPlainText().split('\n')
        self.send_thread = SendFileThread(self.serial_manager, gcode)

        self.sending_progress.setMaximum(len(gcode))
        self.sending_progress.setValue(0)
        self.btn_send_current_file.setText("Annuler l'envoi")
        self.btn_send_current_file.clicked.disconnect()
        self.btn_send_current_file.clicked.connect(self.send_thread.stop)
        self.tabWidget.setEnabled(False)

        self.send_thread.finished.connect(self.file_sent)
        self.send_thread.update_progress.connect(self.update_progress)
        self.send_thread.start()

    @pyqtSlot(int)
    def update_progress(self, s):
        self.sending_progress.setValue(s)

    @pyqtSlot()
    def file_sent(self):
        if self.send_thread.user_stop:
            self.print("Stopped by user.", "error")
            logger.error("File sending stopped by user.")
        else:
            self.print("Done.", "info")
            logger.info("File sent.")
        self.sending_progress.setValue(0)
        self.btn_send_current_file.setText("Envoyer le fichier courrant")
        self.btn_send_current_file.clicked.disconnect()
        self.btn_send_current_file.clicked.connect(self.send_file)
        self.tabWidget.setEnabled(True)

    @pyqtSlot()
    def send_cmd(self):
        gcode = self.command_edit.text()
        self.serial_manager.sendMsg(gcode)
        self.serial_manager.waitForConfirm()

    @pyqtSlot(int)
    def update_config(self, i):
        nb_config = self.config_list.count()
        if i == nb_config-1:
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
        f = QFileDialog.getSaveFileName(
            self, "Sélectionner un fichier",
            directory=settings.CONFIG_DIR,
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
        if self.serial_manager.is_open:
            self.baudrate.setEnabled(True)
            self.serial_ports_list.setEnabled(True)
            self.btn_serial_ports_list.setEnabled(True)
            self.btn_connect.setText("Connecter")
            self.serial_manager.close()
        else:
            port = self.serial_ports_list.currentText()
            baudrate = int(self.baudrate.currentText())
            if self.serial_manager.open(baudrate, port):
                self.baudrate.setEnabled(False)
                self.serial_ports_list.setEnabled(False)
                self.btn_serial_ports_list.setEnabled(False)
                self.btn_connect.setText("Déconnecter")

    @pyqtSlot()
    def choose_file(self):
        file = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier",
            directory=settings.FILE_DIR,
            filter='GCode files (*.gcode, *.ngc)\nAll files (*)')[0]

        if file is not '':
            self.filename.setText(file)
            self.load_file()

    @pyqtSlot()
    def load_file(self):
        file = self.filename.text()
        try:
            logger.info("Loading {}".format(repr(file)))
            with open(file) as f:
                self.code_edit.setText(f.read())
            self.draw_file()
        except FileNotFoundError:
            self.choose_file()

    @pyqtSlot()
    def save_file_as(self):
        file = QFileDialog.getSaveFileName(
            self, "Sélectionner un fichier",
            directory=settings.FILE_DIR,
            filter='GCode files (*.gcode, *.ngc)\nAll files (*)')[0]
        if file is not '':
            logger.info("Saving {}".format(repr(file)))
            self.filename.setText(file)
            with open(file, 'w') as f:
                f.write(self.code_edit.toPlainText())

    @pyqtSlot()
    def save_file(self):
        file = self.filename.text()
        if file == 'Pas de fichier':
            self.save_file_as()
        else:
            logger.info("Saving {}".format(repr(file)))
            with open(file, 'w') as f:
                f.write(self.code_edit.toPlainText())

    @pyqtSlot()
    def draw_file(self):
        gcode = self.code_edit.toPlainText()
        self.sc.clear()
        current_pos = [0, 0, 0]
        for n, t in enumerate(parse(gcode)):
            if t['name'] is not 'G':
                continue

            x, y, z = current_pos

            if self.display_draw_steps.isChecked():
                txt = self.sc.addText(str(n))
                txt.setPos(x, y)
                txt.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable |
                             QGraphicsItem.ItemIsSelectable | txt.flags())

            x = t['args'].get('X', x)
            y = t['args'].get('Y', y)
            z = t['args'].get('Z', z)

            p = QPen(QColor((z <= 0) * 255, 0, (z > 0) * 255))

            if t['value'] in (0, 1):
                self.sc.addLine(current_pos[0], current_pos[1], x, y, pen=p)
            elif t['value'] in (2, 3):
                i, j, k, = current_pos
                i = t['args'].get('I', i)
                j = t['args'].get('J', j)
                k = t['args'].get('K', k)

                pp = QPainterPath()

                h = sqrt(i**2 + j**2)
                if h == 0:
                    current_pos = x, y, z
                    continue

                center_x = current_pos[0] + i
                center_y = current_pos[1] + j

                clockwise = (t['value'] == 2)

                direction_end = -1
                direction_begin = -1
                if y - center_y != 0:
                    direction_end = -(y - center_y) / abs(y - center_y)
                if current_pos[1] - center_y != 0:
                    direction_begin = - \
                        (current_pos[1] - center_y) / \
                        abs(current_pos[1] - center_y)

                c = (current_pos[0] - center_x) / h
                if c < -1:
                    c = -1
                elif c > 1:
                    c = 1
                start_angle = direction_begin * acos(c) / 2 / pi * 360

                c = (x - center_x) / h
                if c < -1:
                    c = -1
                elif c > 1:
                    c = 1
                end_angle = direction_end * acos(c) / 2 / pi * 360

                pp.moveTo(current_pos[0], current_pos[1])
                if clockwise:
                    pp.arcTo(center_x - h, center_y - h, h * 2, h *
                             2, start_angle, start_angle - end_angle)
                else:
                    pp.arcTo(center_x - h, center_y - h, h * 2, h *
                             2, start_angle, end_angle - start_angle)
                self.sc.addPath(pp, p)
            current_pos = x, y, z

        self.fileview.setScene(self.sc)
