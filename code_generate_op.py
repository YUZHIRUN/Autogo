import json
import os
import time
import autogo
import code_generate
import generate_code
import error_code
import threading
from tkinter import filedialog
from PyQt5.QtCore import QTimer

import review_record

err = error_code.err_class()
op_lock = threading.Lock()

g_name_list = list()
g_content_list = list()


class gui_op(code_generate.Ui_MainWindow):
    def __init__(self):
        self.timer = QTimer()
        self.load_status = False
        self.timer.timeout.connect(self.event_timer_operate)

    def event_timer_operate(self):
        if self.load_status is False:
            self.loading_dis()
        else:
            self.load_over()
            self.timer.stop()

    def loading_dis(self):
        self.load_dis.setMaximum(0)
        self.load_dis.setMinimum(0)

    def load_over(self):
        self.load_dis.setMaximum(0)
        self.load_dis.setMinimum(100)
        self.load_dis.setValue(0)

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

    def event_auto_go(self):
        self.mention.setText(err.autogo_wait)
        self.load_status = False
        op_lock.acquire()
        while True:
            if os.path.exists('.config/detail_config.json') is True and (
                    err.void_check(self.user_id.text()) is True or err.void_check(
                self.user_key.text()) is True or err.void_check(self.obj_url.text()) is True or err.void_check(
                self.base_coor.text()) is True):
                with open('.config/detail_config.json') as cfg_obj:
                    config = json.load(cfg_obj)
                    self.user_id.clear()
                    self.user_key.clear()
                    self.base_coor.clear()
                    self.obj_folder.clear()
                    self.obj_url.clear()

                    self.user_id.setText(config['user_id'])
                    self.user_key.setText(config['user_key'])
                    self.base_coor.setText(config['base folder'])
                    self.obj_folder.setText(config['object folder'])
                    self.obj_url.setText(config['link'])
                    self.browser.setCurrentText(config['browser'])
                    if config['visible'] is True:
                        self.visible_bt.setChecked(True)
                    else:
                        self.visible_bt.setChecked(False)
                self.mention.setText(err.ok)
                break
            user_id = self.user_id.text()
            user_key = self.user_key.text()
            base_coor = self.base_coor.text()
            obj_coor = self.obj_folder.text()
            obj_link = self.obj_url.text()
            browser = self.browser.currentText()
            visible = self.visible_bt.isChecked()
            config = {'user_id': user_id, 'user_key': user_key, 'base folder': base_coor, 'object folder': obj_coor,
                      'link': obj_link,
                      'browser': browser, 'visible': visible}
            if err.void_check(config['user_id']) is True:
                self.mention.setText(err.no_id)
                break
            if err.void_check(config['user_key']) is True:
                self.mention.setText(err.no_key)
                break
            if err.void_check(config['base folder']) is True:
                self.mention.setText(err.no_base_folder)
                break
            if err.void_check(config['object folder']) is True:
                self.mention.setText(err.no_obj_folder)
                break
            if err.void_check(config['link']) is True:
                self.mention.setText(err.no_url)
                break
            with open('.config/detail_config.json', 'w') as obj:
                json.dump(config, obj)
            start_time = time.time()
            res = autogo.auto_go_program(config)
            end_time = time.time()
            time_consume = str(round(int(end_time - start_time) / 60, 1))
            self.mention.setText(res + ' Time: ' + time_consume + '(min)')
            break
        op_lock.release()
        self.load_status = True

    def event_review(self):
        self.mention.setText(err.autogo_wait)
        self.load_status = False
        op_lock.acquire()
        while True:
            if os.path.exists('.config/review_config.json') is True and (
                    err.void_check(self.user_id.text()) is True or err.void_check(
                self.user_key.text()) is True or err.void_check(self.review_link.text()) is True or err.void_check(
                self.moderator_id.text()) is True):
                with open('.config/review_config.json') as cfg_obj:
                    config = json.load(cfg_obj)
                    self.user_id.clear()
                    self.user_key.clear()
                    self.review_link.clear()
                    self.moderator_id.clear()

                    self.user_id.setText(config['user_id'])
                    self.user_key.setText(config['user_key'])
                    self.review_link.setText(config['link'])
                    self.moderator_id.setText(config['moderator id'])
                    self.review_type.setCurrentText(config['review area'])
                    self.browser.setCurrentText(config['browser'])
                    if config['visible'] is True:
                        self.visible_bt.setChecked(True)
                    else:
                        self.visible_bt.setChecked(False)
                self.mention.setText(err.ok)
                break
            # comment information
            user_id = self.user_id.text()
            user_key = self.user_key.text()
            browser = self.browser.currentText()
            visible = self.visible_bt.isChecked()

            mode = self.review_mode.currentText()
            moderator_id = self.moderator_id.text()
            review_type = self.review_type.currentText()
            link = self.review_link.text()

            config = {'user_id': user_id, 'user_key': user_key, 'browser': browser, 'visible': visible, 'mode': mode,
                      'moderator id': moderator_id, 'review area': review_type, 'link': link}
            if err.void_check(config['user_id']) is True:
                self.mention.setText(err.no_id)
                break
            if err.void_check(config['user_key']) is True:
                self.mention.setText(err.no_key)
                break
            if err.void_check(config['link']) is True:
                self.mention.setText(err.no_url)
                break
            if err.void_check(config['moderator id']) is True:
                self.mention.setText(err.no_moderator)
                break
            with open('.config/review_config.json', 'w') as obj:
                json.dump(config, obj)
            res = review_record.review_program(config)
            self.mention.setText(res)
            break
        op_lock.release()
        self.load_status = True

    # threading-------------------------------------------------------------------------------
    def th_load_file(self):
        th = threading.Thread(target=self.event_select_file)
        th.start()

    def th_load(self):
        th = threading.Thread(target=self.event_load)
        th.start()

    def th_auto_go(self):
        self.timer.start(100)
        th = threading.Thread(target=self.event_auto_go)
        th.start()

    def th_review(self):
        self.timer.start(100)
        th = threading.Thread(target=self.event_review)
        th.start()

    #  trigger--------------------------------------------------------------------------------
    def trigger_load_file(self):
        self.select_bt.clicked.connect(self.th_load_file)

    def trigger_load(self):
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

    def trigger_auto_go(self):
        self.auto_bt.clicked.connect(self.th_auto_go)

    def trigger_review(self):
        self.record_bt.clicked.connect(self.th_review)
