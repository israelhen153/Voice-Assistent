# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QLabel, QListWidgetItem, QPushButton


class fileDisplay(object):
    def __init__(self, filesList):
        self.app = QApplication([__file__])
        self.Form = QWidget()
        self.Form.setObjectName("Form")
        self.Form.resize(410, 331)
        self.FoundFile = QLabel(self.Form)
        self.SubmitButton = QPushButton(self.Form)
        self.listWidget = QListWidget(self.Form)
        self.setupUi()
        self.populateListWidget(filesList)
        self.Form.show()

    def setupUi(self):
        self.FoundFile.setGeometry(QtCore.QRect(10, 10, 271, 21))
        self.FoundFile.setObjectName("FoundFile")
        self.SubmitButton.setGeometry(QtCore.QRect(160, 280, 103, 36))
        self.SubmitButton.setObjectName("SubmitButton")
        self.SubmitButton.clicked.connect(self.getSelectedRecord)
        self.listWidget.setGeometry(QtCore.QRect(0, 50, 401, 211))
        self.listWidget.setObjectName("listWidget")
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(self.Form)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Form.setWindowTitle(_translate("Form", "Choose a file to open"))
        self.FoundFile.setText(_translate("Form", "Please choose one of the Located Files:"))
        self.SubmitButton.setText(_translate("Form", "submit"))

    def populateListWidget(self, listInput):
        """
            This function files the list widget with the paths from which the user
            chooses the one file he wants to open
        :param listInput:
        :return: None
        """

        if listInput != "":
            for item in listInput:
                self.listWidget.addItem(QListWidgetItem(str(item)))

    def getSelectedRecord(self):
        try:
            self.Form.close()
            self.wantedRecord = self.listWidget.selectedItems()[0].text()
        except Exception as error:
            self.wantedRecord = ""

    def getUsersChoise(self):
        self.app.exec_()
        return self.wantedRecord
