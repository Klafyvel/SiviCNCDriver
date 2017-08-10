#! /bin/bash

cd sivi_cnc_driver
pyuic5 preprocessor_window.ui -o preprocessor_window.py
pyuic5 main_window.ui -o main_window.py