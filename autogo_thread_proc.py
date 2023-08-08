import time
import autogo
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QMutex
import check_user
from tkinter import filedialog

import review_record

mutex = QMutex()


class AccountCheck(QThread):
    signal = pyqtSignal(str, list)

    def __init__(self, user, config, callback):
        super().__init__()
        self.user = user
        self.config = config
        self.callback = callback
        self.signal.connect(self.callback)

    def run(self) -> None:
        mutex.lock()
        res = check_user.account_check(self.config)
        mutex.unlock()
        self.signal.emit(res, self.user)

class SelectFile(QThread):
    signal = pyqtSignal(str)

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.signal.connect(self.callback)

    def run(self) -> None:
        mutex.lock()
        file_path = filedialog.askopenfilename(title='Please select a file...',
                                               filetypes=(
                                                   ('origin file', '*.c'), ('origin file', '*.C'),
                                                   ('origin file', '*.h'),
                                                   ('origin file', '*.H')))
        mutex.unlock()
        self.signal.emit(file_path)


class AutogoProc(QThread):
    signal = pyqtSignal(str)

    def __init__(self, config, callback):
        super().__init__()
        self.config = config
        self.callback = callback
        self.signal.connect(self.callback)

    def run(self) -> None:
        mutex.lock()
        start_time = time.time()
        res = autogo.auto_go_program(self.config)
        end_time = time.time()
        time_consume = str(round(int(end_time - start_time) / 60, 1))
        mention = res + ' Time: ' + time_consume + '(min)'
        mutex.unlock()
        self.signal.emit(mention)



class BuildRecord(QThread):
    signal = pyqtSignal(str)

    def __init__(self, config, callback):
        super().__init__()
        self.config = config
        self.callback = callback
        self.signal.connect(self.callback)

    def run(self) -> None:
        mutex.lock()
        res = review_record.review_program(self.config)
        mutex.unlock()
        self.signal.emit(res)


class CloseRecord(QThread):
    signal = pyqtSignal(str)

    def __init__(self, config, callback):
        super().__init__()
        self.config = config
        self.callback = callback
        self.signal.connect(self.callback)

    def run(self) -> None:
        mutex.lock()
        res = review_record.review_program(self.config)
        mutex.unlock()
        self.signal.emit(res)

