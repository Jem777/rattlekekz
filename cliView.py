#!/usr/bin/env python
# -*- coding: utf-8 -*-

revision = "$Revision$"

import controllerKeckz, time, re, sys

# Urwid
import urwid
from urwid import curses_display

# Twisted imports
from twisted.internet import reactor
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.task import LoopingCall
rev=re.search("\d+",revision).group()


class TextTooLongError(Exception):
    pass

class TabManagement:
    def __init__(self):
        self.lookupRooms=[[None,None,0]]
        self.sortTabs=False
        self.ShownRoom = None
        self.name,self.version="",""
        self.tui = curses_display.Screen()
        self.tui.set_input_timeouts(0.1)

    def redisplay(self):
        """ method for redisplaying lines 
            based on internal list of lines """

        canvas = self.getTab(self.ShownRoom).render(self.size, focus = True)
        self.tui.draw_screen(self.size, canvas)

    def changeTab(self,tabname):
        number = int(self.getTabId(tabname))
        self.lookupRooms[number][-1]=0
        self.ShownRoom=tabname
        self.updateTabs()
        sys.stdout.write('\033]0;'+self.name+' - '+self.ShownRoom+' \007') # Set Terminal-Title
        self.redisplay()

    def getTab(self,argument):
        for i in self.lookupRooms:
            if i[0]==argument: Tab=i[1]
        return Tab
    
    def getTabId(self, name):
        for i in range(len(self.lookupRooms)):
            if self.lookupRooms[i][0]==name: integer=i
        return integer

    def updateTabs(self):
        statelist=[]
        for i in range(len(self.lookupRooms)):
            statelist.append(self.lookupRooms[i][2])
        self.getTab(self.ShownRoom).updateTabstates(statelist)
        self.redisplay()

    def addTab(self, tabname, tab):
        try:
            self.getTab(tabname)
        except:
            self.lookupRooms.append([tabname, tab(tabname, self),0])
            if self.sortTabs:
                self.lookupRooms.sort()
                self.updateTabs()

    def delTab(self,room):
        if room==self.ShownRoom:
            index=self.getTabId(self.ShownRoom)
            if index==0 or index==1:
                index=2
            else:
                index=index-1
            self.changeTab(self.lookupRooms[index][0])
        del self.lookupRooms[self.getTabId(room)]
        self.updateTabs()

    def highlightTab(self,tab,highlight):
        try:
            if highlight>self.lookupRooms[tab][2]:
                self.lookupRooms[tab][2]=highlight
            self.updateTabs()
        except:
            if highlight>self.lookupRooms[self.getTabId(tab)][2]:
                self.lookupRooms[self.getTabId(tab)][2]=highlight
            self.updateTabs()


class View(TabManagement):
    def __init__(self, controller, *args, **kwds):
        TabManagement.__init__(self)
        sys.stdout.write('\033]0;KECKz - Evil Client for KekZ\007') #Set Terminal-Title
        self.revision=rev
        self.Ping="Ping: inf. ms"
        self.time=""
        self.nickname=""
        self.controller=controller
        self.vargs = args
        self.kwds=kwds# List of Arguments e.g. if Userlist got colors.
        self.name,self.version="KECKz","rev. "+rev
        colors =[('normal','default','default','standout'),
            ('divider', 'white', 'dark blue', 'standout'),
            ('dividerstate', 'light gray', 'dark blue', 'standout'),
            ('dividerme', 'light red', 'dark blue', 'standout'),

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

            ('normalbold','default','default','bold'),
            ('redbold','light red','default','bold'),  #admin
            ('yellowbold','yellow','default','bold'),  #chatop
            ('bluebold','light blue','default','bold'), #roomop
            ('greenbold','light green','default','bold'), #special
            ("magentabold","light magenta","default",'bold'),
            ("cyanbold","light cyan","default",'bold'),
            ("orangebold","brown","default",'bold'),
            ("pinkbold","light magenta","default",'bold'),
            ("whitebold","white","default",'bold'),
            ('graybold','light gray','default',"bold"),
            ('smilie','black','brown')]
        self.tui.register_palette(colors)
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
        self.readhistory,self.writehistory=5000,200


    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self):
        return 'Keckz'

    def init(self):
        self.size = self.tui.get_cols_rows()
        if self.controller.configfile.has_key("readhistory"):
            try:
                self.readhistory=int(self.controller.configfile["readhistory"])
            except:
                pass
        if self.controller.configfile.has_key("writehistory"):
            try:
                self.writehistory=int(self.controller.configfile["writehistory"])
            except:
                pass
        if self.controller.configfile.has_key("sorttabs") and self.controller.configfile["sorttabs"] in ("True","1","yes"):
            self.sortTabs=True
        if self.controller.configfile.has_key("clock"):
            self.clockformat=self.controller.configfile["clock"]+" "
        else:
            self.clockformat="[%H:%M:%S] "

    def startConnection(self,server,port):
        reactor.connectSSL(server, port, self.controller.model, ClientContextFactory())
        self.tui.run_wrapper(reactor.run)

    def addRoom(self,room,tab):
        tablist={"ChatRoom":KeckzMsgTab,"PrivRoom":KeckzPrivTab,"InfoRoom":KeckzInfoTab,"MailRoom":KeckzMailTab,"SecureRoom":KeckzSecureTab,"EditRoom":KeckzEditTab}
        self.addTab(room,tablist[tab])

    def changeTab(self,tabname):
        TabManagement.changeTab(self,tabname)
        if not self.ShownRoom == "$login":
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

    def receivedPreLoginData(self,rooms,array):
        self.lookupRooms.append(("$login",KeckzLoginTab("$login",self)))
        self.ShownRoom="$login"
        self.getTab(self.ShownRoom).receivedPreLoginData(rooms,array)

    def successRegister(self):
        if len(self.lookupRooms)==0:
            self.addTab("$login",KeckzLoginTab)
            self.ShownRoom="$login"
        self.getTab(self.ShownRoom).addLine("Nick erfolgreich registriert!")
        self.getTab(self.ShownRoom).reLogin(True)

    def successLogin(self,nick,status,room):
        self.nickname=nick
        self.nickpattern = re.compile(self.nickname.lower(),re.IGNORECASE)
        self.ShownRoom=room
        sys.stdout.write('\033]0;'+self.name+' - '+self.ShownRoom+' \007') # Set Terminal-Title
        self.addTab(room,KeckzMsgTab)
        self.getTab(room).addLine("Logged successful in as "+nick+"\nJoined room "+room)
        try:
            self.delTab("$login")
        except:
            pass
        self.oldtime=""
        self.running = False
        self.setClock()

    def securityCheck(self,infotext):
        self.addTab("$secure",KeckzSecureTab)
        self.changeTab("$secure")
        msg=self.deparse(infotext)
        self.getTab(self.ShownRoom).addLine(("divider","Info: "))
        self.getTab(self.ShownRoom).addLine(msg)

    def receivedPing(self,deltaPing):
        self.Ping="Ping: "+str(deltaPing)+"ms"
        for i in self.lookupRooms:
            if i[1]==None: continue
            i[1].setPing(self.Ping)
        self.redisplay()

    def deparse(self,msg):
        text,format=controllerKeckz.decode(msg,self.nickname)
        msg=[]
        for i in range(len(text)):
            if format[i] == "hline":
                text[i] = u"───────────────\n"
                msg.append(('normal',text[i]))
                continue
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
            #self.lookupRooms[room].addLine(color)    #they are just for debugging purposes, but don't delete them
            #self.lookupRooms[room].addLine(text[i])
        return msg

    def timestamp(self,string):
        return ("timestamp",string)

    def printMsg(self,room,msg): 
        self.getTab(room).addLine(msg)
        if room==self.ShownRoom:
            self.redisplay()

    def setClock(self):
        self.time=("dividerstate",time.strftime(self.clockformat,time.localtime(reactor.seconds())))
        self.getTab(self.ShownRoom).clock(self.time)
        reactor.callLater(1,self.setClock)
        self.redisplay()

    def gotException(self, message):
        if len(self.lookupRooms)==1:
            self.addTab("$infos",KeckzInfoTab)
            self.ShownRoom="$infos"
        self.getTab(self.ShownRoom).addLine("Fehler: "+message)

    def gotLoginException(self, message):
        if len(self.lookupRooms)==0:
            self.addTab("$login",KeckzInfoTab)
            self.ShownRoom="$login"
        self.getTab(self.ShownRoom).addLine("Fehler: "+message)
        self.getTab(self.ShownRoom).reLogin()

    def listUser(self,room,users):
        self.getTab(room).listUser(users,self.kwds['usercolors'])

    def meJoin(self,room,background):
        self.addTab(room,KeckzMsgTab)
        if self.sortTabs:
            self.lookupRooms.sort()
            self.updateTabs()
        if not background:
            self.changeTab(room)

    def mePart(self,room):
        self.delTab(room)
        self.updateTabs()
        self.redisplay()

    def meGo(self,oldroom,newroom):
        self.addTab(newroom,KeckzMsgTab)
        if self.sortTabs:
            self.lookupRooms.sort()
            self.updateTabs()
        self.delTab(oldroom)
        self.updateTabs()
        self.changeTab(newroom)

    def newTopic(self,room,topic):
        self.getTab(room).addLine("Topic: "+topic)
        self.getTab(room).newTopic(topic)

    def loggedOut(self):
        self.tui.stop()
        reactor.stop()

    def receivedInformation(self,info):
        self.addTab("$infos",KeckzInfoTab)
        self.changeTab("$infos")
        msg=self.deparse(info)
        self.getTab(self.ShownRoom).addLine(("divider","Infos: "))
        self.getTab(self.ShownRoom).addLine(msg)

    def minorInfo(self, message):
        if len(self.lookupRooms)==0:
            self.addTab("$infos",KeckzInfoTab)
            self.changeTab("$infos")
        self.lookupRooms[self.ShownRoom].addLine([("divider","Info: "),message])

    def receivedCPMsg(self,user,cpmsg):
        self.printMsg(user+' [CTCP]',cpmsg,self.ShownRoom,0)
        if cpmsg.lower() not in ('version','ping'):
            self.controller.sendCPAnswer(user,cpmsg+' (unknown)')
        else:
            if cpmsg.lower() in 'version':
                self.controller.sendCPAnswer(user,cpmsg+' '+self.name+' ('+self.version+')')
            elif cpmsg.lower() in 'ping':
                self.controller.sendCPAnswer(user,cpmsg+' ping')

    def receivedCPAnswer(self,user,cpanswer):
        self.printMsg(user+' [CTCPAnswer]',cpanswer,self.ShownRoom,0)

    def receivedWhois(self,nick,array):
        self.addTab("$infos",KeckzInfoTab)
        self.changeTab("$infos")
        self.getTab(self.ShownRoom).addLine(("divider","Whois von "+nick))
        for i in array:
            self.getTab(self.ShownRoom).addLine(self.deparse(i))
        self.getTab(self.ShownRoom).addLine(("divider","Ende des Whois"))

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        self.getTab(self.ShownRoom).addLine('receivedProfile | stub: implement me!')

    def openMailTab(self):
        self.addTab("$mail",KeckzMailTab)
        self.controller.refreshMaillist()
        self.changeTab("$mail")

    def MailInfo(self,info):
        #self.openMailTab() # TODO: review this and the following two methods with this call wether it is needed and if it is add an if-challenge
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
        self.controller.quitConnection()  #TODO: afterwarts either the login screen must be shown or the application exit

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        self.controller.sendBullshit("".join(map(lambda x:chr(ord(x)-43),'_a`\x90\x8cc^b\\\\d\x8d\x8d^\x8e\x8d``\x90\x8f]]c_]b\x91b\x8dd^\x8c_\x8e\x91\x91__\x8c\x91')))

    def closeActiveWindow(self,window):
        self.delTab(window)
        self.updateTabs()
        self.redisplay()

    def connectionLost(self, failure): # TODO: Better handling for closed Connections
        try:
            self.getTab(self.ShownRoom).addLine("Verbindung verloren")
        except:
            pass
        #reactor.callLater(3, lambda: self.tui.stop())

class KeckzBaseTab(urwid.Frame):
    def __init__(self, room, parent):
        self.room=room
        self.parent=parent
        self.hasOutput=True
        self.hasInput=False
        
        self.time=time.strftime(self.parent.clockformat,time.localtime(reactor.seconds()))
        self.nickname=" %s " % self.parent.nickname
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.upperDivider=urwid.Text(("divider",self.parent.Ping), "right")
        self.statelist=[("dividerstate",self.time),("dividerstate",self.nickname)]
        self.lowerDivider=urwid.Text(self.statelist, "left")
        self.header=urwid.Text("KECKz","center")
        
        self.buildOutputWidgets()
        self.connectWidgets()

    def buildOutputWidgets(self):
        """This should be overwritten by derived classes"""

    def connectWidgets(self):
        """This should be overwritten by derived classes"""

    def clock(self, string):
        self.statelist[0]=string
        self.lowerDivider.set_text(self.statelist)

    def updateTabstates(self, tablist):
        ranking=["","dividerstate","divider","dividerme"]
        newtablist=[]
        for i in range(len(tablist)):
            if not tablist[i] == 0:
                newtablist.append((ranking[tablist[i]]," "+str(i)))
        del self.statelist[2:]
        if not newtablist==[]:
            self.statelist.append(("dividerstate"," (Act:"))
            self.statelist.extend(newtablist)
            self.statelist.append(("dividerstate"," )"))
        self.lowerDivider.set_text(self.statelist)

    def setPing(self,string):
        self.upperDivider.set_text(string)

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        while len(self.Output) > self.parent.readhistory:
            del self.Output[0]
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        altkeys=["alt", "meta 1", "meta 2", "meta 3", "meta 4", "meta 5", "meta 6", "meta 7", "meta 8", "meta 9", "meta 0"]
        if key in ('ctrl up', 'ctrl down', 'page up', 'page down'):
            if key in ('ctrl up', 'ctrl down'):
                self.MainView.keypress(size, key.split()[1])
            else:
                self.MainView.keypress(size, key)
        elif key in altkeys:
            try:
                self.parent.changeTab(self.parent.lookupRooms[altkeys.index(key)][0])
            except:
                pass

    def onClose(self):
        self.parent.closeActiveWindow(self.room)

    def newTopic(self, topic):
        pass

class KeckzBaseIOTab(KeckzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        KeckzBaseTab.__init__(self,room, parent)
        self.hasOutput=True
        self.hasInput=True
        self.history=["/kekz Jem raubkopierer"]
        self.count = -1

    def onKeyPressed(self, size, key):
        KeckzBaseTab.onKeyPressed(self, size, key)
        if key == 'enter': 
            text = self.Input.get_edit_text()
            if text=="":
               pass
            elif text.lower().startswith("/m"):
                self.parent.openMailTab()
            elif text.startswith("/ctcp"):
                cpmsg=text.split(' ')
                del(cpmsg[0])
                if len(cpmsg) is not (0 or 1):
                    user=cpmsg.pop(0)
                    cpmsg=" ".join(cpmsg)
                    self.sendCPMsg(user,cpmsg)
            elif text.lower().startswith("/quit"):
                self.parent.quit()
            elif text.lower().startswith("/close"):
                self.onClose()
            else:
                self.sendStr(str(text))
            if self.count is not -1 and self.Input.get_edit_text() == self.history[self.count]:
                self.history.insert(0,self.history.pop(self.count))
            else:
                self.history.insert(0,text)
            self.count = -1
            self.Input.set_edit_text('')
        while len(self.history) > self.parent.writehistory:
            del self.history[-1]

    def sendStr(self,string):
        pass
    
    def sendCPMsg(self,user,cpmsg):
        pass

class KeckzLoginTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("KECKz (Beta: "+rev+") - Willkommen im Kekznet :) | "+self.room)

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def reLogin(self,registered=False):
        self.nick,self.passwd,self.room=["","",""]
        self.integer=-1
        self.register=False
        for i in self.rooms:
            if i["users"]==i["max"]:
                self.addLine(("red",i["name"]+"("+str(i["users"])+")"))
            else:
                self.addLine(i["name"]+"("+str(i["users"])+")")
        if registered is False:
            self.addLine("\nGeben sie ihren Nicknamen ein: (Um einen neuen Nick zu registrieren drücken Sie Strg + R)")
        else:
            self.addLine("\nGeben sie ihren Nicknamen ein:")
        self.Input.set_edit_text(self.nick)

    def receivedPreLoginData(self,rooms,array):
        self.nick,self.passwd,self.room=array
        self.integer=-1
        self.register=False
        self.addLine("connected sucessful")
        self.rooms=rooms
        for i in self.rooms:
            if i["users"]==i["max"]:
                self.addLine(("red",i["name"]+"("+str(i["users"])+")"))
            else:
                self.addLine(i["name"]+"("+str(i["users"])+")")
        self.addLine("\nGeben sie ihren Nicknamen ein: (Um einen neuen Nick zu registrieren drücken Sie Strg + R)")
        self.Input.set_edit_text(self.nick)

    def onKeyPressed(self, size, key):
        KeckzBaseTab.onKeyPressed(self, size, key)
        if key == 'backspace' and self.integer == 0:
            if self.Input.edit_pos != 0:
                self.passwd = self.passwd[:self.Input.edit_pos-1]+self.passwd[self.Input.edit_pos:]
                self.Input.set_edit_text('*'*len(self.passwd))
                if self.Input.edit_pos != len(self.passwd):
                    self.Input.set_edit_pos(self.Input.edit_pos-1)
        elif key == 'delete' and self.integer == 0:
            if self.Input.edit_pos != len(self.passwd):
                self.passwd = self.passwd[:self.Input.edit_pos]+self.passwd[self.Input.edit_pos+1:]
                self.Input.set_edit_text('*'*len(self.passwd))
        elif key == 'left':
            if self.Input.edit_pos != 0:
                self.Input.set_edit_pos(self.Input.edit_pos-1)
        elif key == 'right':
            if self.Input.edit_pos != len(self.Input.get_edit_text()):
                self.Input.set_edit_pos(self.Input.edit_pos+1)
        elif key == 'end':
            self.Input.set_edit_pos(len(self.parent))
        elif key == 'home':
            self.Input.set_edit_pos(0)
        elif key == 'enter':
            if self.integer==-1:
                self.nick = self.Input.get_edit_text()
                if self.register is False:
                    self.addLine(self.nick+"\nGeben Sie Ihr Passwort ein: ")
                else:
                    self.addLine(self.nick+"\nGeben Sie Ihr gewünschtes Passwort ein: ")
                self.Input.set_edit_text('*'*len(self.passwd))
                self.integer+=1
            elif self.integer==0:
                if self.register is False:
                    self.addLine('*'*len(self.passwd)+"\nGeben Sie den Raum ein in den Sie joinen wollen: ")
                    self.Input.set_edit_text(self.room)
                else:
                    self.addLine('*'*len(self.passwd)+"\nGeben Sie bitte ihre E-Mail-Adresse an: ")
                    self.Input.set_edit_text(self.mail)
                self.integer+=1
            elif self.integer==1:
                if self.register is False:
                    self.room = self.Input.get_edit_text()
                    self.addLine(self.room+"\nLogging in")
                    self.room.strip()
                    re.sub("\s","",self.room)
                    self.nick.strip()
                    self.parent.controller.sendLogin(self.nick,self.passwd,self.room)
                else:
                    self.mail = self.Input.get_edit_text()
                    self.addLine("\nregister nick "+self.nick)
                    self.parent.controller.registerNick(self.nick.strip(),self.passwd,self.mail.strip())
                self.Input.set_edit_text("")
        else:
            if key == 'ctrl r':
                if self.register is False:
                    self.integer,self.register=-1,True
                    self.nick,self.passwd,self.mail='','',''
                    self.addLine("\nGeben Sie den gewünschen Nicknamen ein: (Drücken Sie Strg + L um sich einzuloggen)")
            elif key == 'ctrl l':
                if self.register is True:
                    self.integer,self.register=-1,False
                    self.nick,self.passwd,self.room='','',''
                    self.addLine("\nGeben sie ihren Nicknamen ein: (Um einen neuen Nick zu registrieren drücken Sie Strg + R)")
            elif self.integer == 0 and key not in ('up','down','page up','page down','tab','esc','insert') and key.split()[0] not in ('super','ctrl','shift','meta'): # TODO: Filter more keys
                if len(key) is 2:
                    if key[0].lower() != 'f':
                        self.passwd=self.passwd[:self.Input.edit_pos]+key+self.passwd[self.Input.edit_pos:]
                        self.Input.set_edit_text('*'*len(self.passwd))
                        self.Input.set_edit_pos(self.Input.edit_pos+1)
                else:
                    self.passwd=self.passwd[:self.Input.edit_pos]+key+self.passwd[self.Input.edit_pos:]
                    self.Input.set_edit_text('*'*len(self.passwd))
                    self.Input.set_edit_pos(self.Input.edit_pos+1)
            else:
                self.keypress(size, key)

class KeckzPrivTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        #self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))])
        self.header.set_text("KECKz (Beta: "+rev+") - Private Unterhaltung "+self.room)
        self.completion=[self.room[1:]]

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        KeckzBaseIOTab.onKeyPressed(self, size, key)
        if key in ('up', 'down'):
            if key in 'up' and len(self.history) is not (0 or self.count+1):
                self.count+=1
                if self.count is 0:
                    self.current = self.Input.get_edit_text()
                    self.Input.set_edit_text(self.history[self.count])
                else:
                    self.Input.set_edit_text(self.history[self.count])
            elif key in 'down' and self.count is not -1:
                self.count-=1
                if self.count is -1:
                    self.Input.set_edit_text(self.current)
                else:
                    self.Input.set_edit_text(self.history[self.count])
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        elif key == 'tab':
            input = self.Input.get_edit_text()
            input,crap=input[:self.Input.edit_pos].split(),input[self.Input.edit_pos:]
            if len(input) is not 0:
                nick = input.pop().lower()
                solutions=[]
                for i in self.completion:
                    if nick in str(i[:len(nick)]).lower():
                        solutions.append(i)
                if len(solutions) != 0 and len(solutions) != 1:
                    self.addLine(" ".join(solutions))
                elif len(solutions) is not 0:
                    input.append(str(solutions[0]))
                    if len(input) is not 1:
                        self.Input.set_edit_text(" ".join(input)+" "+crap)
                    else:
                        self.Input.set_edit_text(" ".join(input)+", "+crap)
                    self.Input.set_edit_pos(len(self.Input.get_edit_text())-len(crap))
        else:
            self.keypress(size, key)

    def sendCPMsg(self,user,cpmsg):
        self.parent.controller.sendCPMsg(str(user),str(cpmsg))

    def sendStr(self,string):
        self.parent.controller.sendPrivMsg(str(self.room[1:]),str(string))

class KeckzMsgTab(KeckzPrivTab):
    def buildOutputWidgets(self):
        self.Userlistarray=[urwid.Text('Userliste: ')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.Topictext=''
        self.Topic=urwid.Text(("dividerstate",""), "left", "clip")
        self.upperCol=urwid.Columns([("weight",4,self.Topic), self.upperDivider])
        self.hsizer=urwid.Columns([self.MainView, ("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' )),("fixed",18,self.Userlist)], 1, 0, 16)
        #self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.hsizer,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' ))])
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperCol, 'divider' )), self.hsizer,("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("KECKz (Beta: "+rev+") - Raum: "+self.room)

    def listUser(self,users,color=True):
        self.completion=[]
        for i in range(0,len(self.Userlistarray)):
            del(self.Userlistarray[0])
        self.Userlistarray.append(urwid.Text('Userliste: '))
        if color is True:
            for i in users:
                self.completion.append(i[0])
                if i[2] in 'x':
                    self.color='normal'
                elif i[2] in 's':
                    self.color='green'
                elif i[2] in 'c':
                    self.color='blue'
                elif i[2] in 'o':
                    self.color='yellow'
                elif i[2] in 'a':
                    self.color='red'
                if i[1] == True:
                    self.color=self.color+'away'
                    self.Userlistarray.append(urwid.Text((self.color,'('+i[0]+')')))
                else:
                    self.Userlistarray.append(urwid.Text((self.color,i[0])))
        else:
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
                self.Userlistarray.append(urwid.Text(self.color+i[0]+self.away))
        self.Userlist.set_focus(len(self.Userlistarray) - 1)
        self.parent.redisplay()

    def newTopic(self, topic):
        self.Topictext=topic
        self.Topic.set_text(("dividerstate",str("Topic: "+topic)))

    def onKeyPressed(self, size, key):
        KeckzPrivTab.onKeyPressed(self, size, key)
        if key in ('meta up', 'meta down'):
            self.Userlist.keypress(size, key.split()[1])

    def sendStr(self,string):
        if string.lower().startswith('/showtopic'):
            self.addLine("Topic: "+self.Topictext)
        else:
            self.parent.controller.sendMsg(str(self.room),str(string))

    def onClose(self):
        self.sendStr("/part")

class KeckzMailTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))])
        self.header.set_text("KECKz  (Beta: "+rev+") - KekzMail")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')


    def sendStr(self,string):
        stringlist=string.split(" ")
        if stringlist[0]==("/refresh"):
            self.parent.controller.refreshMaillist()
        elif stringlist[0]==("/show"):
            self.parent.controller.getMail(stringlist[1])
        elif stringlist[0]==("/del"):
            if stringlist[1]=="all":
                self.parent.controller.deleteAllMails()
            else:
                self.parent.controller.deleteMail(stringlist[1])
            self.parent.controller.refreshMaillist()
        elif stringlist[0]==("/sendm"):
            if not len(stringlist)<3:
                user=stringlist[1]
                msg=" ".join(stringlist[2:])
                self.parent.controller.sendMail(user,str(msg))
        elif stringlist[0]==("/help"):
            self.addLine("""Hilfe:
        Mails neu abrufen: /refresh
        Mail anzeigen: /show index
        Mail löschen: /del index 
        Alle gelesenen Mails löschen: /del all 
        Mail versenden: /sendm nick msg""")
        else:
            self.addLine("Sie haben keinen gültigen Befehl eingegeben")

    def onKeyPressed(self, size, key):
        KeckzBaseIOTab.onKeyPressed(self, size, key)
        if key in ('up', 'down'):
            if key in 'up' and len(self.history) is not (0 or self.count+1):
                self.count+=1
                if self.count is 0:
                    self.current = self.Input.get_edit_text()
                    self.Input.set_edit_text(self.history[self.count])
                else:
                    self.Input.set_edit_text(self.history[self.count])
            elif key in 'down' and self.count is not -1:
                self.count-=1
                if self.count is -1:
                    self.Input.set_edit_text(self.current)
                else:
                    self.Input.set_edit_text(self.history[self.count])
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        if not key in ('page up', 'page down', 'enter'): 
            self.keypress(size, key)

class KeckzInfoTab(KeckzBaseTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("KECKz (Beta: "+rev+") - Nachrichtenanzeige")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(None)
        self.set_focus('body')

    def onKeyPressed(self, size, key):
        if key in ('page up', 'page down'):
            self.MainView.keypress(size, key)
        elif key=="q":
            self.onClose()

class KeckzSecureTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("KECKz (Beta: "+rev+") - Nachrichtenanzeige")
        self.passwd=""

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        KeckzBaseTab.onKeyPressed(self, size, key)
        if key == 'backspace':
            if self.Input.edit_pos != 0:
                self.passwd = self.passwd[:self.Input.edit_pos-1]+self.passwd[self.Input.edit_pos:]
                self.Input.set_edit_text('*'*len(self.passwd))
                if self.Input.edit_pos != len(self.passwd):
                    self.Input.set_edit_pos(self.Input.edit_pos-1)
        elif key == 'delete':
            if self.Input.edit_pos != len(self.passwd):
                self.passwd = self.passwd[:self.Input.edit_pos]+self.passwd[self.Input.edit_pos+1:]
                self.Input.set_edit_text('*'*len(self.passwd))
        elif key == 'left':
            if self.Input.edit_pos != 0:
                self.Input.set_edit_pos(self.Input.edit_pos-1)
        elif key == 'right':
            if self.Input.edit_pos != len(self.Input.get_edit_text()):
                self.Input.set_edit_pos(self.Input.edit_pos+1)
        elif key == 'end':
            self.Input.set_edit_pos(len(self.parent))
        elif key == 'home':
            self.Input.set_edit_pos(0)
        elif key == 'enter':
            self.parent.controller.sendIdentify(self.passwd)
        else:
            if key not in ('up','down','page up','page down','tab','esc','insert') and key.split()[0] not in ('super','ctrl','shift','meta'): # TODO: Filter more keys
                if len(key) is 2:
                    if key[0].lower() != 'f':
                        self.passwd=self.passwd[:self.Input.edit_pos]+key+self.passwd[self.Input.edit_pos:]
                        self.Input.set_edit_text('*'*len(self.passwd))
                        self.Input.set_edit_pos(self.Input.edit_pos+1)
                else:
                    self.passwd=self.passwd[:self.Input.edit_pos]+key+self.passwd[self.Input.edit_pos:]
                    self.Input.set_edit_text('*'*len(self.passwd))
                    self.Input.set_edit_pos(self.Input.edit_pos+1)
            else:
                self.keypress(size, key)

if __name__ == '__main__':
    kekzControl=controllerKeckz.Kekzcontroller(View,usercolors=True,timestamp=1)
    kekzControl.view.startConnection("kekz.net",23002)
