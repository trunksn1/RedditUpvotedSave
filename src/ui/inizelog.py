# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'inizelog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(180, 140)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(180, 140))
        Dialog.setMaximumSize(QtCore.QSize(200, 160))
        self.logButton = QtWidgets.QPushButton(Dialog)
        self.logButton.setGeometry(QtCore.QRect(50, 110, 75, 23))
        self.logButton.setObjectName("logButton")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(20, 5, 135, 95))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.us_label = QtWidgets.QLabel(self.widget)
        self.us_label.setObjectName("us_label")
        self.verticalLayout.addWidget(self.us_label)
        self.userEdit = QtWidgets.QLineEdit(self.widget)
        self.userEdit.setObjectName("userEdit")
        self.verticalLayout.addWidget(self.userEdit)
        self.pass_label = QtWidgets.QLabel(self.widget)
        self.pass_label.setObjectName("pass_label")
        self.verticalLayout.addWidget(self.pass_label)
        self.passEdit = QtWidgets.QLineEdit(self.widget)
        self.passEdit.setEnabled(True)
        self.passEdit.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.passEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passEdit.setObjectName("passEdit")
        self.verticalLayout.addWidget(self.passEdit)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Collega Redditor"))
        self.logButton.setText(_translate("Dialog", "LogIn"))
        self.us_label.setText(_translate("Dialog", "Redditor Username"))
        self.pass_label.setText(_translate("Dialog", "Password"))

