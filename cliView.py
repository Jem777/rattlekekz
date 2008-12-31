#!/usr/bin/env python
# -*- coding: utf-8 -*-

revision = "$Revision$"

import controllerKeckz, time, re

# Urwid
import urwid
from urwid import curses_display

# Twisted imports
from twisted.internet import reactor, ssl

rev=re.search("\d+",revision).group()


class TextTooLongError(Exception):
    pass

class View:
    def __init__(self, controller, *args, **kwds):
        self.nickname=""
        self.controller=controller
        self.vargs = args
        self.kwds=kwds# List of Arguments e.g. if Userlist got colors.
        self.name,self.version="KECKz","rev. "+rev
        tui = curses_display.Screen()
        tui.set_input_timeouts(0.1)
        colors =[('normal','default','default','standout'),
            ('divider', 'white', 'dark blue', 'standout'),

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
        tui.register_palette(colors)
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
        self.tui = tui
        self.lookupRooms={}


    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self): return 'CursesClient'

    def init(self):
        self.size = self.tui.get_cols_rows()

    def startConnection(self,server,port):
        reactor.connectSSL(server, port, self.controller.model, ssl.ClientContextFactory())
        self.tui.run_wrapper(reactor.run)

    def redisplay(self):
        """ method for redisplaying lines 
            based on internal list of lines """

        canvas = self.lookupRooms[self.ShownRoom].render(self.size, focus = True)
        self.tui.draw_screen(self.size, canvas)

    def doRead(self):
        """ Input is ready! """
        keys = self.tui.get_input()

        for key in keys:
            if key == 'window resize':
                self.size = self.tui.get_cols_rows()
                self.redisplay()
            elif key == "ctrl n" or key=="ctrl p":
                array=self.lookupRooms.keys()
                index=array.index(self.ShownRoom)
                if array[index]==array[-1] and key=="ctrl n":
                    index=0
                elif key=="ctrl n":
                    index=index+1
                elif array[index]==array[0]:
                    index=-1
                else:
                    index=index-1
                self.ShownRoom=array[index]
                self.lookupRooms[self.ShownRoom]
            else:
                self.lookupRooms[self.ShownRoom].onKeyPressed(self.size, key)
        self.redisplay()

    def receivedPreLoginData(self,rooms,array):
        self.Ping="Ping: inf. ms"
        self.lookupRooms.update({"$login":KeckzLoginTab("$login",self)})
        self.ShownRoom="$login"
        self.lookupRooms[self.ShownRoom].receivedPreLoginData(rooms,array)

    def successLogin(self,nick,status,room):
        self.nickname=nick
        self.ShownRoom=room
        self.lookupRooms.update({room:KeckzMsgTab(room,self)})
        self.lookupRooms[self.ShownRoom].addLine("Logged successful in as "+nick+"\nJoined room "+room)
        if self.lookupRooms.has_key("$login"):
            del self.lookupRooms["$login"]

    def receivedPing(self,deltaPing):
        self.Ping="Ping: "+str(deltaPing)+"ms"
        for i in self.lookupRooms:
            self.lookupRooms[i].setPing(self.Ping)
        self.redisplay()

    def deparse(self,msg):
        text,format=controllerKeckz.decode(msg)
        msg=[]
        for i in range(len(text)):
            if text[i].isspace() or text[i]=="":
                continue
            form=format[i].split(",")
            color="normal"
            font=""
            for a in form:
                if a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow","white"]:
                    color=a
                if a == "bold":
                    font="bold"
                if a in "sb":
                    if self.smilies.has_key(text[i]):
                        text[i]=self.smilies[text[i]]
                        color="smilie"
                    else:
                        text[i]=""
            msg.append((color+font,text[i]))
            #self.lookupRooms[room].addLine(color)    #they are just for debugging purposes, but don't delete them
            #self.lookupRooms[room].addLine(text[i])
        return msg

    def printMsg(self,nick,message,room,state):
        if self.kwds['timestamp'] == 1:
            msg=[("timestamp",time.strftime("[%H:%M] ",time.localtime(time.time())))]
        elif self.kwds['timestamp'] == 2:
            msg=[("timestamp",time.strftime("[%H:%M:%S] ",time.localtime(time.time())))]
        elif self.kwds['timestamp'] == 3:
            msg=[("timestamp",time.strftime("[%H%M] ",time.localtime(time.time())))]
        if state==0 or state==2 or state==4:
            if nick==self.nickname:
                msg.append(("green",nick+": "))
            else:    
                msg.append(("blue",nick+": "))
        elif state==3:
            msg.append(("green",self.nickname+": "))
        if state==2 or state==3:
            room="#"+nick
            if self.lookupRooms.has_key(room)==False:
                self.lookupRooms.update({room:KeckzPrivTab(room, self)})
                self.lookupRooms[room].setPing(self.Ping)
        if state==4:
            room=self.ShownRoom
        msg.extend(self.deparse(message))
        self.lookupRooms[room].addLine(msg)


    def gotException(self, message):
        if len(self.lookupRooms)==0:
            self.lookupRooms.update({"$infos":KeckzInfoTab("$infos", self)})
            self.lookupRooms[self.ShownRoom].setPing(self.Ping)
            self.ShownRoom="$infos"
        self.lookupRooms[self.ShownRoom].addLine("Fehler: "+message)

    def listUser(self,room,users):
        self.lookupRooms[room].listUser(users,self.kwds['usercolors'])

    def meJoin(self,room,background):
        self.lookupRooms.update({room:KeckzMsgTab(room, self)})
        self.lookupRooms[room].setPing(self.Ping)
        if not background:
            self.ShownRoom=room
            self.redisplay()

    def mePart(self,room):
        if room==self.ShownRoom:
            array=self.lookupRooms.keys()
            index=array.index(self.ShownRoom)
            if array[index]==array[0]:
                index=-1
            else:
                index=index-1
            self.ShownRoom=array[index]
        del self.lookupRooms[room]
        self.redisplay()

    def meGo(self,oldroom,newroom):
        self.lookupRooms.update({newroom:KeckzMsgTab(newroom, self)})
        self.lookupRooms[newroom].setPing(self.Ping)
        self.ShownRoom=newroom
        del self.lookupRooms[oldroom]
        self.redisplay()

    def newTopic(self,room,topic):
        self.lookupRooms[room].addLine("Neues Topic: "+topic)

    def loggedOut(self):
        self.tui.stop()
        reactor.stop()

    def receivedInformation(self,info):
        if not self.lookupRooms.has_key("$infos"):
            self.lookupRooms.update({"$infos":KeckzInfoTab("$infos", self)})
            self.lookupRooms[self.ShownRoom].setPing(self.Ping)
        self.ShownRoom="$infos"
        msg=self.deparse(info)
        self.lookupRooms[self.ShownRoom].addLine(("divider","Infos: "))
        self.lookupRooms[self.ShownRoom].addLine(msg)

    def receivedCPMsg(self,user,cpmsg):
        if cpmsg.upper() not in ('VERSION','PING'):
            self.controller.sendCPAnswer(user,cpmsg+' unknown')
        else:
            self.printMsg(user+' [CTCP]',cpmsg,self.ShownRoom,0)
            if cpmsg.lower() in 'version':
                self.controller.sendCPAnswer(user,cpmsg+' '+self.name+' ('+self.version+')')
            elif cpmsg.lower() in 'ping':
                self.controller.sendCPAnswer(user,cpmsg+' ping')

    def receivedCPAnswer(self,user,cpanswer):
        self.printMsg(user+' [CTCPAnswer]',cpanswer,self.ShownRoom,0)

    def receivedWhois(self,nick,array):
        if not self.lookupRooms.has_key("$infos"):
            self.lookupRooms.update({"$infos":KeckzInfoTab("$infos", self)})
            self.lookupRooms[self.ShownRoom].setPing(self.Ping)
        self.ShownRoom="$infos"
        self.lookupRooms[self.ShownRoom].addLine(("divider","Whois von "+nick))
        for i in array:
            self.lookupRooms[self.ShownRoom].addLine(self.deparse(i))
        self.lookupRooms[self.ShownRoom].addLine(("divider","Ende des Whois"))

    def openMailTab(self):
        if not self.lookupRooms.has_key("$mail"):
            self.lookupRooms.update({"$mail":KeckzMailTab("$mail", self)})
            self.lookupRooms[self.ShownRoom].setPing(self.Ping)
            self.controller.refreshMaillist()
        self.ShownRoom="$mail"

    def MailInfo(self,info):
        self.openMailTab()
        self.lookupRooms[self.ShownRoom].addLine([("divider","Info:\n"),info])

    def receivedMails(self,userid,mailcount,mails):
        self.openMailTab()
        if not len(mails)==0:
            self.lookupRooms[self.ShownRoom].addLine(("green","\nMails: "))
            for i in mails:
                self.lookupRooms[self.ShownRoom].addLine(str(i["index"])+".: von "+i["from"]+", um "+i["date"]+": \n"+i["stub"])

    def printMail(self,user,date,mail):
        self.openMailTab()
        msg=["\nMail von ",("red",user)," vom ",("gray",date+": \n"),"---Anfang der Mail---\n"]
        msg.extend(self.deparse(mail))
        msg.append("\n---Ende der Mail---")
        self.lookupRooms[self.ShownRoom].addLine(msg)

    def quit(self):
        self.controller.quitConnection()  #TODO: afterwarts either the login screen must be shown or the application exit

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        self.controller.sendBullshit("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z")))

    def closeActiveWindow(self,window):
        array=self.lookupRooms.keys()
        if len(array)==1:
            self.quit()
        else:
            index=array.index(window)
            if array[index]==array[0]:
                index=-1
            else:
                index=index-1
            del self.lookupRooms[window]
            self.ShownRoom=array[index]
            self.redisplay()

    def connectionLost(self, failure):
        self.tui.stop()
        reactor.stop()
        print "Verbindung verloren: "+str(failure)

class KeckzBaseTab(urwid.Frame):
    def __init__(self, room, parent):
        self.hasOutput=True
        self.hasInput=False
        self.room=room
        self.parent=parent
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.upperDivider=urwid.Text(("divider","Ping: inf. ms"), "right")
        self.header=urwid.Text("KECKz","center")
        
        self.buildOutputWidgets()
        self.connectWidgets()

    def buildOutputWidgets(self):
        """This should be overwritten by derived classes"""

    def connectWidgets(self):
        """This should be overwritten by derived classes"""

    def setPing(self,string):
        self.upperDivider.set_text(string)

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        if key in ('ctrl up', 'ctrl down', 'page up', 'page down'):
            if key in ('ctrl up', 'ctrl down'):
                self.MainView.keypress(size, key.split()[1])
            else:
                self.MainView.keypress(size, key)

    def OnClose(self):
        self.parent.closeActiveWindow(self.room)

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
            elif text=="/m":
                self.parent.openMailTab()
            elif text.startswith("/ctcp"):
                cpmsg=text.split(' ')
                del(cpmsg[0])
                if len(cpmsg) is not (0 or 1):
                    user=cpmsg.pop(0)
                    cpmsg=" ".join(cpmsg)
                    self.sendCPMsg(user,cpmsg)
            elif text=="/quit":
                self.parent.quit()
            elif text=="/close":
                self.OnClose()
            else:
                self.sendStr(str(text))
            if self.count is not -1:
                self.history.insert(0,self.history.pop(self.count))
            else:
                self.history.insert(0,text)
            self.count = -1
            self.Input.set_edit_text('')

    def sendStr(self,string):
        pass
    
    def sendCPMsg(self,user,cpmsg):
        pass

class KeckzLoginTab(KeckzBaseIOTab): # TODO: Make this fuck working
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.Input = urwid.Edit()
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("KECKz (Alpha: "+rev+") - Private Unterhaltung "+self.room)

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def receivedPreLoginData(self,rooms,array):
        self.addLine("connected sucessful")
        for i in rooms:
            if i["users"]==i["max"]:
                self.addLine(("red",i["name"]+"("+str(i["users"])+")"))
            else:
                self.addLine(i["name"]+"("+str(i["users"])+")")


class KeckzPrivTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.header.set_text("KECKz (Alpha: "+rev+") - Private Unterhaltung "+self.room)
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
            if len(input) is not 0:
                input,crap=input[:self.Input.edit_pos].split(),input[self.Input.edit_pos:]
                nick = input.pop().lower()
                solutions=[]
                for i in self.completion:
                    if nick in str(i[:len(nick)]).lower():
                        solutions.append(i)
                if len(solutions) != 0 and len(solutions) != 1:
                    self.addLine(" ".join(solutions))
                elif len(solutions) is not 0:
                    input.append(solutions[0])
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
        self.hsizer=urwid.Columns([self.MainView, ("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' )),("fixed",18,self.Userlist)], 1, 0, 16)
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.hsizer,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' ))])
        self.header.set_text("KECKz (Alpha: "+rev+") - Raum: "+self.room)

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
                self.Userlistarray.append(urwid.Text((self.color,i[0]))) # may we use ● in front of nicks
        else:
            self.away=''
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
                    self.away=' A'
                else:
                    self.away=''
                self.Userlistarray.append(urwid.Text(self.color+i[0]+self.away))
        self.Userlist.set_focus(len(self.Userlistarray) - 1)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        KeckzPrivTab.onKeyPressed(self, size, key)
        if key in ('meta up', 'meta down'):
            self.Userlist.keypress(size, key.split()[1])

    def sendStr(self,string):
        self.parent.controller.sendMsg(str(self.room),str(string))

    def OnClose(self):
        self.sendStr("/part")

class KeckzMailTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.header.set_text("KECKz  (Alpha: "+rev+") - KekzMail")

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
        if not key in ('page up', 'page down', 'enter'): 
            self.keypress(size, key)

class KeckzInfoTab(KeckzBaseTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView])
        self.header.set_text("KECKz (Alpha: "+rev+") - Nachrichtenanzeige")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(None)
        self.set_focus('body')

    def onKeyPressed(self, size, key):
        if key in ('page up', 'page down'):
            self.MainView.keypress(size, key)
        elif key=="q":
            self.OnClose()

if __name__ == '__main__':
    kekzControl=controllerKeckz.Kekzcontroller(View,usercolors=True,timestamp=1)
    kekzControl.view.startConnection("kekz.net",23002)
