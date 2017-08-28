import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *

from sivicncdriver import settings
from sivicncdriver.ui.interface import MainWindow


def main():
    """
    The main function of the application.

    It will create a QApplication and a main window then run the application and
    exit.
    """
    app = QApplication(sys.argv)

    qtTranslator = QTranslator()
    translate_path = os.path.join(
        settings.TRANSLATE_DIR,
        "SiviCNCDriver_" + QLocale.system().name()
    )
    qtTranslator.load(translate_path)
    app.installTranslator(qtTranslator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
