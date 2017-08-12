=============
SiviCNCDriver
=============

:Info: This is a Python program to control a CNC.
:Author: Hugo LEVY-FALK
:Date: 2017-08
:Version: 0.1.1

.. index: README
.. contents:: Table of Contents

------

Goal
====

SiviCNCDriver, as its name lets you guess, is designed to drive a CNC.

Installation
============
Using pip
---------
On any operating system with a python and pip installated, use pip (you may need superuser privilege) ::

    pip install sivicncdriver

Then you should be able to run the program with a simple::

    sivicnc

Binary distribution (Windows)
-----------------------------
If, for some reasons, you can't or don't want to use pip, a binary is available here_ .

.. _here: https://github.com/Klafyvel/SiviCNCDriver/releases/tag/v0.1.2

Contribute
===========

The project has its own Git repository on GitHub_.

.. _github: https://github.com/Klafyvel/SiviCNCDriver

You nill need ``virtualenv`` ::

    pip install --user virtualenv

Create a directory in which we will work. ::

    mkdir SiviCNCDriver
    cd SiviCNCDriver

Clone the project ::

    git clone https://github.com/Klafyvel/SiviCNCDriver.git

Then create the virtual environment ::

    virtualenv ENV

Activate it ::

    source ENV/bin/activate

Download the dependencies ::

    cd SiviCNCDriver
    pip install -r requirements.txt

You can code ! To test the code, run the application as package ::

    python -m sivicncdriver

If you need to re-create the ui after editing it with QtCreator, you can use `make_ui.sh` or directly `pyuic5`.


Custom G-codes
==============

SiviCNCDriver uses several custom G-Codes, they may change in the future.


+---------------------+--------------------------------------------------------------------------------------------------------------+
|Command              | Explanation                                                                                                  |
+=====================+==============================================================================================================+
|``S0 Xnnn Ynnn Znnn``| Perform a straight line with ``nnn`` in steps on the given axes. A negative number make the axis go backward.|
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S1 X Y Z``         | Trigger continuous advancement forward on the given axes.                                                    |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S2 X Y Z``         | Trigger continuous advancement backward on the given axes.                                                   |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S3 X Y Z``         | Stop continuous advancement (if exists) on the given axes.                                                   |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S4 Xnnn Ynnn Znnn``| Set the mm/step on the given axes.                                                                           |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S5 X Y Z``         | Set driving mode to normal on the given axes.                                                                |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S6 X Y Z``         | Set driving mode to max torque on the given axes.                                                            |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S7 X Y Z``         | Set driving mode to half steps on the given axes.                                                            |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S8 Xnnn Ynnn Znnn``| Set the play of the given axes, with ``nnn`` in millimeters.                                                 |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S9 X Y Z``         | Set the given axes sense to reverse.                                                                         |
+---------------------+--------------------------------------------------------------------------------------------------------------+
|``S10 X Y Z``        | Set the given axes sense to normal.                                                                          |
+---------------------+--------------------------------------------------------------------------------------------------------------+


License
=======

SiviCNCDriver
Copyright (C) 2017  Hugo LEVY-FALK

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
