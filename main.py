import sys
import code_generate_op
from PyQt5.QtWidgets import QMainWindow, QApplication

app = QApplication(sys.argv)
main_window = QMainWindow()

widget_obj = code_generate_op.gui_op()
widget_obj.setupUi(main_window)

widget_obj.trigger_load_file()
widget_obj.trigger_th_load()
widget_obj.trigger_clear()

widget_obj.trigger_disp_func()
widget_obj.trigger_rename()
widget_obj.trigger_disp_struct()
widget_obj.trigger_disp_enum()
widget_obj.trigger_disp_macro()
widget_obj.trigger_disp_global_var()

main_window.show()
sys.exit(app.exec_())
