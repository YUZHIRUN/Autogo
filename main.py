import sys
import safe_lic
from PyQt5.QtCore import Qt
from autogo_interaction import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore


def get_qss():
    with open('autogo.qss', 'r') as obj:
        qss = obj.read()
    return qss


if __name__ == '__main__':
    if safe_lic.right_verification() is True:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        app = QApplication(sys.argv)
        qss = get_qss()
        app.setStyleSheet(qss)

        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    else:
        pass
