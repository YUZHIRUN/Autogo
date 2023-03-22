# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'code_generate.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(811, 868)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(811, 868))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        MainWindow.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ico/source/dev_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(9, 6, 791, 95))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.groupBox.setFont(font)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(10, 20, 781, 51))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(590, 64, 191, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(9, 106, 791, 281))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.macro_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.macro_num.setGeometry(QtCore.QRect(660, 160, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.macro_num.setFont(font)
        self.macro_num.setText("")
        self.macro_num.setReadOnly(True)
        self.macro_num.setObjectName("macro_num")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setGeometry(QtCore.QRect(47, 30, 80, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.select_bt = QtWidgets.QPushButton(self.groupBox_3)
        self.select_bt.setGeometry(QtCore.QRect(610, 30, 140, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.select_bt.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.select_bt.setFont(font)
        self.select_bt.setAutoFillBackground(True)
        self.select_bt.setObjectName("select_bt")
        self.local_func_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.local_func_num.setGeometry(QtCore.QRect(160, 90, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.local_func_num.setFont(font)
        self.local_func_num.setText("")
        self.local_func_num.setReadOnly(True)
        self.local_func_num.setObjectName("local_func_num")
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setGeometry(QtCore.QRect(530, 90, 131, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.file_path = QtWidgets.QLineEdit(self.groupBox_3)
        self.file_path.setGeometry(QtCore.QRect(127, 30, 460, 30))
        self.file_path.setAutoFillBackground(True)
        self.file_path.setFrame(True)
        self.file_path.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.file_path.setReadOnly(True)
        self.file_path.setObjectName("file_path")
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setGeometry(QtCore.QRect(340, 160, 51, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.struct_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.struct_num.setGeometry(QtCore.QRect(160, 160, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.struct_num.setFont(font)
        self.struct_num.setText("")
        self.struct_num.setReadOnly(True)
        self.struct_num.setObjectName("struct_num")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(100, 160, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.global_var_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.global_var_num.setGeometry(QtCore.QRect(660, 90, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.global_var_num.setFont(font)
        self.global_var_num.setText("")
        self.global_var_num.setReadOnly(True)
        self.global_var_num.setObjectName("global_var_num")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(270, 90, 121, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setGeometry(QtCore.QRect(530, 160, 141, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.enum_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.enum_num.setGeometry(QtCore.QRect(400, 160, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.enum_num.setFont(font)
        self.enum_num.setText("")
        self.enum_num.setReadOnly(True)
        self.enum_num.setObjectName("enum_num")
        self.global_func_num = QtWidgets.QLineEdit(self.groupBox_3)
        self.global_func_num.setGeometry(QtCore.QRect(400, 90, 60, 30))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.global_func_num.setFont(font)
        self.global_func_num.setText("")
        self.global_func_num.setReadOnly(True)
        self.global_func_num.setObjectName("global_func_num")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(40, 90, 111, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.load_bt = QtWidgets.QPushButton(self.groupBox_3)
        self.load_bt.setGeometry(QtCore.QRect(170, 230, 160, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.load_bt.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.load_bt.setFont(font)
        self.load_bt.setAutoFillBackground(True)
        self.load_bt.setObjectName("load_bt")
        self.clear_bt = QtWidgets.QPushButton(self.groupBox_3)
        self.clear_bt.setGeometry(QtCore.QRect(460, 230, 160, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.clear_bt.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.clear_bt.setFont(font)
        self.clear_bt.setAutoFillBackground(True)
        self.clear_bt.setObjectName("clear_bt")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(9, 394, 795, 430))
        self.tabWidget.setMinimumSize(QtCore.QSize(510, 381))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.tabWidget.setFont(font)
        self.tabWidget.setMouseTracking(False)
        self.tabWidget.setObjectName("tabWidget")
        self.Function = QtWidgets.QWidget()
        self.Function.setObjectName("Function")
        self.func_items = QtWidgets.QListWidget(self.Function)
        self.func_items.setGeometry(QtCore.QRect(7, 10, 256, 381))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.func_items.setFont(font)
        self.func_items.setFrameShape(QtWidgets.QFrame.Box)
        self.func_items.setFrameShadow(QtWidgets.QFrame.Raised)
        self.func_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.func_items.setObjectName("func_items")
        self.func_disp = QtWidgets.QTextEdit(self.Function)
        self.func_disp.setGeometry(QtCore.QRect(270, 10, 510, 381))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.func_disp.setFont(font)
        self.func_disp.setFrameShape(QtWidgets.QFrame.Box)
        self.func_disp.setFrameShadow(QtWidgets.QFrame.Raised)
        self.func_disp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.func_disp.setReadOnly(False)
        self.func_disp.setMarkdown("")
        self.func_disp.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.func_disp.setObjectName("func_disp")
        self.tabWidget.addTab(self.Function, "")
        self.global_variable = QtWidgets.QWidget()
        self.global_variable.setObjectName("global_variable")
        self.gloabal_disp = QtWidgets.QTextEdit(self.global_variable)
        self.gloabal_disp.setGeometry(QtCore.QRect(270, 10, 510, 381))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.gloabal_disp.setFont(font)
        self.gloabal_disp.setFrameShape(QtWidgets.QFrame.Box)
        self.gloabal_disp.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gloabal_disp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.gloabal_disp.setReadOnly(False)
        self.gloabal_disp.setMarkdown("")
        self.gloabal_disp.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.gloabal_disp.setObjectName("gloabal_disp")
        self.global_items = QtWidgets.QListWidget(self.global_variable)
        self.global_items.setGeometry(QtCore.QRect(7, 10, 256, 381))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.global_items.setFont(font)
        self.global_items.setFrameShape(QtWidgets.QFrame.Box)
        self.global_items.setFrameShadow(QtWidgets.QFrame.Raised)
        self.global_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.global_items.setObjectName("global_items")
        self.tabWidget.addTab(self.global_variable, "")
        self.struct = QtWidgets.QWidget()
        self.struct.setObjectName("struct")
        self.struct_disp = QtWidgets.QTextEdit(self.struct)
        self.struct_disp.setGeometry(QtCore.QRect(270, 10, 510, 381))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.struct_disp.setFont(font)
        self.struct_disp.setFrameShape(QtWidgets.QFrame.Box)
        self.struct_disp.setFrameShadow(QtWidgets.QFrame.Raised)
        self.struct_disp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.struct_disp.setReadOnly(False)
        self.struct_disp.setMarkdown("")
        self.struct_disp.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.struct_disp.setObjectName("struct_disp")
        self.struct_items = QtWidgets.QListWidget(self.struct)
        self.struct_items.setGeometry(QtCore.QRect(7, 10, 256, 381))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.struct_items.setFont(font)
        self.struct_items.setFrameShape(QtWidgets.QFrame.Box)
        self.struct_items.setFrameShadow(QtWidgets.QFrame.Raised)
        self.struct_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.struct_items.setObjectName("struct_items")
        self.tabWidget.addTab(self.struct, "")
        self.enum = QtWidgets.QWidget()
        self.enum.setObjectName("enum")
        self.enum_disp = QtWidgets.QTextEdit(self.enum)
        self.enum_disp.setGeometry(QtCore.QRect(270, 10, 510, 381))
        self.enum_disp.setMaximumSize(QtCore.QSize(620, 491))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.enum_disp.setFont(font)
        self.enum_disp.setFrameShape(QtWidgets.QFrame.Box)
        self.enum_disp.setFrameShadow(QtWidgets.QFrame.Raised)
        self.enum_disp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.enum_disp.setReadOnly(False)
        self.enum_disp.setMarkdown("")
        self.enum_disp.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.enum_disp.setObjectName("enum_disp")
        self.enum_items = QtWidgets.QListWidget(self.enum)
        self.enum_items.setGeometry(QtCore.QRect(7, 10, 256, 381))
        self.enum_items.setMinimumSize(QtCore.QSize(256, 381))
        self.enum_items.setMaximumSize(QtCore.QSize(256, 491))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.enum_items.setFont(font)
        self.enum_items.setFrameShape(QtWidgets.QFrame.Box)
        self.enum_items.setFrameShadow(QtWidgets.QFrame.Raised)
        self.enum_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.enum_items.setObjectName("enum_items")
        self.tabWidget.addTab(self.enum, "")
        self.macro = QtWidgets.QWidget()
        self.macro.setObjectName("macro")
        self.macro_disp = QtWidgets.QTextEdit(self.macro)
        self.macro_disp.setGeometry(QtCore.QRect(270, 10, 510, 381))
        self.macro_disp.setMinimumSize(QtCore.QSize(510, 381))
        self.macro_disp.setMaximumSize(QtCore.QSize(620, 491))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.macro_disp.setFont(font)
        self.macro_disp.setFrameShape(QtWidgets.QFrame.Box)
        self.macro_disp.setFrameShadow(QtWidgets.QFrame.Raised)
        self.macro_disp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.macro_disp.setReadOnly(False)
        self.macro_disp.setMarkdown("")
        self.macro_disp.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.macro_disp.setObjectName("macro_disp")
        self.macro_items = QtWidgets.QListWidget(self.macro)
        self.macro_items.setGeometry(QtCore.QRect(7, 10, 256, 381))
        self.macro_items.setMinimumSize(QtCore.QSize(256, 381))
        self.macro_items.setMaximumSize(QtCore.QSize(256, 491))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.macro_items.setFont(font)
        self.macro_items.setFrameShape(QtWidgets.QFrame.Box)
        self.macro_items.setFrameShadow(QtWidgets.QFrame.Raised)
        self.macro_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.macro_items.setObjectName("macro_items")
        self.tabWidget.addTab(self.macro, "")
        self.other_function = QtWidgets.QWidget()
        self.other_function.setObjectName("other_function")
        self.pushButton = QtWidgets.QPushButton(self.other_function)
        self.pushButton.setGeometry(QtCore.QRect(280, 180, 221, 91))
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.other_function, "")
        self.mention = QtWidgets.QLabel(self.centralwidget)
        self.mention.setGeometry(QtCore.QRect(78, 832, 711, 28))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.mention.setFont(font)
        self.mention.setFrameShape(QtWidgets.QFrame.Box)
        self.mention.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mention.setText("")
        self.mention.setObjectName("mention")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(10, 830, 61, 30))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CodeAnalyser"))
        self.groupBox.setTitle(_translate("MainWindow", "Discription"))
        self.label_8.setText(_translate("MainWindow", "          This tool is used for the statistical work of the key information of C code and generates the corresponding pseudo-code for each function."))
        self.label_9.setText(_translate("MainWindow", "Developer:yuzhirun Version:1.0"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Discover"))
        self.label.setText(_translate("MainWindow", "Input file:"))
        self.select_bt.setText(_translate("MainWindow", "Select"))
        self.label_6.setText(_translate("MainWindow", "Gloable Variable:"))
        self.label_5.setText(_translate("MainWindow", "Enum:"))
        self.label_2.setText(_translate("MainWindow", "Struct:"))
        self.label_4.setText(_translate("MainWindow", "Global Function:"))
        self.label_7.setText(_translate("MainWindow", "Macro Definition:"))
        self.label_3.setText(_translate("MainWindow", "Local Function:"))
        self.load_bt.setText(_translate("MainWindow", "To load"))
        self.clear_bt.setText(_translate("MainWindow", "Clear"))
        self.func_disp.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\',\'Calibri\',\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\',\'Calibri\';\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Function), _translate("MainWindow", "Function"))
        self.gloabal_disp.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\',\'Calibri\',\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\',\'Calibri\';\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.global_variable), _translate("MainWindow", "Global Variable"))
        self.struct_disp.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\',\'Calibri\',\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\',\'Calibri\';\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.struct), _translate("MainWindow", "Struct"))
        self.enum_disp.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\',\'Calibri\',\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\',\'Calibri\';\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.enum), _translate("MainWindow", "Enum"))
        self.macro_disp.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\',\'Calibri\',\'Calibri\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\',\'Calibri\';\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.macro), _translate("MainWindow", "Macro Definition"))
        self.pushButton.setText(_translate("MainWindow", "RENAMED!"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.other_function), _translate("MainWindow", "other function"))
        self.label_11.setText(_translate("MainWindow", "Prompt:"))
import icon_rc
