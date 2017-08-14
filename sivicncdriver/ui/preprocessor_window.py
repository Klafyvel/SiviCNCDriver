# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preprocessor_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(561, 298)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("traceIcon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialog.setWindowIcon(icon)
        dialog.setModal(True)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(dialog)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget_2 = QtWidgets.QWidget(dialog)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(self.widget_2)
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.chk_del_num = QtWidgets.QCheckBox(self.groupBox)
        self.chk_del_num.setChecked(True)
        self.chk_del_num.setObjectName("chk_del_num")
        self.verticalLayout.addWidget(self.chk_del_num)
        self.chk_del_comments = QtWidgets.QCheckBox(self.groupBox)
        self.chk_del_comments.setChecked(True)
        self.chk_del_comments.setObjectName("chk_del_comments")
        self.verticalLayout.addWidget(self.chk_del_comments)
        self.chk_optimize_bounding_box = QtWidgets.QCheckBox(self.groupBox)
        self.chk_optimize_bounding_box.setToolTip("")
        self.chk_optimize_bounding_box.setChecked(True)
        self.chk_optimize_bounding_box.setObjectName("chk_optimize_bounding_box")
        self.verticalLayout.addWidget(self.chk_optimize_bounding_box)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.btn_run_preproc = QtWidgets.QPushButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/rc/rc/work.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_run_preproc.setIcon(icon1)
        self.btn_run_preproc.setObjectName("btn_run_preproc")
        self.verticalLayout_3.addWidget(self.btn_run_preproc)
        self.horizontalLayout.addWidget(self.widget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.output = QtWidgets.QTextEdit(self.groupBox_2)
        self.output.setObjectName("output")
        self.verticalLayout_2.addWidget(self.output)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_4.addWidget(self.widget_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("dialog", "Preprocessor"))
        self.groupBox.setTitle(_translate("dialog", "Parameters"))
        self.chk_del_num.setText(_translate("dialog", "Remove numbering (NXX)"))
        self.chk_del_comments.setText(_translate("dialog", "Remove comments"))
        self.chk_optimize_bounding_box.setText(_translate("dialog", "Minimize bounding box"))
        self.btn_run_preproc.setText(_translate("dialog", "Run preprocessor"))
        self.groupBox_2.setTitle(_translate("dialog", "Output"))

from sivicncdriver.ui import ressources_rc
