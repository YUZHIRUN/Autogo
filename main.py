import sys
import safe
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

import code_generate_op
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtCore


if __name__ == '__main__':
    if safe.right_verification() is True:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        app = QApplication(sys.argv)
        main_window = QMainWindow()

        widget_obj = code_generate_op.gui_op()
        widget_obj.setupUi(main_window)

        widget_obj.trigger_register()
        widget_obj.trigger_back()
        widget_obj.trigger_switch_tool()

        widget_obj.trigger_select_file()
        widget_obj.trigger_load()
        widget_obj.trigger_clear()

        widget_obj.trigger_auto_go()
        widget_obj.trigger_build_record()
        widget_obj.trigger_close_record()

        widget_obj.trigger_disp_func()
        widget_obj.trigger_disp_global_var()
        widget_obj.trigger_disp_macro()
        widget_obj.trigger_disp_struct()
        widget_obj.trigger_disp_enum()
        widget_obj.trigger_disp_union()

        main_window.show()
        sys.exit(app.exec_())
    else:
        pass