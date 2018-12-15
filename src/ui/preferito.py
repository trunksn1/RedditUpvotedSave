# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferito.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(335, 462)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(11, 11, 264, 16))
        self.label.setObjectName("label")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10, 38, 311, 401))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.subEdit = QtWidgets.QLineEdit(self.widget)
        self.subEdit.setObjectName("subEdit")
        self.horizontalLayout.addWidget(self.subEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.subscelteColonne = QtWidgets.QColumnView(self.widget)
        self.subscelteColonne.setObjectName("subscelteColonne")
        self.verticalLayout.addWidget(self.subscelteColonne)
        self.CreaButton = QtWidgets.QCommandLinkButton(self.widget)
        self.CreaButton.setObjectName("CreaButton")
        self.verticalLayout.addWidget(self.CreaButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600; font-style:italic;\">Crea una nuova raccolta di sub preferite</span></p></body></html>"))
        self.label_2.setText(_translate("Form", "Sub da aggiungere"))
        self.CreaButton.setText(_translate("Form", "Finito"))

