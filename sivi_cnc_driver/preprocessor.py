# Trace
# Copyright (C) 2015  Hugo LEVY-FALK
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .preprocessor_window import Ui_dialog

from .settings import logger
from .gcode import parse
from .arc_calculator import arc_to_segments


class PreprocessorDialog(QDialog, Ui_dialog):

    def __init__(self, gcode, parent=None):
        super(PreprocessorDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.gcode = gcode
        self.original = gcode

        self.btn_run_preproc.clicked.connect(self.run_preprocessor)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.cancel)

        self.gcode_vars = {}

    @pyqtSlot()
    def run_preprocessor(self):
        self.remove_useless()

    def remove_useless(self):
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
        r = r.split('\n')
        r[last_g00] = 'G00 X0.0000 Y0.0000'
        r = '\n'.join(r)
        self.output.setText(r)
        self.gcode = r

    def get_minimize_bounding_box(self):
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
            logger.debug("Z = {}".format(z))
            if z > 0 :
                continue
            logger.debug("Obviously, z<=0.")
            if 'X' in t['args']:
                x = t['args']['X']
                if not set_x :
                    min_x = x
                    set_x = True
                min_x = min(min_x, x)
            if 'Y' in t['args']:
                y = t['args']['Y']
                if not set_y :
                    min_y = y
                    set_y = True
                min_y = min(min_y, y)

            if t['value'] in (2,3):
                i = t['args'].get('I', 0)
                j = t['args'].get('J', 0)
                k = t['args'].get('K', 0)
                clockwise = (t['value'] == 2)
                for xc, yc in arc_to_segments((x_o, y_o), (i,j), (x,y), clockwise):
                    min_x = min(min_x, xc)
                    min_y = min(min_y, yc)
            x_o, y_o = x,y
        logger.debug("Minimizing by setting origin to {},{}".format(x,y))
        return min_x, min_y

    def run_calcs(self):
        # for i in parse_instr(self.gcode):
        #     if ''
        pass

    @pyqtSlot()
    def cancel(self):
        self.gcode = self.original
        self.reject()
