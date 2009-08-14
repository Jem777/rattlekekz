#!/usr/bin/env python
# -*- coding: utf-8 -*-

copyright = """
    Copyright 2008, 2009 Moritz Doll and Christian Scharkus

    This file is part of rattlekekz.

    rattlekekz is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    rattlekekz is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with rattlekekz.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
import re

class rattlekekzBaseTab(QtGui.QWidget):
    def _setup(self):
        pass

    def fu(self):
        print "fu"

class rattlekekzLoginTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        self.Box = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight,self)
        self.Box.addWidget(QtGui.QListView())
        Form = QtGui.QFormLayout()
        Form.addRow("Nickname",QtGui.QLineEdit())
        Form.addRow("Passwort",QtGui.QLineEdit())
        Form.addRow(u"Räume",QtGui.QLineEdit())
        Form.addRow(QtGui.QPushButton("&Login"))
        self.Box.addLayout(Form)
        self.Box.itemAt(0).widget().setModel(QtGui.QStringListModel())
        self.roomList = self.Box.itemAt(0).widget().model()
        self.nickInput = self.Box.itemAt(1).layout().itemAt(1).widget() # QLineEdit
        self.passInput = self.Box.itemAt(1).layout().itemAt(3).widget() # QLineEdit
        self.roomInput = self.Box.itemAt(1).layout().itemAt(5).widget() # QLineEdit
        self.loginButton = self.Box.itemAt(1).layout().itemAt(6).widget() # QPushButton
        self.passInput.setEchoMode(QtGui.QLineEdit.Password)
        self.loginButton.setDisabled(True)

    def receivedPreLoginData(self,rooms,array):
        self.loginButton.setEnabled(True)
        list=[]
        for i in rooms:
            list.append(i["name"]+" ("+str(i["users"])+"/"+str(i["max"])+")")
        self.roomList.setStringList(list)

class rattlekekzPrivTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        Box1 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box1.addWidget(QtGui.QSplitter())
        Box1.itemAt(0).widget().addWidget(QtGui.QTextBrowser())
        Box1.itemAt(0).widget().addWidget(QtGui.QListView())
        self.Box0.addLayout(Box1)
        Box2 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box2.addWidget(QtGui.QLineEdit())
        Box2.addWidget(QtGui.QPushButton("&Send"))
        self.Box0.addLayout(Box2)
        self.output=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(0) # QTextbrowser
        self.userlist=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(1) # QListView
        self.input=self.Box0.itemAt(1).layout().itemAt(0).widget() # QLineEdit TODO: May replace with QTextEdit
        self.send=self.Box0.itemAt(1).layout().itemAt(1).widget() # QPushButton
        self.connect(self.send,QtCore.SIGNAL("clicked()"),self.sendStr)
        self.connect(self.input,QtCore.SIGNAL("returnPressed()"),self.sendStr)

    def sendStr(self):
        if self.input.hasAcceptableInput():
            input = str(self.input.text())
            self.parent.sendStr(self.room,input)

class rattlekekzMsgTab(rattlekekzPrivTab):
    pass

class rattlekekzMailTab(rattlekekzBaseTab):
    pass

class rattlekekzInfoTab(rattlekekzBaseTab):
    pass

class rattlekekzSecureTab(rattlekekzBaseTab):
    pass

class rattlekekzEditTab(rattlekekzBaseTab):
    pass