# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tips.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ico/.imgs/灯泡提示.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(8, 90, 384, 201))
        self.listWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.listWidget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.listWidget.setGridSize(QtCore.QSize(0, 25))
        self.listWidget.setModelColumn(0)
        self.listWidget.setObjectName("listWidget")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(19, 20, 31, 31))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/ico/.imgs/灯泡提示.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(60, 20, 311, 51))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Tips"))
        self.label_2.setText(_translate("Form", "There are possibly some variables that are global variables, but they do not adhere to the coding conventions."))
import icon_rc
