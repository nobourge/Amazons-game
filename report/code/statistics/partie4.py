#!/usr/bin/env python3

# std
from sys import argv
from time import time

from PyQt5.QtWidgets import QApplication

from gui import App


def main():
    app = QApplication(argv)
    if not app:
        app = QApplication(argv)
    ex = App()
    return app.exec_()


if __name__ == '__main__':
    exit(main())
