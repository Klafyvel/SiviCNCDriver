"""
The interface module
====================

Provides the MainWindow class. 
"""

import serial
from math import atan2, sqrt, pi
import os
import json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from sivicncdriver import settings
from sivicncdriver.settings import logger
from sivicncdriver.gcode import parse
from sivicncdriver.serial_list import serial_ports
from sivicncdriver.serial_manager import SerialManager
from sivicncdriver.ui.preprocessor import PreprocessorDialog
from sivicncdriver.arc_calculator import arc_to_segments
from sivicncdriver.thread_send import SendThread
from sivicncdriver.thread_read import ReadThread
import sivicncdriver.gcode_maker as gcode_maker

from sivicncdriver.ui.main_window import Ui_MainWindow

__all__ = ['MainWindow']

_translate = QtCore.QCoreApplication.translate

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main window of the application.
    """

    def __init__(self):
        """
        The __init__ method.

        It will set the UI up, list available serial ports, list available
        configurations, connect the UI and so on.
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.zoom = 1
        self.list_serials()
        self.list_configs()

        self.set_serial_mode("manual")

        self.serial_manager = SerialManager(serial.Serial(timeout=0))

        s = """Welcome to SiviCNCDriver, by Klafyvel from sivigik.com"""
        self.print(s, msg_type="info")

        self.sc = QGraphicsScene(self.fileview)
        self.connectUi()
        self.update_config(self.config_list.currentIndex())

        self.file_loaded = False

        self.send_thread = None
        self.waiting_cmd = []

        self.last_selected_path = None
        self.last_selected_item = None

        self.read_thread = None

    def connectUi(self):
        """
        Connects The UI signals and slots.
        """
        logger.debug("Connecting Ui.")
        self.btn_serial_ports_list.clicked.connect(self.list_serials)

        self.btn_y_plus.pressed.connect(self.start_continuous_y_forward)
        self.btn_y_minus.pressed.connect(self.start_continuous_y_backward)
        self.btn_x_plus.pressed.connect(self.start_continuous_x_forward)
        self.btn_x_minus.pressed.connect(self.start_continuous_x_backward)
        self.btn_z_plus.pressed.connect(self.start_continuous_z_forward)
        self.btn_z_minus.pressed.connect(self.start_continuous_z_backward)
        self.btn_y_plus.released.connect(self.stop_y)
        self.btn_y_minus.released.connect(self.stop_y)
        self.btn_x_plus.released.connect(self.stop_x)
        self.btn_x_minus.released.connect(self.stop_x)
        self.btn_z_plus.released.connect(self.stop_z)
        self.btn_z_minus.released.connect(self.stop_z)
        self.btn_set_origin.clicked.connect(self.set_origin)
        self.btn_go_to_zero.clicked.connect(self.goto_origin)
        self.btn_emergency_stop.clicked.connect(self.emergency_stop)

        self.auto_cmd_type.currentIndexChanged.connect(
            self.manage_auto_cmd_number)
        self.btn_run_auto_cmd.clicked.connect(self.auto_cmd)
        self.manage_auto_cmd_number(self.auto_cmd_type.currentIndex())

        self.btn_run_custom_cmd.clicked.connect(self.run_custom_cmd)

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
        self.btn_close.clicked.connect(self.close_file)

        self.serial_manager.send_print.connect(self.print)

        self.btn_preprocessor.clicked.connect(self.run_preprocessor)

        self.display_axis.clicked.connect(self.draw_file)
        self.display_draw_steps.clicked.connect(self.draw_file)
        self.display_bounding_box.clicked.connect(self.draw_file)
        self.reverse_display_x.clicked.connect(self.draw_file)
        self.reverse_display_y.clicked.connect(self.draw_file)
        self.reverse_display_z.clicked.connect(self.draw_file)

        self.btn_license.clicked.connect(self.about_license)
        self.btn_about_qt.clicked.connect(self.about_qt)

        self.zoomIn_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self)
        self.zoomOut_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self)

        self.zoomIn_shortcut.activated.connect(self.zoomIn)
        self.zoomOut_shortcut.activated.connect(self.zoomOut)

        self.sc.selectionChanged.connect(self.highlight_selected_line)
        self.code_edit.cursorPositionChanged.connect(self.highlight_selected_path)

    def list_serials(self):
        """
        Lists available serials ports.
        """
        logger.debug("Listing available serial ports.")
        l = serial_ports()
        for i in range(self.serial_ports_list.count()):
            self.serial_ports_list.removeItem(0)
        for i in l:
            logger.info("Found {}".format(i))
            self.serial_ports_list.addItem(i)

    def list_configs(self):
        """
        Lists available configurations.
        """
        for _ in range(self.config_list.count()):
            self.config_list.removeItem(0)
        logger.debug("Listing available configurations.")
        for f in os.listdir(settings.CONFIG_DIR):
            if f.endswith(".json"):
                logger.debug("Found {}".format(f))
                self.config_list.addItem(f[:-5])
        self.config_list.addItem(_translate("MainWindow", "New configuration"))

    def set_serial_mode(self, mode):
        """
        Change serial mode.

        :param mode: can be "manual" or "file"
        :type mode: str
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
        """
        Resets the configuration.
        """
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

        self.minTime_x.setValue(5)
        self.minTime_y.setValue(5)
        self.minTime_z.setValue(5)

        logger.info("Reset config.")

    def config_as_dict(self):
        """
        Get the configuration as a dict.

        :return: The configuration as a dict.
        :rtype: dict
        """
        return {
            "x_drive": self.drive_x.currentIndex(),
            "x_ratio": self.ratio_x.value(),
            "x_play": self.play_x.value(),
            "x_reverse": bool(self.reverse_x.checkState()),
            "x_min_time": self.minTime_x.value(),
            "y_drive": self.drive_y.currentIndex(),
            "y_ratio": self.ratio_y.value(),
            "y_play": self.play_y.value(),
            "y_reverse": bool(self.reverse_y.checkState()),
            "y_min_time": self.minTime_y.value(),
            "z_drive": self.drive_z.currentIndex(),
            "z_ratio": self.ratio_z.value(),
            "z_play": self.play_z.value(),
            "z_reverse": bool(self.reverse_z.checkState()),
            "z_min_time": self.minTime_z.value(),
        }

    def run_thread(self, gcode, n=None, disable=True, allow_waiting=True):
        """
        Run a thread to send the diven gcode.
        :param gcode: The gcode as a list of commands.
        :param n: a length for the sending_process.
        :param disable: Should the ui elements which trigger sending be
            disabled ?
        :param allow_waiting: If True and a thread is already running, wait for
            it to end before sending the command. Else stop the current thread.
        :type gcode: list
        :type n: int
        :type disable: bool
        :type allow_waiting: bool
        """
        if self.send_thread and allow_waiting:
            logger.info("Thread already in use, waiting for the end.")
            self.waiting_cmd.append({"gcode":gcode, "n":n, "disable":disable})
            return
        elif self.send_thread:
            self.send_thread.stop()
            self.serial_manager.serial.flush()

        self.send_thread = SendThread(self.serial_manager, gcode)
        if n:
            self.sending_progress.setMaximum(n)
        else:
            self.sending_progress.setMaximum(len(gcode))
        self.sending_progress.setValue(0)
        self.btn_send_current_file.setText("Annuler l'envoi")
        self.btn_send_current_file.clicked.disconnect()
        self.btn_send_current_file.clicked.connect(self.send_thread.stop)
        
        if disable:
            self.tabWidget.setEnabled(False)

        
        self.send_thread.read_allowed.connect(self.read_thread.set_read_allowed)
        self.serial_manager.send_confirm.connect(self.send_thread.confirm)

        self.send_thread.finished.connect(self.sending_end)
        self.send_thread.update_progress.connect(self.update_progress)
        self.send_thread.start()


    # Slots
    @pyqtSlot(str, str)
    def print(self, txt, msg_type="operator"):
        """
        Prints a message on the application console.

        :param txt: The message
        :param msg_type: The type of the message. Can be "operator", "machine",
            "error" or "info"
        :type txt: str
        :type msg_type: str
        """

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
        """
        Enable the widgets for auto commands
        """
        self.auto_cmd_number.setValue(1)
        self.auto_cmd_number.setEnabled(n != 1)
        self.auto_cmd_2.setEnabled(n != 1)

    @pyqtSlot()
    def auto_cmd(self):
        """
        Sends auto commands using a thread if they are too long.
        """
        logger.info("Sending auto command.")
        self.print("Sending auto command.", "info")

        axis = self.auto_cmd_axis.currentText()
        n = self.auto_cmd_number.value()
        step = self.auto_cmd_step.value()

        if self.auto_cmd_type.currentIndex() == 1:
            it = [gcode_maker.step(axis, step)]
        else:
            axis2 = self.auto_cmd_axis_2.currentText()
            step2 = self.auto_cmd_step_2.value()

            # AKA "Do not do this at home kids" :
            it = (
                (
                    (
                        gcode_maker.step(axis, step),
                        gcode_maker.step(axis, -step)
                    )[(i%4)>=2], 
                    gcode_maker.step(axis2, step2)
                )[i%2] for i in range(4*n-1)
            )

        self.run_thread(it, n)

    @pyqtSlot()
    def run_custom_cmd(self):
        """
        Sends a custom command using a thread.
        """
        logger.info("Sending custom command.")
        self.print("Sending custom command.", "info")
        gcode = self.custom_cmd.toPlainText().split('\n')
        n = self.custom_cmd_number.value()
        l = len(gcode)

        it = (gcode[i%l] for i in range(n*l))

        self.run_thread(it, n*l)

    @pyqtSlot()
    def send_file(self):
        """
        Send a file using a different thread.
        """
        logger.info("Sending file.")
        self.print("Sending file.", "info")
        gcode = self.code_edit.toPlainText().split('\n')
        self.run_thread(gcode)

    @pyqtSlot()
    def send_cmd(self):
        """
        Sends an user command using a thread.
        """
        gcode = [self.command_edit.text()]
        logger.info("Sending command.")
        self.print("Sending command.", "info")
        self.run_thread(gcode)

    @pyqtSlot()
    def send_config(self):
        """
        Send a configuration to the machine.
        """
        self.save_config()
        gcode = gcode_maker.config_as_gcode(**self.config_as_dict()).split('\n')
        logger.info("Sending configuration.")
        self.print("Sending configuration.", "info")
        self.run_thread(gcode)

    @pyqtSlot()
    def sending_end(self):
        """
        Manages the end of upload. If some commands are waiting, run them at the
        end.
        """

        self.send_thread.read_allowed.disconnect()
        self.serial_manager.send_confirm.disconnect()

        if self.send_thread and self.send_thread.user_stop:
            self.print("Stopped by user.", "error")
            logger.error("Upload stopped by user.")
        else:
            self.print("Done.", "info")
            logger.info("Upload done.")
        self.sending_progress.setValue(0)
        self.btn_send_current_file.setText("Envoyer le fichier courrant")
        self.btn_send_current_file.clicked.disconnect()
        self.btn_send_current_file.clicked.connect(self.send_file)
        self.tabWidget.setEnabled(True)

        self.send_thread = None

        if len(self.waiting_cmd)>0:
            self.run_thread(**self.waiting_cmd.pop(0))

    @pyqtSlot()
    def start_continuous_y_forward(self):
        self.run_thread([gcode_maker.start_continuous_y_forward()], disable=False)

    @pyqtSlot()
    def start_continuous_y_backward(self):
        self.run_thread([gcode_maker.start_continuous_y_backward()], disable=False)

    @pyqtSlot()
    def start_continuous_x_forward(self):
        self.run_thread([gcode_maker.start_continuous_x_forward()], disable=False)

    @pyqtSlot()
    def start_continuous_x_backward(self):
        self.run_thread([gcode_maker.start_continuous_x_backward()], disable=False)

    @pyqtSlot()
    def start_continuous_z_forward(self):
        self.run_thread([gcode_maker.start_continuous_z_forward()], disable=False)

    @pyqtSlot()
    def start_continuous_z_backward(self):
        self.run_thread([gcode_maker.start_continuous_z_backward()], disable=False)

    @pyqtSlot()
    def stop_y(self):
        self.run_thread([gcode_maker.stop_y()])

    @pyqtSlot()
    def stop_x(self):
        self.run_thread([gcode_maker.stop_x()])

    @pyqtSlot()
    def stop_z(self):
        self.run_thread([gcode_maker.stop_z()])

    @pyqtSlot()
    def emergency_stop(self):
        self.run_thread([gcode_maker.emergency_stop()], allow_waiting=False)

    @pyqtSlot()
    def set_origin(self):
        self.run_thread([gcode_maker.set_origin()])

    @pyqtSlot()
    def goto_origin(self):
        self.run_thread([gcode_maker.goto_origin()])


    @pyqtSlot(int)
    def update_progress(self, s):
        """
        Updates the progress bar.
        """
        self.sending_progress.setValue(s)

    @pyqtSlot(int)
    def manage_emulate_serial_port(self, s):
        """
        Enable widgets for serial port emulation.
        """
        st = bool(s)
        self.serial_manager.fake_mode = st
        self.baudrate.setEnabled(not st)
        self.serial_ports_list.setEnabled(not st)
        self.btn_serial_ports_list.setEnabled(not st)
        self.btn_connect.setEnabled(not st)
        if st:
            self.print("Emulating serial port.", "info")
            self.read_thread = ReadThread()
            self.read_thread.read.connect(self.serial_manager.readMsg)
            self.read_thread.start()
        else:
            self.print("Exiting serial port emulation.", "info")
            self.read_thread.read.disconnect()
            self.read_thread.stop()

    @pyqtSlot(int)
    def update_config(self, i):
        """
        Updates the configuration widgets.
        """
        nb_config = self.config_list.count()
        if i == nb_config-1:
            self.reset_config()
        else:
            file = self.config_list.currentText() + ".json"
            file = os.path.join(settings.CONFIG_DIR, file)
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

            self.minTime_x.setValue(config.get("x_min_time", 5));
            self.minTime_y.setValue(config.get("y_min_time", 5));
            self.minTime_z.setValue(config.get("z_min_time", 5));

    @pyqtSlot()
    def save_config(self, filename=None):
        """
        Saves a configuration.
        :param filename: The name of the file.
        :type filename: str
        """
        logger.info("Saving configuration.")
        logger.debug("Filename given : {}".format(filename))
        current_config = self.config_list.currentIndex()
        nb_config = self.config_list.count()
        if current_config == nb_config-1 and not filename:
            self.save_config_as()
        else:
            if not filename:
                file = self.config_list.currentText() + ".json"
                file = os.path.join(settings.CONFIG_DIR, file)
            else:
                file = filename
            config = self.config_as_dict()
            with open(file, "w") as f:
                json.dump(config, f)

    @pyqtSlot()
    def save_config_as(self):
        """
        Saves a configuration in a new file.
        """
        f = QFileDialog.getSaveFileName(
            self, _translate("MainWindow","Select file"),
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
    def manage_connection(self):
        """
        Manages the connection widgets.
        """
        if self.serial_manager.is_open:
            if self.send_thread:
                self.emergency_stop()
            self.read_thread.read.disconnect()
            self.read_thread.stop()
            self.baudrate.setEnabled(True)
            self.serial_ports_list.setEnabled(True)
            self.btn_serial_ports_list.setEnabled(True)
            self.btn_connect.setText(_translate("MainWindow", "Connect"))
            self.serial_manager.close()
        else:
            port = self.serial_ports_list.currentText()
            baudrate = int(self.baudrate.currentText())
            if self.serial_manager.open(baudrate, port):
                self.read_thread = ReadThread()
                self.baudrate.setEnabled(False)
                self.serial_ports_list.setEnabled(False)
                self.btn_serial_ports_list.setEnabled(False)
                self.btn_connect.setText(_translate("MainWindow", "Disconnect"))
                self.read_thread.read.connect(self.serial_manager.readMsg)
                self.read_thread.start()

    @pyqtSlot()
    def choose_file(self):
        """
        Sets the gcode file.
        """
        if not self.file_loaded:
            directory = settings.FILE_DIR
        else:
            directory = os.path.dirname(self.filename.text())
        file = QFileDialog.getOpenFileName(
            self, _translate("MainWindow", "Select file"),
            directory=directory,
            filter='GCode files (*.gcode, *.ngc)\nAll files (*)')[0]

        if file is not '':
            self.filename.setText(file)
            self.load_file()

    @pyqtSlot()
    def load_file(self):
        """
        Loads a gcode file.
        """
        file = self.filename.text()
        try:
            logger.info("Loading {}".format(repr(file)))
            with open(file) as f:
                self.code_edit.setText(f.read())
            self.draw_file()
            self.file_loaded = True
        except FileNotFoundError:
            self.choose_file()

    @pyqtSlot()
    def save_file_as(self):
        """
        Saves a gcode file in a nex file.
        """
        if not self.file_loaded:
            directory = settings.FILE_DIR
        else:
            directory = os.path.dirname(self.filename.text())
        file = QFileDialog.getSaveFileName(
            self, _translate("MainWindow", "Select file"),
            directory=directory,
            filter='GCode files (*.gcode, *.ngc)\nAll files (*)')[0]
        if file is not '':
            logger.info("Saving {}".format(repr(file)))
            self.filename.setText(file)
            with open(file, 'w') as f:
                f.write(self.code_edit.toPlainText())
            self.file_loaded = True

    @pyqtSlot()
    def save_file(self):
        """
        Saves a gcode file.
        """
        if not self.file_loaded:
            self.save_file_as()
        else:
            file = self.filename.text()
            logger.info("Saving {}".format(repr(file)))
            with open(file, 'w') as f:
                f.write(self.code_edit.toPlainText())

    @pyqtSlot()
    def close_file(self):
        """
        Close the current file.
        """
        self.filename.setText(_translate("MainWindow", "No file."))
        self.code_edit.setText("")
        self.draw_file()

    @pyqtSlot()
    def draw_file(self, highlight_line=None):
        """
        Draws a gcode file.

        :param highlight_line: A line which is to be highlighted.
        :type highlight_line: int
        """
        gcode = self.code_edit.toPlainText()
        self.sc.clear()
        current_pos = [0, 0, 0]
        min_x, max_x, min_y, max_y, min_z, max_z = 0, 0, 0, 0, 0, 0

        reverse_x = self.reverse_display_x.isChecked()
        reverse_y = self.reverse_display_y.isChecked()
        reverse_z = self.reverse_display_z.isChecked()

        current_line = None

        for n, t in enumerate(parse(gcode)):
            logger.debug("Processing from {t}, highlight={highlight_line}".format(**locals()))
            if t['name'] == '__error__':
                self.chk_display_current_line.setChecked(False)
                self.code_edit.setExtraSelections([])
                QMessageBox.critical(self, _translate("MainWindow", "Error."), 
                    _translate("MainWindow", "An error occurred during parsing."))
                logger.error("While parsing line {}".format(t['line']))
                highlight = QTextEdit.ExtraSelection()
                highlight.cursor = QTextCursor(self.code_edit.document().findBlockByLineNumber(t['line']))
                highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
                highlight.format.setBackground(Qt.red)
                self.code_edit.setTextCursor(highlight.cursor)
                self.code_edit.setExtraSelections([highlight])
                break
            
            current_line = t['line']


            if t['name'] is not 'G':
                continue

            x, y, z = current_pos

            if self.display_draw_steps.isChecked():
                effective_x = x if not reverse_x else -x
                effective_y = y if not reverse_y else -y
                txt = self.sc.addText(str(n))
                txt.setPos(effective_x, effective_y)
                txt.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable |
                             QGraphicsItem.ItemIsSelectable | txt.flags())

            x = t['args'].get('X', x)
            y = t['args'].get('Y', y)
            z = t['args'].get('Z', z)


            effective_z = z if not reverse_z else -z


            if t['line'] == highlight_line:
                p = QPen(QColor(0, 255,0))
                p.setWidthF(3/self.zoom)
            else:
                p = QPen(QColor((effective_z <= 0) * 255, 0, (effective_z > 0) * 255))
                p.setWidthF(1/self.zoom)

            effective_x_o = current_pos[0] if not reverse_x else -current_pos[0]
            effective_y_o = current_pos[1] if not reverse_y else -current_pos[1]


            pp = QPainterPath()
            pp.moveTo(effective_x_o,effective_y_o)

            if t['value'] in (0, 1):
                logger.debug("Drawing a line.".format(**locals()))
                effective_x = x if not reverse_x else -x
                effective_y = y if not reverse_y else -y
                pp.lineTo(effective_x, effective_y)
            elif t['value'] in (2, 3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)
                k = t['args'].get('K', 0)

                x_o = current_pos[0]
                y_o = current_pos[1]

                clockwise = (t['value'] == 2)

                logger.debug(
                    "Drawing circle clockwise={clockwise}".format(**locals()))
                for xc, yc in arc_to_segments((x_o, y_o), (i, j), (x, y), clockwise, 1/self.zoom):
                    effective_x = xc if not reverse_x else -xc
                    effective_y = yc if not reverse_y else -yc
                    min_x = min(min_x, effective_x)
                    max_x = max(max_x, effective_x)
                    min_y = min(min_y, effective_y)
                    max_y = max(max_y, effective_y)
                    pp.lineTo(effective_x,effective_y)

            path_item = self.sc.addPath(pp,pen=p)
            path_item.setFlags(QGraphicsItem.ItemIsSelectable | path_item.flags())
            path_item.setData(0, t['line'])

            if current_line == highlight_line:
                p2 = QPen(QColor((effective_z <= 0) * 255, 0, (effective_z > 0) * 255))
                p2.setWidthF(1/self.zoom)
                path_item.setData(1, p2)
                self.last_selected_item = path_item

            current_pos = x, y, z

            min_x = min(min_x, effective_x_o)
            max_x = max(max_x, effective_x_o)
            min_y = min(min_y, effective_y_o)
            max_y = max(max_y, effective_y_o)
            min_z = min(min_z, current_pos[2])
            max_z = max(max_z, current_pos[2])

        self.space_x.display(max_x-min_x)
        self.space_y.display(max_y-min_y)
        self.space_z.display(max_z-min_z)

        if self.display_bounding_box.isChecked():
            p = QPen(QColor(0, 255, 0))
            self.sc.addRect(min_x, min_y, max_x-min_x, max_y-min_y, p)
            txt1 = self.sc.addText(str(max_x-min_x))
            txt1.setPos((min_x+max_x)/2, max_y)
            txt2 = self.sc.addText(str(max_y-min_y))
            txt2.setPos(max_x, (min_y+max_y)/2)

        if self.display_axis.isChecked():
            arrow_length = min(self.space_x.value(), self.space_y.value())
            if reverse_x:
                arrow_length_x = - arrow_length
            else:
                arrow_length_x = arrow_length
            if reverse_y:
                arrow_length_y = - arrow_length
            else:
                arrow_length_y = arrow_length
            
            sign = lambda x: (1, -1)[x < 0]

            x_axis_arrow = QPainterPath()
            x_axis_arrow.lineTo(arrow_length_x,0)
            x_axis_arrow.lineTo(0.95*arrow_length_x,0.05*arrow_length_x)
            x_axis_arrow.moveTo(arrow_length_x,0)
            x_axis_arrow.lineTo(0.95*arrow_length_x,-0.05*arrow_length_x)
            x_axis_arrow.addText(arrow_length_x*1.1, -10 * sign(arrow_length_y), QFont("sans-serif"), "X")
            self.sc.addPath(x_axis_arrow)

            y_axis_arrow = QPainterPath()
            y_axis_arrow.lineTo(0, arrow_length_y)
            y_axis_arrow.lineTo(0.05*arrow_length_y, 0.95*arrow_length_y)
            y_axis_arrow.moveTo(0, arrow_length_y)
            y_axis_arrow.lineTo(-0.05*arrow_length_y, 0.95*arrow_length_y)
            y_axis_arrow.addText(-10 * sign(arrow_length_x), arrow_length_y*1.1, QFont("sans-serif"), "Y")
            self.sc.addPath(y_axis_arrow)
        
        logger.debug("Drawing done, setting scene to view.")
        self.fileview.setScene(self.sc)
        logger.debug("Done.")
        logger.debug("Min x : {min_x}, min y : {min_y}".format(**locals()))

    @pyqtSlot()
    def run_preprocessor(self):
        """
        Runs the preprocessor dialog.
        """
        self.preprocessor = PreprocessorDialog(self.code_edit.toPlainText())
        self.preprocessor.accepted.connect(self.end_preprocessor)
        self.preprocessor.show()

    @pyqtSlot()
    def end_preprocessor(self):
        """
        Manages the end of the preprocessing interface.
        """
        self.code_edit.setText(self.preprocessor.gcode)
        self.preprocessor.accepted.disconnect()
        self.draw_file()

    @pyqtSlot()
    def about_license(self):
        """
        Displays informations about the license.
        """
        with open(os.path.join(settings.APP_DIR, 'license_dialog_text')) as f:
            QMessageBox.about(self, _translate("MainWindow", "License"), f.read())

    @pyqtSlot()
    def about_qt(self):
        """
        Displays informations about Qt.
        """
        QMessageBox.aboutQt(self)

    @pyqtSlot()
    def zoomIn(self):
        """
        Zoom the file view in.
        """
        self.fileview.scale(2,2)
        self.zoom *= 2
        self.draw_file()

    @pyqtSlot()
    def zoomOut(self):
        """
        Zoom the file view out.
        """
        self.fileview.scale(1/2,1/2)
        self.zoom *= 1/2
        self.draw_file()

    @pyqtSlot()
    def highlight_selected_line(self):
        """
        Highlight corresponding gcode lines for the selected path.
        """
        self.code_edit.cursorPositionChanged.disconnect()
        self.code_edit.setExtraSelections([])
        sel = self.sc.selectedItems()
        l = []
        i = None
        if self.last_selected_item:
            self.last_selected_item.setPen(self.last_selected_item.data(1))

        for s in sel:
            highlight = QTextEdit.ExtraSelection()
            highlight.cursor = QTextCursor(self.code_edit.document().findBlockByLineNumber(s.data(0)))
            highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
            highlight.format.setBackground(Qt.green)
            l.append(highlight)
            i = s.data(0)
            s.setData(1, QPen(s.pen()))
            p = QPen(QColor(0, 255,0))
            p.setWidthF(3/self.zoom)
            s.setPen(p)
            self.last_selected_item = s
        
        self.last_selected_path = i
        self.code_edit.setExtraSelections(l)
        if len(l) > 0:
            self.code_edit.setTextCursor(l[0].cursor)

        self.code_edit.cursorPositionChanged.connect(self.highlight_selected_path)


    @pyqtSlot()
    def highlight_selected_path(self):
        if not self.chk_display_current_line.isChecked():
            return

        i = self.code_edit.textCursor().blockNumber()
        if i == self.last_selected_path:
            return
        else:
            self.last_selected_path = i
            self.last_selected_item = None
        self.code_edit.setExtraSelections([])
        highlight = QTextEdit.ExtraSelection()
        highlight.cursor = self.code_edit.textCursor()
        highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
        highlight.format.setBackground(Qt.green)
        self.code_edit.setExtraSelections([highlight])
        self.draw_file(highlight_line=i)
