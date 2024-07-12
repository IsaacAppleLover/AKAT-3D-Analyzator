# \file    main.py
# \author  IDS Imaging Development Systems GmbH
# \date    2021-01-15
# \since   1.2.0
# 
# \brief   This application demonstrates how to use the IDS peak genericAPI
#          combined with a QT widgets GUI to display images from Genicam
#          compatible device.
# 
# \version 1.3.0
# 
# Copyright (C) 2021 - 2024, IDS Imaging Development Systems GmbH.
# 
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
# 
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
# 
# General permission to copy or modify is hereby granted.

import sys

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication

from mainwindow import MainWindow


def main():
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    try:
        return a.exec()
    except AttributeError:
        return a.exec_()


if __name__ == "__main__":
    sys.exit(main())
