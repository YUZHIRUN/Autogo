class err_class:
    def __init__(self):
        self.ok = 'Successful operation!'
        self.file_err = 'C file error!'
        self.waiting = 'Please waiting...'
        self.no_file = 'Please input a file!'
        self.no_record = 'Information cannot be queried.'
        self.if_err = 'if phase error!'
        self.regular_err = 'regular expression error!'
        self.cfg_err = 'Configuration file error!'
        self.no_id = 'Please input user id!'
        self.no_key = 'Please input password!'
        self.no_base_folder = 'Please input base folder!'
        self.base_coor_err = 'Base folder format is error!'
        self.no_url = 'Please input object url!'
        self.autogo_wait = 'AutoGo is running...'

        self.driver_interrupt = 'Browser interrupt!'

    def void_check(self, input_str: str):
        if input_str == '' or input_str is None:
            return True
        else:
            return False
