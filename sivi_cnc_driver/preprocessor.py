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

from preprocessor_interface import Ui_dialog

from gcodeParser import parse_instr


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
        r = ''
        for i in parse_instr(self.gcode):
            if 'M' in i['name'] or 'G' in i['name']:
                if not rm_nums and 'N' in i['args']:
                    r += 'N' + str(int(i['args']['N'])) + ' '
                r += i['name'] + str(int(i['value'])) + ' '
                for a in i['args']:
                    if a in 'XYZIJF':
                        r += a + str(i['args'][a]) + ' '
                if 'comment' in i['args'] and not rm_comm:
                    t += '(' + i['args']['comment'] + ')'
                r += '\n'
        self.output.setText(r)
        self.gcode = r

    def run_calcs(self):
        # for i in parse_instr(self.gcode):
        #     if ''
        pass

    @pyqtSlot()
    def cancel(self):
        self.gcode = self.original
        self.reject()
