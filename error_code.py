class err_class:
    def __init__(self):
        self.ok = 'Success!'
        self.file_err = 'C file error!'
        self.waiting = 'Please waiting...'
        self.no_file = 'Please input a file!'
        self.no_record = 'Information cannot be queried.'
        self.if_err = 'if phase error!'

    def void_check(self, input_str: str):
        if input_str == '' or input_str is None:
            return True
        else:
            return False
