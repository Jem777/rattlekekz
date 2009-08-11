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
        self.output=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(0)
        self.userlist=self.Box0.itemAt(0).layout().itemAt(0).widget().widget(1)
        self.input=self.Box0.itemAt(1).layout().itemAt(0).widget()
        self.send=self.Box0.itemAt(1).layout().itemAt(1).widget()
        self.connect(self.send,QtCore.SIGNAL("clicked()"),self.fu)

    def fu(self):
        print "fu"

class rattlekekzLoginTab(rattlekekzBaseTab):
    pass

class rattlekekzPrivTab(rattlekekzBaseTab):
    pass

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