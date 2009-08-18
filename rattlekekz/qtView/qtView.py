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

#twisted/qt
from PyQt4 import QtGui,QtCore
import qt4reactor
app = QtGui.QApplication(sys.argv,True)
qt4reactor.install()
from twisted.internet import reactor

from rattlekekz.core.pluginmanager import iterator
from rattlekekz.qtView.tabs import *
from rattlekekz.qtView.tabmanagement import TabManager

class View(TabManager,iterator):
    def __init__(self,controller, *args, **kwds):
        self.name,self.version="rattlekekz","0.1 Nullpointer Exception"  # Diese Variablen werden vom View abgefragt
        self.controller=controller
        self.kwds=kwds# List of Arguments e.g. if Userlist got colors.
        TabManager.__init__(self)
        self.blubb=lambda x:chr(ord(x)-43)
        self.plugins={}
        self.main = QtGui.QMainWindow()
        self.main.setWindowTitle(self.name)
        self.menu=self.main.menuBar()
        self.menu.addMenu("&File") # TODO: add shit
        self.main.setCentralWidget(QtGui.QTabWidget())
        self.tabs=self.main.centralWidget()
        self.tabs.setMovable(True)
        self.addTab("$login",rattlekekzLoginTab)
        self.changeTab("$login")
        #self.tabs.addTab(rattlekekzBaseTab(),"fu")
        #self.tabs.widget(0)._setup()
        #self.tabs.addTab(QtGui.QWidget(),"bar")
        self.main.show()
        self.smilies={"s6":":-)",
                 "s4":":-(",
                 "s1":":-/",
                 "s8":"X-O",
                 "s7":"(-:",
                 "s9":"?-|",
                 "s10":"X-|",
                 "s11":"8-)",
                 "s2":":-D",
                 "s3":":-P",
                 "s5":";-)",
                 "sxmas":"o:)",
                 "s12":":-E",
                 "s13":":-G"}
        self.colors={"red":"FF0000",
                     "blue":"020285",
                     "green":"015401",
                     "gray":"696969",
                     "cyan":"00FFFF",
                     "magenta":"FF00FF",
                     "orange":"FFA500",
                     "pink":"FFC0CB",
                     "yellow":"FFFF00",
                     "normal":"000000",
                     "normalaway":"696969",
                     "greenaway":"215421",
                     "blueaway":"222285",
                     "yellowaway":"FFA500",
                     "redaway":"FF2020"}

    def deparse(self,msg):
        text,format=self.controller.decode(msg)
        msg=[]
        self.fontTag=False
        for i in range(len(text)):
            text[i]="&amp;".join(text[i].split("&"))
            text[i]="&lt;".join(text[i].split("<"))
            text[i]="&gt;".join(text[i].split(">"))
            if format[i] == "newline":
                msg.append("<br>")
                continue
            if format[i] == "hline":
                msg.append("<hr>")
                continue
            if format[i] == "imageurl":
                msg.append(("<img src="+text[i]+">"))
                continue
            if len(format[i]) > 1:
                if format[i][0] == "ownnick":
                    if not "green" in format[i][1]:
                        color = "green"
                    else:
                        color = "blue"
                    if self.fontTag:
                        msg.append("</font><font color='#"+self.colors[color]+"'>"+text[i])
                    else:
                        msg.append("<font color='#"+self.colors[color]+"'>"+text[i])
                        self.fontTag=True
                    continue
            #if text[i].isspace() or text[i]=="":   # NOTE: If there are any bugs with new rooms and the roomop-message THIS could be is the reason ;)
            #    continue                           # 
            if text[i] == "":                       #
                continue                            #
            form=format[i].split(",")
            color=""
            font="<span>"
            for a in form:
                if a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow","white","reset"]:
                    if a != "reset":
                        color=a
                    else:
                        color="reset"
                if a == "bold":
                    font="<b>"
                if a == "italic":
                    font="<i>"
                if a == "sb":
                    text[i]="<img src='http://kekz.net/forum/Smileys/default/"+text[i]+".png'>" # TODO: fetch this stuff
                if a == "button":
                    color=""
                    font="<a>"
                    text[i] = "["+text[i]+"]"
            if color != "":
                if self.fontTag:
                    msg.append("</font><font color='#"+self.colors[color]+"'>"+font+text[i]+font[:1]+"/"+font[1:])
                else:
                    msg.append("<font color='#"+self.colors[color]+"'>"+font+text[i]+font[:1]+"/"+font[1:])
                    self.fontTag=True
            else:
                msg.append(font+text[i]+font[:1]+"/"+font[1:])
            #for i in range(len(msg)):
            #    if type(msg[i][1]) is unicode:
            #        msg[i] = (msg[i][0],msg[i][1].encode("utf_8"))
            ##self.lookupRooms[room].addLine(color)    #they are just for debugging purposes, but don't delete them
            ##self.lookupRooms[room].addLine(text[i])
        #for i in range(len(msg)): # TODO: Add real parsing
        #    msg[i]=msg[i][1]
        if self.fontTag:
            msg.append("</font>")
        return msg

    def stringHandler(self,string,return_utf8=False):
        if type(string) is list:
            result=[]
            for i in string:
                if return_utf8 == False:
                    try:
                        i=str(i)
                    except UnicodeEncodeError:
                        i=unicode(i).encode("utf_8")
                    result.append(i)
                else:
                    try:
                        i=unicode(i)
                    except UnicodeDecodeError:
                        i=str(i).decode("utf_8")
                    result.append(i)
            return result
        else:
            if return_utf8 == False:
                try:
                    return str(string)
                except UnicodeEncodeError:
                    string=unicode(string)
                    return string.encode("utf_8")
            else:
                try:
                    return unicode(string)
                except UnicodeDecodeError:
                    string=str(string)
                    return string.decode("utf_8")

    def finishedReadingConfigfile(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        self.isConnected=True
        self.getTab(self.ShownRoom).receivedPreLoginData(rooms,array)

    def startConnection(self,host,port):
        reactor.connectSSL(host, port, self.controller.model, self.controller.model)
        reactor.run()

    def addRoom(self,room,tab):
        tablist={"ChatRoom":rattlekekzMsgTab,"PrivRoom":rattlekekzPrivTab,"InfoRoom":rattlekekzInfoTab,"MailRoom":rattlekekzMailTab,"SecureRoom":rattlekekzSecureTab,"EditRoom":rattlekekzEditTab}
        self.addTab(room,tablist[tab])

    def sendLogin(self, nick, passwd, room):
        self.iterPlugins('sendLogin', [nick, passwd, room])

    def connectionLost(self,reason):
        pass

    def connectionFailed(self):
        print "fail!"

    def successLogin(self,nick,status,room):
        self.nickname=nick
        self.ShownRoom=room
        self.addTab(room,rattlekekzMsgTab)
        self.changeTab(room)
        self.delTab("$login")

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

    def printMsg(self,room,msg):
        self.getTab(room).addLine("".join(msg))

    def gotException(self, message):
        pass

    def listUser(self,room,users):
        self.getTab(room).listUser(users,self.kwds['usercolors'])

    def meJoin(self,room,background):
        self.addTab(room,rattlekekzMsgTab)
        if not background:
            self.changeTab(room)

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

    def sendStr(self,channel,string):
        self.iterPlugins('sendStr', [channel, string])

    def timestamp(self, string):
        return string

    def colorizeText(self, color, text):
        return text

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)


if __name__=="__main__": # TODO: Make this right
    server="kekz.net"
    from rattlekekz.core import controller
    controllerRattleKekz.Kekzcontroller(View).startConnection(server,23002)