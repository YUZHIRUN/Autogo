from PyQt5.QtWidgets import QDialog, QWidget
from Prompt import *
from tips import *

class err_class:
    def __init__(self):
        self.ok = 'Autogo operate successful!'
        self.file_err = 'C file error!'
        self.draw_error = 'Draw flow chart failure!'
        self.convert_code_error = 'Convert Error!'
        self.waiting = 'Please waiting...'
        self.no_file = 'Please input a file!'
        self.no_record = 'Information cannot be queried.'
        self.if_err = 'if phase error!'
        self.regular_err = 'regular expression error!'
        self.cfg_err = 'Configuration file error!'
        self.no_id = 'Please input user id!'
        self.no_key = 'Please input password!'
        self.no_base_folder = 'Please input base folder!'
        self.no_obj_folder = 'Please input object folder!'
        self.base_coor_err = 'Base folder format is error!'
        self.no_url = 'Please input object url!'
        self.no_moderator = 'Please input moderator Id!'
        self.autogo_swdd_wait = 'Autogo is building software detail design...'
        self.record_build_wait = 'Autogo is building review record...'
        self.record_close_wait = 'Autogo is closing review record...'
        self.no_load = 'Please load a file!'
        self.user_info_err = 'Please check your user id or password!'
        self.password_err = 'Please check your password!'
        self.user_cfg_err = 'User config file error!'

        self.driver_interrupt = 'Browser interrupt!'
        self.driver_over = 'Browser driver overdue!'

    def void_check(self, input_str: str):
        if input_str == '' or input_str is None:
            return True
        else:
            return False

    class Prompt(QDialog, Ui_Dialog):
        def __init__(self, mention=None):
            super().__init__()
            self.setupUi(self)
            self.mention = mention
            self.mention_proc()

        def mention_proc(self):
            self.prompt.setText(self.mention)

    class Tips(QWidget, Ui_Form):
        def __init__(self, global_vars):
            super().__init__()
            self.setupUi(self)
            self.global_vars = global_vars
            self.tips_proc()

        def tips_proc(self):
            self.listWidget.addItems(self.global_vars)

