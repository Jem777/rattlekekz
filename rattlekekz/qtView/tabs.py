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

from PyQt4 import QtCore,QtGui
import re

class rattlekekzBaseTab(QtGui.QWidget):
    def _setup(self,room,parent):
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
        Form.addRow("Password",QtGui.QLineEdit())
        Form.addRow("Rooms",QtGui.QLineEdit())
        Form.addRow(QtGui.QPushButton("&Login"),QtGui.QPushButton("&Register"))
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
        self.registerButton = self.Box.itemAt(1).layout().itemAt(7).widget() # QPushButton
        self.passInput.setEchoMode(QtGui.QLineEdit.Password)
        self.loginButton.setDisabled(True)
        self.connect(self.loginButton,QtCore.SIGNAL("clicked()"),self.sendLogin)
        self.connect(self.registerButton,QtCore.SIGNAL("clicked()"),self.registerNick)

    def receivedPreLoginData(self,rooms,array):
        self.loginButton.setEnabled(True)
        list=[]
        for i in rooms:
            list.append(i["name"]+" ("+str(i["users"])+"/"+str(i["max"])+")")
        self.roomList.setStringList(list)

    def sendLogin(self):
        nick,password,rooms=self.parent.stringHandler([self.nickInput.text(),self.passInput.text(),self.roomInput.text()])
        self.parent.sendLogin(nick,password,rooms)

    def registerNick(self):
        self.parent.addTab("$register",rattlekekzRegTab)
        self.parent.changeTab("$register")

class rattlekekzRegTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        self.Form = QtGui.QFormLayout(self)
        self.Form.addRow("Nickname",QtGui.QLineEdit())
        self.Form.addRow("Password",QtGui.QLineEdit())
        self.Form.addRow("Password",QtGui.QLineEdit())
        self.Form.addRow("E-Mail",QtGui.QLineEdit())
        self.Form.addRow(QtGui.QPushButton("&Register"))
        self.nickInput = self.Form.itemAt(1).widget() # QLineEdit
        self.passwordInput = self.Form.itemAt(3).widget() # QLineEdit
        self.passwordCheck = self.Form.itemAt(5).widget() # QLineEdit
        self.mailInput = self.Form.itemAt(7).widget() # QLineEdit
        self.registerButton = self.Form.itemAt(8).widget() # QPushButton
        self.connect(self.registerButton,QtCore.SIGNAL("clicked()"),self.registerNick)

    def registerNick(self):
        if self.passwordInput.text() == self.passwordCheck.text():
            nick,passwd,mail = map(lambda x: x.strip(),self.parent.stringHandler([self.nickInput.text(),self.passwordInput.text(),self.mailInput.text()]))
            if nick != "" != mail:
                self.parent.registerNick(nick,passwd,mail)
                print "STUB: register nick"
            else:
                print "STUB: Nick or Mail empty"
        else:
            "STUB: Passwords not matching"

class rattlekekzPrivTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(QtGui.QTextBrowser())
        Box2 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box2.addWidget(QtGui.QLineEdit())
        Box2.addWidget(QtGui.QPushButton("&Send"))
        self.Box0.addLayout(Box2)
        self.output=self.Box0.itemAt(0).widget() # QTextBrowser
        self.output.setReadOnly(True)
        self.output.setHtml(u"")
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
        self.room,self.parent=room,parent
        self.Box0 = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        self.Box0.addWidget(QtGui.QLineEdit())
        Box1 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        Box1.addWidget(QtGui.QSplitter())
        Box1.itemAt(0).widget().addWidget(QtGui.QTextBrowser())
        Box1.itemAt(0).widget().addWidget(QtGui.QListView())
        self.Box0.addLayout(Box1)
        Box2 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        class QLineEdit(QtGui.QLineEdit):
            def event(self,event):
                event.setAccepted(True)
                if event.type() != QtCore.QEvent.KeyPress:
                    return QtGui.QLineEdit.event(self,event)
                elif QtCore.Qt.Key_Backtab != event.key() != QtCore.Qt.Key_Tab:
                    return self.keyPressEvent(event)
                elif event.key() == QtCore.Qt.Key_Tab:
                    self.emit(QtCore.SIGNAL("tabPressed()"))
                    return True
        Box2.addWidget(QLineEdit())
        Box2.addWidget(QtGui.QPushButton("&Send"))
        self.Box0.addLayout(Box2)
        self.userView = self.Box0.itemAt(1).layout().itemAt(0).widget().widget(1)
        self.userView.setModel(QtGui.QStringListModel())
        self.userView.setEditTriggers(self.userView.NoEditTriggers)
        #self.userView.setSelectionMode(self.roomView.NoSelection)
        self.userView.setDragDropMode(self.userView.NoDragDrop)
        #self.roomView.setAlternatingRowColors(True)
        self.topicLine=self.Box0.itemAt(0).widget() # QLineEdit
        self.userList=self.Box0.itemAt(1).layout().itemAt(0).widget().widget(1).model() # QStringListModel
        self.output=self.Box0.itemAt(1).layout().itemAt(0).widget().widget(0) # QTextBrowser
        self.output.setReadOnly(True)
        self.output.setHtml(u"")
        self.input=self.Box0.itemAt(2).layout().itemAt(0).widget() # QLineEdit TODO: May replace with QTextEdit
        #self.input.setCompleter(QtGui.QCompleter())
        #self.input.completer().setModel(QtGui.QStringListModel())
        #self.input.completer().setCompletionMode(QtGui.QCompleter.InlineCompletion)
        #self.input.completer().setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.send=self.Box0.itemAt(2).layout().itemAt(1).widget() # QPushButton
        self.connect(self.send,QtCore.SIGNAL("clicked()"),self.sendStr)
        self.connect(self.input,QtCore.SIGNAL("tabPressed()"),self.complete)
        self.connect(self.input,QtCore.SIGNAL("returnPressed()"),self.sendStr)

    def listUser(self,users,color=True):
        """takes a list of users and updates the Userlist of the room"""
        self.completion=[]
        new=[]
        self.userList.removeRows(0,self.userList.rowCount())
        #if color: # TODO: Add color parsing
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
        #            new.append("<font color='#"+self.parent.colors[self.color]+"'>("+i[0]+")</font>")
        #        else:
        #            new.append("<font color='#"+self.parent.colors[self.color]+"'>"+i[0]+"</font>")
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
                if i[1]:
                    new.append(self.color+"("+i[0]+")")
                else:
                    new.append(self.color+i[0])
        new = self.parent.stringHandler(new,True)
        self.userList.setStringList(new)
        #self.input.completer().model().setStringList(self.completion)

    def complete(self):
        at=False
        input = self.parent.stringHandler(self.input.text())
        input,crap=input[:self.input.cursorPosition()].split(),input[self.input.cursorPosition():]
        if len(input) is not 0:
            nick = input.pop().lower()
            if nick.startswith("@"):
                nick = nick[1:]
                at=True
            solutions=[]
            newInput = nick
            if nick != "":
                for i in self.completion:
                    if nick in str(i[:len(nick)]).lower():
                        solutions.append(i)
                if len(solutions) != 0 and len(solutions) != 1:
                    solutions.sort(key=lambda x: len(x))
                    for x in range(len(solutions[0])):
                        if solutions[0][x] != solutions[1][x]:
                            break
                        else:
                            newInput=solutions[0][:x+1]
                    if at:
                        newInput="@"+newInput
                    input.append(str(newInput))
                    self.input.setText(self.parent.stringHandler(" ".join(input)+crap,True))
                    self.input.setCursorPosition(len(self.input.text())-len(crap))
                    self.addLine(" ".join(solutions))
                elif len(solutions) is not 0:
                    if at:
                        solutions[0]="@"+solutions[0]
                    input.append(str(solutions[0]))
                    if len(input) is not 1:
                        self.input.setText(self.parent.stringHandler(" ".join(input)+" "+crap,True))
                    else:
                        self.input.setText(self.parent.stringHandler(" ".join(input)+", "+crap,True))
                    self.input.setCursorPosition(len(self.input.text())-len(crap))

    def newTopic(self,topic):
        self.topicLine.setText(self.parent.stringHandler(topic,True))
        self.addLine(self.parent.stringHandler("Topic: "+topic,True))

class rattlekekzMailTab(rattlekekzBaseTab):
    pass

class rattlekekzInfoTab(rattlekekzBaseTab):
    def _setup(self,room,parent):
        self.room,self.parent=room,parent
        Box = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom,self)
        Box.addWidget(QtGui.QTextEdit())
        self.output = Box.itemAt(0).widget()
        self.output.setHtml("")
        self.output.setReadOnly(True)

    def addLine(self,msg):
        self.output.append(self.parent.stringHandler(msg,True))

class rattlekekzSecureTab(rattlekekzBaseTab):
    pass

class rattlekekzEditTab(rattlekekzBaseTab):
    pass