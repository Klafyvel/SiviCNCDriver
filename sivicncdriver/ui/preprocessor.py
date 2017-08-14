"""
The preprocessor module
=======================

Provides the PreprocessorDialog class.
"""
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from sivicncdriver.ui.preprocessor_window import Ui_dialog
from sivicncdriver import settings
from sivicncdriver.settings import logger
from sivicncdriver.gcode import parse
from sivicncdriver.arc_calculator import arc_to_segments


class PreprocessorDialog(QDialog, Ui_dialog):
    """
    The preprocessor dialog.
    """
    def __init__(self, gcode, parent=None):
        """
        The __init__ method.
        :param gcode: The gcode which is to be preprocessed.
        :param parent: Qt stuff.
        :type gcode: str
        """
        super(PreprocessorDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.gcode = gcode
        self.original = gcode
        self.has_been_run_once = False
        
        self.btn_run_preproc.clicked.connect(self.run_preprocessor)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.cancel)

    @pyqtSlot()
    def run_preprocessor(self):
        """
        Runs the preprocessor on the G-Code.
        """
        self.remove_useless()
        self.has_been_run_once = True

    def remove_useless(self):
        """
        Remove useless things in the code according to the UI options.
        """
        rm_nums = self.chk_del_num.isChecked()
        rm_comm = self.chk_del_comments.isChecked()
        minimize = self.chk_optimize_bounding_box.isChecked()
        if minimize:
            x,y = self.get_minimize_bounding_box()
        r = ''
        last_g00 = None
        line = 0
        for i in parse(self.gcode):
            if 'M' in i['name'] or 'G' in i['name']:
                if not rm_nums and 'N' in i['args']:
                    r += 'N' + str(int(i['args']['N'])) + ' '
                r += i['name'] + str(int(i['value'])) + ' '
                for a in i['args']:
                    if (not minimize and a in 'XY') or (a in 'ZIJKF'):
                        r += a + str(i['args'][a]) + ' '
                    elif minimize and a =='X':
                        r += a + str(i['args'][a]-x) + ' '
                    elif minimize and a == 'Y':
                        r += a + str(i['args'][a]-y) + ' '
                if i['name'] == 'G' and i['value'] == 0:
                    last_g00 = line
                r += '\n'
                line += 1
            if 'comment' in i['args'] and not rm_comm:
                logger.debug(i)
                r += '(' + i['args']['comment'] + ')\n'
                line += 1
        if last_g00:
            r = r.split('\n')
            r[last_g00] = 'G00 X0.0000 Y0.0000'
            r = '\n'.join(r)
        self.output.setText(r)
        self.gcode = r

    def get_minimize_bounding_box(self):
        """
        Computes a new origin for the drawing.
        """
        min_x, min_y = 0,0
        set_x, set_y = False, False
        x_o, y_o = 0,0
        x,y = 0,0
        z = 0
        r = ''
        for t in parse(self.gcode):
            if t['name'] is not 'G':
                continue
            if 'Z' in t['args']:
                z = t['args']['Z']
            if z > 0 or t['value'] not in (1,2,3) or not('X' in t['args'] or 'Y' in t['args']):
                x_o = t['args'].get('X', x_o)
                y_o = t['args'].get('Y', y_o)
                continue
            if 'X' in t['args']:
                x = t['args']['X']
                if not set_x:
                    min_x = x
                    set_x = True
                if x < min_x:
                    logger.debug("min_x becomes {x} from {t}".format(**locals()))
                min_x = min(min_x, x)
            if 'Y' in t['args']:
                y = t['args']['Y']
                if not set_y :
                    min_y = y
                    set_y = True
                if y < min_y:
                    logger.debug("min_y becomes {y} from {t}".format(**locals()))
                min_y = min(min_y, y)

            if t['value'] in (2,3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)
                k = t['args'].get('K', 0)
                clockwise = (t['value'] == 2)
                for xc, yc in arc_to_segments((x_o, y_o), (i,j), (x,y), clockwise):
                    print(xc, yc)
                    if not set_x:
                        min_x = xc
                        set_x = True
                    if not set_y:
                        min_y = yc
                        set_y = True
                    if xc < min_x:
                        logger.debug("min_x becomes {xc} from {t}".format(**locals()))
                    if yc < min_y:
                        logger.debug("min_y becomes {yc} from {t}".format(**locals()))
                    min_x = min(min_x, xc)
                    min_y = min(min_y, yc)
            x_o, y_o = x,y
        logger.debug("Minimizing by setting origin to {},{}".format(min_x,min_y))
        return min_x, min_y


    @pyqtSlot()
    def accept(self):
        if not self.has_been_run_once:
            self.run_preprocessor()
        super(PreprocessorDialog, self).accept()

    @pyqtSlot()
    def cancel(self):
        self.gcode = self.original
        self.reject()
