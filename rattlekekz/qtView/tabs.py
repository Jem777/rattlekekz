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
        self.roomView = self.Box.itemAt(0).widget()
        self.roomView.setModel(QtGui.QStringListModel())
        self.roomView.setEditTriggers(self.roomView.NoEditTriggers)
        self.roomView.setSelectionMode(self.roomView.NoSelection)
        self.roomView.setDragDropMode(self.roomView.NoDragDrop)
        self.roomView.setAlternatingRowColors(True)
        self.roomList = self.Box.itemAt(0).widget().model() # QStringListModel
        self.nickInput = self.Box.itemAt(1).layout().itemAt(1).widget() # QLineEdit
        self.passInput = self.Box.itemAt(1).layout().itemAt(3).widget() # QLineEdit
        self.roomInput = self.Box.itemAt(1).layout().itemAt(5).widget() # QLineEdit
        self.loginButton = self.Box.itemAt(1).layout().itemAt(6).widget() # QPushButton
        self.passInput.setEchoMode(QtGui.QLineEdit.Password)
        self.loginButton.setDisabled(True)
        self.connect(self.loginButton,QtCore.SIGNAL("clicked()"),self.sendLogin)

    def receivedPreLoginData(self,rooms,array):
        self.loginButton.setEnabled(True)
        list=[]
        for i in rooms:
            list.append(i["name"]+" ("+str(i["users"])+"/"+str(i["max"])+")")
        self.roomList.setStringList(list)

    def sendLogin(self):
        nick,password,rooms=self.parent.stringHandler([self.nickInput.text(),self.passInput.text(),self.roomInput.text()])
        self.parent.sendLogin(nick,password,rooms)

class rattlekekzPrivTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(QtGui.QTextEdit())
        Box2 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box2.addWidget(QtGui.QLineEdit())
        Box2.addWidget(QtGui.QPushButton("&Send"))
        self.Box0.addLayout(Box2)
        self.output=self.Box0.itemAt(0).widget() # QTextEdit
        self.output.setReadOnly(True)
        self.input=self.Box0.itemAt(1).layout().itemAt(0).widget() # QLineEdit TODO: May replace with QTextEdit
        self.send=self.Box0.itemAt(1).layout().itemAt(1).widget() # QPushButton
        self.connect(self.send,QtCore.SIGNAL("clicked()"),self.sendStr)
        self.connect(self.input,QtCore.SIGNAL("returnPressed()"),self.sendStr)

    def sendStr(self):
        if self.input.hasAcceptableInput():
            input = self.parent.stringHandler(self.input.text())
            self.parent.sendStr(self.parent.stringHandler(self.room),input)
            self.input.setText("")

    def addLine(self,msg):
        self.output.append(self.parent.stringHandler(msg,True))

class rattlekekzMsgTab(rattlekekzPrivTab):
    def _setup(self,room,parent):
        rattlekekzPrivTab._setup(self,room,parent)
        Box1 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box1.addWidget(QtGui.QSplitter())
        Box1.itemAt(0).widget().addWidget(QtGui.QTextEdit())
        Box1.itemAt(0).widget().addWidget(QtGui.QListView())
        self.Box0.insertLayout(0,Box1)
        self.Box0.removeWidget(self.output)
        self.userView = self.Box0.itemAt(0).layout().itemAt(0).widget().widget(1)
        self.userView.setModel(QtGui.QStringListModel())
        self.userView.setEditTriggers(self.userView.NoEditTriggers)
        #self.userView.setSelectionMode(self.roomView.NoSelection)
        self.userView.setDragDropMode(self.userView.NoDragDrop)
        #self.roomView.setAlternatingRowColors(True)
        self.userList=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(1).model() # QStringListModel
        self.output=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(0) # QTextEdit
        self.output.setReadOnly(True)

    def listUser(self,users,color=True): # TODO: Move to MsgTab
        """takes a list of users and updates the Userlist of the room"""
        self.completion=[]
        new=[]
        self.userList.removeRows(0,self.userList.rowCount())
        #if color is True: # TODO: Add color parsing
        #    for i in users:
        #        self.completion.append(i[0])
        #        if i[2] in 'x':
        #            self.color='normal'
        #        elif i[2] in 's':
        #            self.color='green'
        #        elif i[2] in 'c':
        #            self.color='blue'
        #        elif i[2] in 'o':
        #            self.color='yellow'
        #        elif i[2] in 'a':
        #            self.color='red'
        #        if i[1] == True:
        #            self.color=self.color+'away'
        #            self.Userlistarray.append(urwid.Text((self.color,'('+i[0]+')')))
        #        else:
        #            self.Userlistarray.append(urwid.Text((self.color,i[0])))
        #else:
        if True:
            for i in users:
                self.completion.append(i[0])
                if i[2] in 'x':
                    self.color=' '
                elif i[2] in 's':
                    self.color='~'
                elif i[2] in 'c':
                    self.color='$'
                elif i[2] in 'o':
                    self.color='@'
                elif i[2] in 'a':
                    self.color='%'
                if i[1] == True:
                    i[0] = '('+i[0]+')'
                new.append(self.color+i[0])
        new = self.parent.stringHandler(new,True)
        self.userList.setStringList(new)

class rattlekekzMailTab(rattlekekzBaseTab):
    pass

class rattlekekzInfoTab(rattlekekzBaseTab):
    pass

class rattlekekzSecureTab(rattlekekzBaseTab):
    pass

class rattlekekzEditTab(rattlekekzBaseTab):
    pass