import sys

from PyQt5.QtWidgets import QApplication

import settings
from settings import logger
from interface import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()