"""
This is the __main__ module of the sivicncdriver package.
"""
import sys

from PyQt5.QtWidgets import QApplication

from .interface import MainWindow

def main():
    """
    The main function of the application.

    It will create a QApplication and a main window then run the application and
    exit.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()