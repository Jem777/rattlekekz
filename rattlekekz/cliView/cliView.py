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

revision = "$Revision$"

# rattlekekz
from rattlekekz.cliView.tabmanagement import TabManager
from rattlekekz.cliView.tabs import *

# System
import sys, subprocess, time
from re import search

# Urwid
import urwid

# Twisted
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.task import LoopingCall
rev=search("\d+",revision).group()


class TextTooLongError(Exception):
    pass

class View(TabManager):
    def __init__(self, controller, *args, **kwds):
        TabManager.__init__(self)
        sys.stdout.write('\033]0;rattlekekz\007') # TODO: some more maybe?
        self.revision=rev
        self.ShownRoom=None
        self.Ping=""
        self.nickname=""
        self.controller=controller
        self.vargs = args
        self.kwds=kwds# List of Arguments e.g. if Userlist got colors.
        self.plugins={}
        self.name,self.version="rattlekekz","0.1 Beta 'Nullpointer-Exception'"
        colors =[('normal','default','default'),
            ('divider', 'white', 'dark blue'),
            ('divideryellow', 'yellow', 'dark blue'),
            ('dividerstate', 'light gray', 'dark blue'),
            ('dividerme', 'light red', 'dark blue'),

            ('red','light red','default'),  #admin
            ('yellow','yellow','default'),  #chatop
            ('blue','light blue','default'), #roomop
            ('green','light green','default'), #special
            ('redaway','dark red','default'),
            ('yellowaway','brown','default'),
            ('blueaway','dark blue','default'),
            ('greenaway','dark green','default'),
            ('normalaway','light gray','default'),
            ("timestamp","dark green","default"), #time
            ("magenta","light magenta","default"),
            ("cyan","light cyan","default"),
            ("orange","brown","default"),
            ("pink","light magenta","default"),
            ("white","white","default"),
            ('gray','light gray','default'),
            ('smilie','black','brown')]

        bold=[('normalbold','default,bold','default'),#,'bold'),
            ('redbold','light red,bold','default','bold'),  #admin
            ('yellowbold','yellow,bold','default','bold'),  #chatop
            ('bluebold','light blue,bold','default','bold'), #roomop
            ('greenbold','light green,bold','default','bold'), #special
            ("magentabold","light magenta,bold","default",'bold'),
            ("cyanbold","light cyan,bold","default",'bold'),
            ("orangebold","brown,bold","default",'bold'),
            ("pinkbold","light magenta,bold","default",'bold'),
            ("whitebold","white,bold","default",'bold'),
            ('graybold','light gray,bold','default',"bold")]
        nobold=[('normalbold','default','default'),
            ('redbold','light red','default'),
            ('yellowbold','yellow','default'),
            ('bluebold','light blue','default'),
            ('greenbold','light green','default'),
            ("magentabold","light magenta","default"),
            ("cyanbold","light cyan","default"),
            ("orangebold","brown","default"),
            ("pinkbold","light magenta","default"),
            ("whitebold","white","default"),
            ('graybold','light gray','default')]
        try:
            self.tui.register_palette(colors+bold)
        except:
            self.tui.register_palette(colors+nobold)
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
        reactor.addReader(self)
        reactor.callWhenRunning(self.init)
        self.oldtime=""
        self.isConnected=False


    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self): # TODO: is this needed?
        return 'rattlekekz'

    def init(self):
        self.blubb=lambda x:chr(ord(x)-43)
        self.size = self.tui.get_cols_rows()
        self.writehistory=self.controller.writehistory # TODO: Find some way to handle variables with plugin-system
        self.readhistory=self.controller.readhistory
        if self.controller.configfile.has_key("sorttabs") and self.controller.configfile["sorttabs"] in ("True","1","yes"):
            self.sortTabs=True
        self.addTab("$login",rattlekekzLoginTab)
        self.changeTab("$login")

    def suspendView(self):
        self.tui.stop()
        fubar = subprocess.call("links www.google.de", shell=True)
        self.tui.start()

    def startConnection(self,server,port):
        reactor.connectSSL(server, port, self.controller.model, self.controller.model)
        self.tui.run_wrapper(reactor.run)

    def addRoom(self,room,tab):
        tablist={"ChatRoom":rattlekekzMsgTab,"PrivRoom":rattlekekzPrivTab,"InfoRoom":rattlekekzInfoTab,"MailRoom":rattlekekzMailTab,"SecureRoom":rattlekekzSecureTab,"EditRoom":rattlekekzEditTab}
        self.addTab(room,tablist[tab])

    def setTitle(self):
        highlight=0
        for i in self.lookupRooms:
            if i[2]>highlight:
                highlight=i[2]
        if highlight==0 or highlight==1:
            prefix=""
        elif highlight==2:
            prefix="[+] "
        else:
            prefix="[*] "
        sys.stdout.write('\033]0;'+prefix+self.name+' - '+self.ShownRoom+' \007')

    def changeTab(self,tabname):
        TabManager.changeTab(self,tabname)
        self.setTitle()
        if not self.ShownRoom == None:
            self.getTab(self.ShownRoom).clock(self.time)
            self.redisplay()

    def doRead(self):
        """ Input is ready! """
        if self.ShownRoom != None:
            keys = self.tui.get_input()
            for key in keys:
                if key == 'window resize':
                    self.size = self.tui.get_cols_rows()
                    for i in self.lookupRooms:
                        try:
                            i[1].newTopic(i[1].Topictext)
                        except:
                            pass
                    self.redisplay()
                elif key == "ctrl n" or key=="ctrl p":
                    array=self.lookupRooms
                    index=self.getTabId(self.ShownRoom)
                    if len(array)==2:
                        pass
                    elif array[index]==array[-1] and key=="ctrl n":
                        index=1
                    elif key=="ctrl n":
                        index=index+1
                    elif array[index]==array[0] or array[index]==array[1] :
                        index=-1
                    else:
                        index=index-1
                    self.changeTab(self.lookupRooms[index][0])
                else:
                    self.getTab(self.ShownRoom).onKeyPressed(self.size, key)
            self.redisplay()

    def hiThere(self,name,instance):
        """method for plugins to say "hi there" :D"""
        if not self.plugins.has_key(name):
            self.plugins[name]=instance
            return (self,0,"plugin registered")
        else:
            return (self,1,"the plugin or another instance of it is allready registered")

    def outHere(self,name,instance):
        """method for plugins to get the hell out of here"""
        if self.plugins.has_key(name):
            if self.plugins[name] is instance:
                del self.plugins[name]
            else:
                self.controller.gotException("instance don't match registered plugin") # This should never occure ;)

    def iterPlugins(self,method,kwds=[]):
        taken,handled=False,False
        for i in self.plugins:
            try:
                value = getattr(self.plugins[i], method)(self,*kwds)
                if value is 'handled':
                    handled=True
                    break
                elif value is 'taken':
                    taken=True
                    continue
            except AttributeError:
                pass # TODO: May add some message or so.
            except:
                pass # TODO: add message for error in plugin xy
        if not handled:
            getattr(self.controller, method)(*kwds)

    def receivedPreLoginData(self,rooms,array):
        self.isConnected=True
        self.getTab(self.ShownRoom).receivedPreLoginData(rooms,array)

    def successLogin(self,nick,status,room):
        self.nickname=nick
        self.ShownRoom=room
        self.addTab(room,rattlekekzMsgTab)
        self.changeTab(room)
        self.delTab("$login")


    def successRegister(self):
        if len(self.lookupRooms)==1:
            self.addTab("$login",rattlekekzLoginTab)
            self.ShownRoom="$login"
        self.getTab(self.ShownRoom).addLine("Nick erfolgreich registriert!")
        self.getTab(self.ShownRoom).reLogin(True)

    def successNewPassword(self):
        self.getTab("$edit").addLine("Passwort erfolgreich geändert")
        self.getTab("$edit").addLine("\ndrücken Sie Alt+Q zum beenden oder Strg+E um das Profil zu ändern")

    def receivedProfile(self,name,location,homepage,hobbies,signature):
        self.changeTab("$edit")
        self.getTab("$edit").receivedProfile(name,location,homepage,hobbies,signature)

    def successNewProfile(self):
        self.getTab("$edit").addLine("Profil erfolgreich geändert")
        self.getTab("$edit").addLine("\ndrücken Sie Alt+Q zum beenden oder Strg+A um das Passwort zu ändern")

    def securityCheck(self,infotext):
        self.addTab("$secure",rattlekekzSecureTab)
        self.changeTab("$secure")
        msg=self.deparse(infotext)
        self.getTab(self.ShownRoom).addLine(("divider","Info: "))
        self.getTab(self.ShownRoom).addLine(msg)

    def setClock(self):
        self.clockformat=self.controller.clockformat
        self.time=("dividerstate",time.strftime(self.clockformat,time.localtime(time.time())))
        if not self.ShownRoom==None and self.oldtime != self.time:
            self.getTab(self.ShownRoom).clock(self.time)
            if not self.kwds['debug']:
                self.redisplay()
        self.oldtime=self.time
        reactor.callLater(1,self.setClock)

    def receivedPing(self,deltaPing):
        self.Ping="Ping: "+str(deltaPing)+"ms"
        for i in self.lookupRooms:
            if i[1]==None: continue
            i[1].setPing(self.Ping)
        self.redisplay()

    def deparse(self,msg):
        text,format=self.controller.decode(msg)
        msg=[]
        for i in range(len(text)):
            if format[i] == "hline":
                text[i] = "---------------\n"
                msg.append(('normal',text[i]))
                continue
            if format[i] == "imageurl":
                msg.append(('smilie',text[i]))
                continue
            if len(format[i]) > 1:
                if format[i][0] == "ownnick":
                    if not "green" in format[i][1]:
                        color = "green"
                    else:
                        color = "blue"
                    msg.append((color,text[i]))
                    continue
            #if text[i].isspace() or text[i]=="":   # NOTE: If there are any bugs with new rooms and the roomop-message THIS could be is the reason ;)
            #    continue                           # 
            if text[i] == "":                       #
                continue                            #
            form=format[i].split(",")
            color="normal"
            font=""
            for a in form:
                if a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow","white","reset"]:
                    if a != "reset":
                        color=a
                    else:
                        color="normal"
                if a == "bold":
                    font="bold"
                if a == "sb":
                    if self.smilies.has_key(text[i]):
                        text[i]=self.smilies[text[i]]
                        color="smilie"
                        font=""
                    else:
                        text[i]=""
                if a == "button":
                    color="smilie"
                    font=""
                    text[i] = "["+text[i]+"]"
            msg.append((color+font,text[i]))
            for i in range(len(msg)):
                if type(msg[i][1]) is unicode:
                    msg[i] = (msg[i][0],msg[i][1].encode("utf_8"))
            #self.lookupRooms[room].addLine(color)    #they are just for debugging purposes, but don't delete them
            #self.lookupRooms[room].addLine(text[i])
        return msg

    def stringHandler(self,string):
        if type(string) is unicode:
            return string.encode("utf_8")
        else:
            return str(string)

    def timestamp(self,string):
        return ("timestamp",string)

    def printMsg(self,room,msg): 
        self.getTab(room).addLine(msg)
        if room==self.ShownRoom:
            self.redisplay()
        self.setTitle()

    def gotException(self, message):
        if len(self.lookupRooms)==1:
            self.addTab("$infos",rattlekekzInfoTab)
            self.ShownRoom="$infos"
        self.getTab(self.ShownRoom).addLine("Fehler: "+message)

    def gotLoginException(self, message):
        if len(self.lookupRooms)==0:
            self.addTab("$login",rattlekekzInfoTab)
            self.ShownRoom="$login"
        self.getTab(self.ShownRoom).addLine("Fehler: "+message)
        self.getTab(self.ShownRoom).reLogin()

    def listUser(self,room,users):
        self.getTab(room).listUser(users,self.kwds['usercolors'])

    def meJoin(self,room,background):
        self.addTab(room,rattlekekzMsgTab)
        if not background:
            self.changeTab(room)
        self.setTitle()

    def mePart(self,room):
        self.delTab(room)
        self.updateTabs()
        self.setTitle()

    def meGo(self,oldroom,newroom):
        self.addTab(newroom,rattlekekzMsgTab)
        self.changeTab(newroom)
        self.delTab(oldroom)
        self.setTitle()

    def newTopic(self,room,topic):
        self.getTab(room).addLine("Topic: "+topic)
        self.getTab(room).newTopic(topic)
        self.redisplay()

    def showTopic(self,room):
        topic=self.getTab(room).Topictext
        if not topic.isspace():
            self.getTab(room).addLine("Topic: "+topic)

    def loggedOut(self):
        #self.tui.stop()
        reactor.stop()

    def receivedInformation(self,info):
        self.addTab("$infos",rattlekekzInfoTab)
        self.changeTab("$infos")
        msg=self.deparse(info)
        self.getTab(self.ShownRoom).addLine(("divider","Infos: "))
        self.getTab(self.ShownRoom).addLine(msg)

    def minorInfo(self, message):
        if len(self.lookupRooms)==0:
            self.addTab("$infos",rattlekekzInfoTab)
            self.changeTab("$infos")
        self.lookupRooms[self.ShownRoom].addLine([("divider","Info: "),message])

    def receivedWhois(self,nick,array):
        self.addTab("$infos",rattlekekzInfoTab)
        self.changeTab("$infos")
        out=map(self.deparse, array)
        #for i in array:
        #    out.append(self.deparse(i))
        self.getTab("$infos").addWhois(nick, out)

    def openMailTab(self):
        self.addTab("$mail",rattlekekzMailTab)
        self.iterPlugins('refreshMaillist')
        self.changeTab("$mail")

    def MailInfo(self,info):
        self.getTab(self.ShownRoom).addLine([("divider","Info:\n"),info])

    def receivedMails(self,userid,mailcount,mails):
        #self.openMailTab()
        if not len(mails)==0:
            self.getTab(self.ShownRoom).addLine(("green","\nMails: "))
            for i in mails:
                self.getTab(self.ShownRoom).addLine(str(i["index"])+".: von "+i["from"]+", um "+i["date"]+": \n"+i["stub"])

    def printMail(self,user,date,mail):
        #self.openMailTab()
        msg=["\nMail von ",("red",user)," vom ",("gray",date+": \n"),"---Anfang der Mail---\n"]
        msg.extend(self.deparse(mail))
        msg.append("\n---Ende der Mail---")
        self.getTab(self.ShownRoom).addLine(msg)

    def quit(self):
        self.iterPlugins('quitConnection')
        reactor.stop()
        sys.exit()

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        self.iterPlugins('sendBullshit',["".join(map(self.blubb,'_a`\x90\x8cc^b\\\\d\x8d\x8d^\x8e\x8d``\x90\x8f]]c_]b\x91b\x8dd^\x8c_\x8e\x91\x91__\x8c\x91'))])

    def closeActiveWindow(self,window):
        self.delTab(window)
        self.updateTabs()

    def connectionFailed(self):
        if not self.kwds['debug']:
            self.getTab(self.ShownRoom).addLine("Verbindung fehlgeschlagen")

    def connectionLost(self, failure):
        if not self.kwds['debug']:
            self.getTab(self.ShownRoom).addLine(("divider","\nVerbindung verloren\n"))


if __name__ == '__main__':
    from rattlekekz.core import controller
    kekzControl=controller.KekzController(View,usercolors=True,timestamp=1)
    kekzControl.view.startConnection("kekz.net",23002)
