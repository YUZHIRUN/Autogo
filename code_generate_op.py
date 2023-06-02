import code_generate
import generate_code
import error_code
import threading
from tkinter import filedialog

err = error_code.err_class()
op_lock = threading.Lock()

g_name_list = list()
g_content_list = list()


class gui_op(code_generate.Ui_MainWindow):

    def clear_disp(self):
        self.func_items.clear()
        self.struct_items.clear()
        self.enum_items.clear()
        self.macro_items.clear()
        self.global_var_num.clear()

    def display_info(self, file_path, mode_op='load'):
        ret, name_list, content_list, num_list = generate_code.get_code_info(file_path, mode=mode_op)
        g_name_list.clear()
        g_content_list.clear()
        self.clear_disp()
        g_name_list.extend(name_list)
        g_content_list.extend(content_list)
        if ret == err.ok:
            self.func_num.setText(str(num_list[0]))
            self.global_var_num.setText(str(num_list[1]))
            self.macro_num.setText(str(num_list[2]))
            self.struct_num.setText(str(num_list[3]))
            self.enum_num.setText(str(num_list[4]))
            self.union_num.setText(str(num_list[5]))
            if len(name_list[0]) != 0:
                for name_idx in name_list[0]:
                    self.func_items.addItem(name_idx)
            if len(name_list[1]) != 0:
                for name_idx in name_list[1]:
                    self.func_items.addItem(name_idx)
            if len(name_list[2]) != 0:
                for name_idx in name_list[2]:
                    self.global_items.addItem(name_idx)
            if len(name_list[3]) != 0:
                for name_idx in name_list[3]:
                    self.macro_items.addItem(name_idx)
            if len(name_list[4]) != 0:
                for name_idx in name_list[4]:
                    self.struct_items.addItem(name_idx)
            if len(name_list[5]) != 0:
                for name_idx in name_list[5]:
                    self.enum_items.addItem(name_idx)
            if len(name_list[6]) != 0:
                for name_idx in name_list[6]:
                    self.union_item.addItem(name_idx)
        return ret

    # event-----------------------------------------------------------------------------------
    def event_select_file(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        file_path = filedialog.askopenfilename(title='Please select a file...',
                                               filetypes=(
                                                   ('origin file', '*.c'), ('origin file', '*.C'),
                                                   ('origin file', '*.h'),
                                                   ('origin file', '*.H')))
        if err.void_check(file_path) is False:
            self.file_path.setText(file_path)
            self.mention.setText(err.ok)
        else:
            self.mention.setText(err.no_file)
        op_lock.release()

    def event_load(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        file_path = self.file_path.text()
        while True:
            if err.void_check(file_path) is True:
                ret = err.no_file
                self.mention.setText(ret)
                break
            ret = self.display_info(file_path)
            self.mention.setText(ret)
            break
        op_lock.release()

    def event_clear_info(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        while True:
            file_path = self.file_path.text()
            if err.void_check(file_path) is True:
                self.mention.setText(err.no_file)
                break
            generate_code.clear_info()
            ret = self.display_info(file_path, mode_op='clear')
            self.func_items.clear()
            self.global_items.clear()
            self.struct_items.clear()
            self.enum_items.clear()
            self.macro_items.clear()
            self.union_item.clear()
            self.func_disp.clear()
            self.gloabal_disp.clear()
            self.struct_disp.clear()
            self.enum_disp.clear()
            self.macro_disp.clear()
            self.union_disp.clear()
            self.mention.setText(ret)
            break
        op_lock.release()

    def event_disp_func(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.func_items.currentItem().text()
        while True:
            if g_name_list[0].count(name) != 0:
                index = g_name_list[0].index(name)
                content = g_content_list[0][index]
            elif g_name_list[1].count(name) != 0:
                index = g_name_list[1].index(name)
                content = g_content_list[1][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.func_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    def event_disp_global_var(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.global_items.currentItem().text()
        while True:
            if g_name_list[2].count(name) != 0:
                index = g_name_list[2].index(name)
                content = g_content_list[2][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.gloabal_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    def event_disp_macro(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.macro_items.currentItem().text()
        while True:
            if g_name_list[3].count(name) != 0:
                index = g_name_list[3].index(name)
                content = g_content_list[3][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.macro_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    def event_disp_struct(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.struct_items.currentItem().text()
        while True:
            if g_name_list[4].count(name) != 0:
                index = g_name_list[4].index(name)
                content = g_content_list[4][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.struct_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    def event_disp_enum(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.enum_items.currentItem().text()
        while True:
            if g_name_list[5].count(name) != 0:
                index = g_name_list[5].index(name)
                content = g_content_list[5][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.enum_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    def event_disp_union(self):
        self.mention.setText(err.waiting)
        op_lock.acquire()
        name = self.union_item.currentItem().text()
        while True:
            if g_name_list[6].count(name) != 0:
                index = g_name_list[6].index(name)
                content = g_content_list[6][index]
            else:
                self.mention.setText(err.no_record)
                break
            self.union_disp.setPlainText(content)
            self.mention.setText(err.ok)
            break
        op_lock.release()

    # threading-------------------------------------------------------------------------------
    def th_load_file(self):
        th = threading.Thread(target=self.event_select_file)
        th.start()

    def th_load(self):
        th = threading.Thread(target=self.event_load)
        th.start()

    #  trigger--------------------------------------------------------------------------------
    def trigger_load_file(self):
        self.select_bt.clicked.connect(self.th_load_file)

    def trigger_th_load(self):
        self.load_bt.clicked.connect(self.th_load)

    def trigger_clear(self):
        self.clear_bt.clicked.connect(self.event_clear_info)

    def trigger_disp_func(self):
        self.func_items.clicked.connect(self.event_disp_func)

    def trigger_disp_struct(self):
        self.struct_items.clicked.connect(self.event_disp_struct)

    def trigger_disp_enum(self):
        self.enum_items.clicked.connect(self.event_disp_enum)

    def trigger_disp_macro(self):
        self.macro_items.clicked.connect(self.event_disp_macro)

    def trigger_disp_global_var(self):
        self.global_items.clicked.connect(self.event_disp_global_var)

    def trigger_disp_union(self):
        self.union_item.clicked.connect(self.event_disp_union)
