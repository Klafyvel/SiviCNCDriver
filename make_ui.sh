#! /bin/bash

cd sivicncdriver/ui
pyrcc5 ressources.qrc -o ressources_rc.py
pyuic5 preprocessor_window.ui --import-from=sivicncdriver.ui -o preprocessor_window.py
pyuic5 main_window.ui --import-from=sivicncdriver.ui -o main_window.py