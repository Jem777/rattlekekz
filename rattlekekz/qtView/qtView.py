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

import sys
from PyQt4 import QtGui
import qt4reactor
app = QtGui.QApplication(sys.argv,True)
qt4reactor.install()
from twisted.internet import reactor
from rattlekekz.core.pluginmanager import iterator
from rattlekekz.qtView import tabs

class View(iterator):
    def __init__(self,controller, *args, **kwds):
        self.name,self.version="rattlekekz","0.1 Nullpointer Exception"  # Diese Variablen werden vom View abgefragt
        self.controller=controller
        self.plugins={}
        self.main = QtGui.QMainWindow()
        self.main.setWindowTitle(self.name)
        self.menu=self.main.menuBar()
        self.menu.addMenu("&File") # TODO: add shit
        self.main.setCentralWidget(QtGui.QTabWidget())
        self.tabs=self.main.centralWidget()
        self.tabs.setMovable(True)
        self.tabs.addTab(tabs.rattlekekzBaseTab(),"fu")
        self.tabs.widget(0)._setup()
        self.tabs.addTab(QtGui.QWidget(),"bar")
        self.main.show()

    def finishedReadingConfigfile(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        pass

    def startConnection(self,host,port):
        reactor.connectSSL(host, port, self.controller.model, self.controller.model)
        reactor.run()

    def connectionLost(self,reason):
        pass

    def successLogin(self,nick,status,room):
        pass

    def successRegister(self):
        pass

    def successNewPassword(self):
        pass

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        pass

    def successNewProfile(self):
        pass

    def securityCheck(self, infotext):
        pass

    def receivedPing(self,deltaPing):
        pass

    def printMsg(self,nick,msg,channel,status):
        pass

    def gotException(self, message):
        pass

    def listUser(self,room,users):
        pass

    def meJoin(self,room,background):
        pass

    def mePart(self,room):
        pass

    def meGo(self,oldroom,newroom):
        pass

    def newTopic(self,room,topic):
        pass

    def loggedOut(self):
        pass

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        self.iterPlugins('sendBullshit',["".join(map(self.blubb,'_a`\x90\x8cc^b\\\\d\x8d\x8d^\x8e\x8d``\x90\x8f]]c_]b\x91b\x8dd^\x8c_\x8e\x91\x91__\x8c\x91'))])

    def receivedInformation(self,info):
        pass

    def receivedWhois(self,nick,array):
        pass

    def MailInfo(self,info):
        pass

    def receivedMails(self,userid,mailcount,mails):
        pass

    def printMail(self,user,date,mail):
        pass

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)


if __name__=="__main__": # TODO: Make this right
    server="kekz.net"
    from rattlekekz.core import controller
    controllerRattleKekz.Kekzcontroller(View).startConnection(server,23002)