import json
import csv
import Autogo_ui
import generate_code
import error_code
from error_code import *
from autogo_thread_proc import *
from PyQt5.QtWidgets import QMainWindow
import convert_item as convert
from PyQt5.QtCore import QTimer

err = error_code.err_class()

VERSION = 'Version:3.6 '
g_name_list = list()
g_content_list = list()
g_user_id = ''
g_user_key = ''
g_browser = ''

def check_user_cfg() -> bool:
    if os.path.exists('.private/__user.csv') is True:
        return True
    else:
        return False

def del_user(user: str):
    current_user = list()
    with open('.private/__user.csv', 'r') as obj:
        reader = csv.reader(obj)
        for e in reader:
            if len(e) != 0:
                current_user.append(e)
    for e in current_user:
        for i in e:
            if i.count(user) != 0:
                current_user.remove(e)
    with open('.private/__user.csv', 'w') as w_obj:
        writer = csv.writer(w_obj)
        writer.writerows(current_user)


def add_user(user_info: list):
    exist_check = False
    with open('.private/__user.csv', 'r') as r_obj:
        reader = csv.reader(r_obj)
        for e in reader:
            if e == user_info:
                exist_check = True
                break
    if exist_check is False:
        with open('.private/__user.csv', 'a') as user_obj:
            writer = csv.writer(user_obj)
            writer.writerow(user_info)


def user_reg(user_info: list):
    res = err.user_info_err
    if check_user_cfg() is False:
        res = err.user_cfg_err
    else:
        with open('.private/__user.csv', 'r') as user_obj:
            content_list = csv.reader(user_obj)
            for user in content_list:
                if len(user) != 0:
                    if user[0] == user_info[0] and user[1] == user_info[1]:
                        res = err.ok
                    elif user[0] == user_info[0] and user[1] != user_info[1]:
                        del_user(user_info[0])
    return res


class MainWindow(Autogo_ui.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.timer = QTimer()
        self.load_status = ''
        self.thread = None
        self.mention = None
        self.tips = None
        self.browser_over = None
        self.timer.timeout.connect(self.event_timer_operate)
        self.set_version()
        self.trigger_register()
        self.trigger_back()
        self.trigger_switch_tool()
        self.trigger_select_file()
        self.trigger_load()
        self.trigger_clear()
        self.trigger_auto_go()
        self.trigger_build_record()
        self.trigger_close_record()
        self.trigger_convert_code()
        self.trigger_convert_graph()
        self.trigger_pseudo_code_clear()
        self.trigger_graph_xml_clear()
        self.trigger_disp_func()
        self.trigger_disp_global_var()
        self.trigger_disp_macro()
        self.trigger_disp_struct()
        self.trigger_disp_enum()
        self.trigger_disp_union()

    def check_load(self):
        func_n = int(self.func_num.text())
        g_var = int(self.global_var_num.text())
        macro_n = int(self.macro_num.text())
        st_n = int(self.struct_num.text())
        enum_n = int(self.enum_num.text())
        union_n = int(self.union_num.text())
        if func_n == 0 and g_var == 0 and macro_n == 0 and st_n == 0 and st_n == 0 and enum_n == 0 and union_n == 0:
            return False
        else:
            return True

    def mention_to_user(self, content):
        self.mention = Prompt(content)
        self.mention.show()

    def event_timer_operate(self):
        if self.load_status == 'swdd_start':
            self.loading_dis()
        elif self.load_status == 'swdd_over':
            self.loading_dis(mode='over')
            self.timer.stop()
        elif self.load_status == 'review_start':
            self.loading_dis(progress_type='review', mode='load')
        elif self.load_status == 'review_over':
            self.loading_dis(progress_type='review', mode='over')
            self.timer.stop()
        else:
            pass

    def loading_dis(self, progress_type='swdd', mode='load'):
        if progress_type == 'swdd':
            if mode == 'load':
                self.swdd_progress.setMaximum(0)
                self.swdd_progress.setMinimum(0)
            else:
                self.swdd_progress.setMinimum(0)
                self.swdd_progress.setMaximum(100)
                self.swdd_progress.setValue(0)
        else:
            if mode == 'load':
                self.review_progress.setMaximum(0)
                self.review_progress.setMinimum(0)
            else:
                self.review_progress.setMinimum(0)
                self.review_progress.setMaximum(100)
                self.review_progress.setValue(0)

    #
    def clear_disp(self):
        self.func_items.clear()
        self.struct_items.clear()
        self.enum_items.clear()
        self.macro_items.clear()
        self.global_items.clear()
        self.union_item.clear()

    #
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
            if len(name_list[0]) != 0:  # global function
                for name_idx in name_list[0]:
                    self.func_items.addItem(name_idx)
            if len(name_list[1]) != 0:  # local function
                for name_idx in name_list[1]:
                    self.func_items.addItem(name_idx)
            if len(name_list[2]) != 0:  # global var
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

    def event_register(self):
        global g_user_id, g_user_key, g_browser
        if (err.void_check(self.user_id.text()) is True or err.void_check(
                self.user_key.text()) is True) and os.path.exists('.config/user_config.json') is True:
            with open('.config/user_config.json', mode='r') as cfg_obj:
                self.user_id.clear()
                self.user_key.clear()

                cfg = json.load(cfg_obj)
                self.user_id.setText(cfg['user id'])
                self.user_key.setText(cfg['user key'])
                self.browser.setCurrentText(cfg['browser'])
        else:
            if err.void_check(self.user_id.text()) is True or self.user_id.text() == err.no_id:
                self.user_id.setText(err.no_id)
            elif err.void_check(self.user_key.text()) is True or self.user_id.text() == err.no_key:
                self.user_id.setText(err.no_key)
            else:
                g_user_id = self.user_id.text()
                g_user_key = self.user_key.text()
                g_browser = self.browser.currentText()

                config = {'user id': g_user_id, 'user key': g_user_key, 'browser': g_browser}
                user = list()
                user.append(g_user_id)
                user.append(g_user_key)
                res = user_reg(user)
                if res == err.user_info_err:
                    self.thread = AccountCheck(user, config, self.register_ui_proc)
                    self.thread.start()
                    return 0
                if res == err.ok:
                    cfg = {'user id': g_user_id, 'user key': g_user_key, 'browser': g_browser}
                    add_user(user)
                    with open('.config/user_config.json', mode='w') as cfg_obj:
                        json.dump(cfg, cfg_obj)
                    # check_user
                    self.stack_first.setCurrentWidget(self.tool_page)
                elif res == err.user_cfg_err:
                    g_user_id = ''
                    g_user_key = ''
                    g_browser = ''
                    self.user_id.clear()
                    self.user_key.clear()
                    self.mention_to_user(err.user_cfg_err)
                else:
                    g_user_id = ''
                    g_user_key = ''
                    g_browser = ''
                    self.user_id.clear()
                    self.user_key.clear()
                    self.user_id.setText(res)

    def register_ui_proc(self, res, user):
        global g_user_id, g_user_key, g_browser
        if res == err.ok:
            cfg = {'user id': g_user_id, 'user key': g_user_key, 'browser': g_browser}
            add_user(user)
            with open('.config/user_config.json', mode='w') as cfg_obj:
                json.dump(cfg, cfg_obj)
            # check_user
            self.stack_first.setCurrentWidget(self.tool_page)
        elif res == err.driver_over:
            g_user_id = ''
            g_user_key = ''
            g_browser = ''
            self.user_id.clear()
            self.user_key.clear()
            self.browser_over = BrowserOver()
            self.browser_over.show()
        else:
            g_user_id = ''
            g_user_key = ''
            g_browser = ''
            self.user_id.clear()
            self.user_key.clear()
            self.mention_to_user(res)
            # self.user_id.setText(res)

    def event_back(self):
        self.stack_first.setCurrentWidget(self.register_page)

    # region event
    def event_select_file(self):
        self.thread = SelectFile(self.select_file_ui_proc)
        self.thread.start()

    def select_file_ui_proc(self, file_path):
        if err.void_check(file_path) is False:
            self.file_path.setText(file_path)
        else:
            self.file_path.clear()
            # self.mention_to_user(err.no_file)

    def event_switch_tool(self):
        item = self.tool_item.selectedIndexes()[0]
        self.stack_second.setCurrentIndex(int(item.row()))

    def event_load(self):
        file_path = self.file_path.text()
        while True:
            if err.void_check(file_path) is True:
                ret = err.no_file
                self.mention_to_user(ret)
                break
            ret = self.display_info(file_path)
            another_global_vars = generate_code.g_another_global_vars
            if len(another_global_vars) != 0:
                self.tips = Tips(another_global_vars)
                self.tips.show()
                generate_code.g_another_global_vars.clear()
            if ret != err.ok:
                self.mention_to_user(ret)
            break

    def event_clear_info(self):
        while True:
            file_path = self.file_path.text()
            if err.void_check(file_path) is True:
                self.mention_to_user(err.no_file)
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
            if ret != err.ok:
                self.mention_to_user(ret)
            break

    def event_disp_func(self):
        name = self.func_items.currentItem().text()
        while True:
            if g_name_list[0].count(name) != 0:
                index = g_name_list[0].index(name)
                content = g_content_list[0][index]
            elif g_name_list[1].count(name) != 0:
                index = g_name_list[1].index(name)
                content = g_content_list[1][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.func_disp.setPlainText(content)
            break

    def event_disp_global_var(self):
        name = self.global_items.currentItem().text()
        while True:
            if g_name_list[2].count(name) != 0:
                index = g_name_list[2].index(name)
                content = g_content_list[2][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.gloabal_disp.setPlainText(content)
            break

    def event_disp_macro(self):
        name = self.macro_items.currentItem().text()
        while True:
            if g_name_list[3].count(name) != 0:
                index = g_name_list[3].index(name)
                content = g_content_list[3][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.macro_disp.setPlainText(content)
            break

    def event_disp_struct(self):
        name = self.struct_items.currentItem().text()
        while True:
            if g_name_list[4].count(name) != 0:
                index = g_name_list[4].index(name)
                content = g_content_list[4][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.struct_disp.setPlainText(content)
            break

    def event_disp_enum(self):
        name = self.enum_items.currentItem().text()
        while True:
            if g_name_list[5].count(name) != 0:
                index = g_name_list[5].index(name)
                content = g_content_list[5][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.enum_disp.setPlainText(content)
            break

    def event_disp_union(self):
        name = self.union_item.currentItem().text()
        while True:
            if g_name_list[6].count(name) != 0:
                index = g_name_list[6].index(name)
                content = g_content_list[6][index]
            else:
                self.mention_to_user(err.no_record)
                break
            self.union_disp.setPlainText(content)
            break

    def event_auto_go(self):
        self.swdd_mention.setText(err.autogo_swdd_wait)
        self.timer.start(100)
        while True:
            if err.void_check(g_user_id) is True:
                self.swdd_mention.setText(err.no_id)
                break
            if err.void_check(g_user_key) is True:
                self.swdd_mention.setText(err.no_key)
                break
            if os.path.exists('.config/detail_config.json') is True and (
                    err.void_check(self.swdd_url.text()) is True or err.void_check(
                self.base_coor.text()) is True or err.void_check(self.obj_folder.text()) is True):
                with open('.config/detail_config.json') as cfg_obj:
                    config = json.load(cfg_obj)
                    self.base_coor.clear()
                    self.obj_folder.clear()
                    self.swdd_url.clear()

                    self.base_coor.setText(config['base folder'])
                    self.obj_folder.setText(config['object folder'])
                    self.swdd_url.setText(config['link'])
                self.swdd_mention.setText(err.ok)
                break
            base_coor = self.base_coor.text()
            obj_coor = self.obj_folder.text()
            obj_link = self.swdd_url.text()
            config = {'base folder': base_coor, 'object folder': obj_coor, 'link': obj_link}
            if err.void_check(config['base folder']) is True:
                self.swdd_mention.setText(err.no_base_folder)
                break
            if err.void_check(config['object folder']) is True:
                self.swdd_mention.setText(err.no_obj_folder)
                break
            if err.void_check(config['link']) is True:
                self.swdd_mention.setText(err.no_url)
                break
            with open('.config/detail_config.json', 'w') as obj:
                json.dump(config, obj)
            config['user id'] = g_user_id
            config['user key'] = g_user_key
            config['browser'] = g_browser
            if err.void_check(self.file_path.text()) is True or self.check_load() is False:
                self.swdd_mention.setText(err.no_load)
                break
            self.load_status = 'swdd_start'
            self.thread = AutogoProc(config, callback=self.autogo_ui_proc)
            self.thread.start()
            break

    def autogo_ui_proc(self, mention):
        if mention.count(err.driver_over) != 0:
            self.swdd_mention.setText(mention)
            self.browser_over = BrowserOver()
            self.browser_over.show()
        else:
            self.swdd_mention.setText(mention)
        self.load_status = 'swdd_over'

    def event_build_record(self):
        self.review_mention.setText(err.record_build_wait)
        self.timer.start(100)
        while True:
            if err.void_check(g_user_id) is True:
                self.review_mention.setText(err.no_id)
                break
            if err.void_check(g_user_key) is True:
                self.review_mention.setText(err.no_key)
                break
            if os.path.exists('.config/review_config.json') is True and (
                    err.void_check(self.review_link.text()) is True or err.void_check(
                self.moderator_id.text()) is True):
                with open('.config/review_config.json') as cfg_obj:
                    config = json.load(cfg_obj)
                    self.review_link.clear()
                    self.moderator_id.clear()

                    self.review_link.setText(config['record link'])
                    self.moderator_id.setText(config['moderator id'])
                    self.review_type.setCurrentText(config['review area'])
                self.review_mention.setText(err.ok)
                break
            # comment information
            moderator_id = self.moderator_id.text()
            review_type = self.review_type.currentText()
            link = self.review_link.text()

            config = {'moderator id': moderator_id, 'review area': review_type, 'record link': link}
            if err.void_check(config['record link']) is True:
                self.review_mention.setText(err.no_url)
                break
            if err.void_check(config['moderator id']) is True:
                self.review_mention.setText(err.no_moderator)
                break
            with open('.config/review_config.json', 'w') as obj:
                json.dump(config, obj)
            config['user id'] = g_user_id
            config['user key'] = g_user_key
            config['browser'] = g_browser
            config['mode'] = 'build'
            self.load_status = 'review_start'
            self.thread = BuildRecord(config, callback=self.build_record_ui_proc)
            self.thread.start()
            break

    def build_record_ui_proc(self, res):
        self.review_mention.setText(res)
        self.load_status = 'review_over'

    def event_close_record(self):
        self.review_mention.setText(err.record_close_wait)
        self.timer.start(100)
        while True:
            if err.void_check(g_user_id) is True:
                self.review_mention.setText(err.no_id)
                break
            if err.void_check(g_user_key) is True:
                self.review_mention.setText(err.no_key)
                break
            # comment information
            link = self.close_link.text()
            if err.void_check(link) is True:
                self.review_mention.setText(err.no_url)
                break
            config = {'user id': g_user_id, 'user key': g_user_key, 'browser': g_browser, 'close link': link,
                      'mode': 'close'}
            self.load_status = 'review_start'
            self.thread = CloseRecord(config, self.close_record_ui_proc)
            self.thread.start()
            break

    def close_record_ui_proc(self, res):
        self.review_mention.setText(res)
        self.load_status = 'review_over'

    def event_convert_code(self):
        origin_code = self.origin_code.toPlainText()
        if err.void_check(origin_code) is True:
            res_code = 'No Origin code!'
        else:
            res_code = convert.convert_code_to_pseudo(origin_code)
        self.pseudo_code.clear()
        self.pseudo_code.setPlainText(res_code)

    def event_convert_graph_to_xml(self):
        origin_code = self.graph_origin.toPlainText()
        if err.void_check(origin_code) is True:
            res_xml = 'No Origin Pseudo-code!'
        else:
            res_xml = convert.convert_graph_to_xml(origin_code)
        self.graph.clear()
        self.graph.setPlainText(res_xml)

    def event_pseudo_code_clear(self):
        self.origin_code.clear()
        self.pseudo_code.clear()

    def event_xml_clear(self):
        self.graph_origin.clear()
        self.graph.clear()

    def set_version(self):
        self.version.setText(VERSION)


    # endregion event
    #  trigger--------------------------------------------------------------------------------
    def trigger_register(self):
        self.log_in_bt.clicked.connect(self.event_register)

    def trigger_back(self):
        self.back_bt.clicked.connect(self.event_back)

    def trigger_select_file(self):
        self.select_bt.clicked.connect(self.event_select_file)

    def trigger_load(self):
        self.load_bt.clicked.connect(self.event_load)

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

    def trigger_convert_code(self):
        self.code_change_bt.clicked.connect(self.event_convert_code)

    def trigger_convert_graph(self):
        self.graph_convert_bt.clicked.connect(self.event_convert_graph_to_xml)

    def trigger_pseudo_code_clear(self):
        self.pseudo_code_clear.clicked.connect(self.event_pseudo_code_clear)

    def trigger_graph_xml_clear(self):
        self.xml_clear.clicked.connect(self.event_xml_clear)

    #
    def trigger_auto_go(self):
        self.auto_bt.clicked.connect(self.event_auto_go)

    #
    def trigger_build_record(self):
        self.review_build_bt.clicked.connect(self.event_build_record)

    def trigger_close_record(self):
        self.review_close_bt.clicked.connect(self.event_close_record)

    def trigger_switch_tool(self):
        self.tool_item.clicked.connect(self.event_switch_tool)
