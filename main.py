import sys

from PyQt5.QtWidgets import QApplication

import settings
from settings import logger
# from interface import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    logger.debug(settings.APP_DIR)
    sys.exit()