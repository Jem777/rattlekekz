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

import urwid, re

class rattlekekzBaseTab(urwid.Frame):
    def __init__(self, room, parent):
        """The Base Tab for rattlekekz
        all other tabs are derived by this one
        it takes two arguments:
            room (string) and parent (object) """
        self.room=str(room)
        self.parent=parent
        self.hasOutput=True
        self.hasInput=False
        
        self.time=""
        self.nickname=" %s " % self.parent.nickname
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.upperDivider=urwid.Text(("divider",self.parent.Ping), "right")
        self.statelist=[("dividerstate",self.time),("dividerstate",self.nickname),("dividerstate"," ")]
        self.lowerDivider=urwid.Text(self.statelist, "left")
        self.header=urwid.Text("rattlekekz","center")
        
        self.buildOutputWidgets()
        self.connectWidgets()

    def buildOutputWidgets(self):
        """This should be overwritten by derived classes"""

    def connectWidgets(self):
        """This should be overwritten by derived classes"""

    def clock(self, time):
        """Displays the current time"""
        self.statelist[0]=time
        self.lowerDivider.set_text(self.statelist)

    def updateTabstates(self, tablist):
        """Updates the list of active tabs"""
        ranking=["","dividerstate","divideryellow","dividerme"]
        newtablist=[]
        for i in range(len(tablist)):
            if not tablist[i] == 0:
                newtablist.append((ranking[tablist[i]]," "+str(i)))
        del self.statelist[3:]
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
        if self.MainView.get_focus()[1]>=len(self.Output) - 3:
            self.MainView.set_focus(len(self.Output) - 1)
        else:
            #"""Do something that informs the user that new text is there"""
            self.statelist[2]=("dividerstate","[*]")
            self.lowerDivider.set_text(self.statelist)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        altkeys=["alt", "meta 1", "meta 2", "meta 3", "meta 4", "meta 5", "meta 6", "meta 7", "meta 8", "meta 9", "meta 0"]
        if key in ('ctrl up', 'ctrl down', 'page up', 'page down'):
            if key in ('ctrl up', 'ctrl down'):
                self.MainView.keypress(size, key.split()[1])
            else:
                self.MainView.keypress(size, key)
            if self.MainView.get_focus()[1]>=len(self.Output) - 1:
                self.statelist[2]=("dividerstate"," ")
                self.lowerDivider.set_text(self.statelist)
                self.parent.redisplay()
        elif key in altkeys:
            try:
                self.parent.changeTab(self.parent.lookupRooms[altkeys.index(key)][0])
            except:
                pass

    def onClose(self):
        """Closes the Room"""
        self.parent.closeActiveWindow(self.room)


class rattlekekzLoginTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))])
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Willkommen im Kekznet | "+self.room)

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
        self.passwd=""
        self.integer=-1
        self.register=False
        self.addLine("connected sucessful")
        self.rooms=rooms
        for i in self.rooms:
            if i["users"]==i["max"]:
                self.addLine(("red",i["name"]+"("+str(i["users"])+")"))
            else:
                self.addLine(i["name"]+"("+str(i["users"])+")")
        self.Input.set_edit_text(self.nick)
        self.Input.set_edit_pos(len(self.nick))
        self.addLine("\nGeben sie ihren Nicknamen ein: (Um einen neuen Nick zu registrieren drücken Sie Strg + R)")

    def onKeyPressed(self, size, key):
        if self.parent.isConnected:
            self.onReallyKeyPressed(size, key)
        else:
            pass

    def onReallyKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
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
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        elif key == 'home':
            self.Input.set_edit_pos(0)
        elif key in ['enter','tab','shift tab']:
            if self.integer==-1:
                self.nick = self.Input.get_edit_text()
                if self.register is False:
                    self.addLine(self.nick+"\nGeben Sie Ihr Passwort ein: ")
                else:
                    self.addLine(self.nick+"\nGeben Sie Ihr gewünschtes Passwort ein: ")
                self.Input.set_edit_text('*'*len(self.passwd))
                self.integer+=1
            elif self.integer==0:
                if key != 'shift tab':
                    if self.register is False:
                        self.addLine('*'*len(self.passwd)+"\nGeben Sie den Raum ein in den Sie joinen wollen: ")
                        self.Input.set_edit_text(self.room)
                    else:
                        self.addLine('*'*len(self.passwd)+"\nGeben Sie bitte ihre E-Mail-Adresse an: ")
                        self.Input.set_edit_text(self.mail)
                    self.integer+=1
                else:
                    if self.register is False:
                        self.addLine("\nGeben sie ihren Nicknamen ein: (Um einen neuen Nick zu registrieren drücken Sie Strg + R)")
                    else:
                        self.addLine("\nGeben Sie den gewünschen Nicknamen ein: (Drücken Sie Strg + L um sich einzuloggen)")
                    self.Input.set_edit_text(self.nick)
                    self.integer-=1
            elif self.integer==1:
                if key != 'shift tab':
                    if self.register is False:
                        self.room = self.Input.get_edit_text()
                        self.addLine(self.room+"\nLogging in")
                        self.room.strip()
                        re.sub("\s","",self.room)
                        self.nick.strip()
                        self.parent.sendLogin(self.nick,self.passwd,self.room)
                    else:
                        self.mail = self.Input.get_edit_text()
                        self.addLine("\nregister nick "+self.nick)
                        self.parent.registerNick(self.nick.strip(),self.passwd,self.mail.strip())
                    self.integer+=1
                    self.Input.set_edit_text("")
                else:
                    self.room = self.Input.get_edit_text()
                    if self.register is False:
                        self.addLine(self.nick+"\nGeben Sie Ihr Passwort ein: ")
                    else:
                        self.addLine(self.nick+"\nGeben Sie Ihr gewünschtes Passwort ein: ")
                    self.Input.set_edit_text('*'*len(self.passwd))
                    self.integer-=1
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
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
            elif self.integer == 0 and key not in ('up','down','page up','page down','tab','esc','insert') and key.split()[0] not in ('super','ctrl','shift','meta'):
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

class rattlekekzPrivTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)
        self.history=[""]
        self.count = -1

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))])
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Private Unterhaltung "+self.room)
        self.completion=[self.room[1:]]

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
        if key == 'ctrl d' and self.Input.get_edit_text() is "": # TODO: Find a good way to do this for all tabs
            self.onClose()
        if key == 'enter': 
            text = self.Input.get_edit_text()
            if text=="":
                return
            elif text.lower().startswith("/suspend"):
                self.parent.suspendView(text.lower()[9:])
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
            at=False
            input = self.Input.get_edit_text()
            input,crap=input[:self.Input.edit_pos].split(),input[self.Input.edit_pos:]
            if len(input) is not 0:
                nick = input.pop().lower()
                if nick.startswith("@"):
                    nick = nick[1:]
                    at=True
                solutions=[]
                if nick != "":
                    for i in self.completion:
                        if nick in str(i[:len(nick)]).lower():
                            solutions.append(i)
                    if len(solutions) != 0 and len(solutions) != 1:
                        self.addLine(" ".join(solutions))
                    elif len(solutions) is not 0:
                        if at:
                            solutions[0]="@"+solutions[0]
                        input.append(str(solutions[0]))
                        if len(input) is not 1:
                            self.Input.set_edit_text(" ".join(input)+" "+crap)
                        else:
                            self.Input.set_edit_text(" ".join(input)+", "+crap)
                        self.Input.set_edit_pos(len(self.Input.get_edit_text())-len(crap))
        else:
            self.keypress(size, key)

    def sendStr(self,string):
        """sends the string to the controller"""
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.sendStr(self.room,string)


class rattlekekzMsgTab(rattlekekzPrivTab):
    def buildOutputWidgets(self):
        self.Userlistarray=[urwid.Text('Userliste: ')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.Topictext=''
        self.Topic=urwid.Text(("dividerstate",""), "left", "clip")
        self.upperCol=urwid.Columns([("weight",4,self.Topic), self.upperDivider])
        self.hsizer=urwid.Columns([self.MainView, ("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' )),("fixed",18,self.Userlist)], 1, 0, 16)
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperCol, 'divider' )), self.hsizer,("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Raum: "+self.room)

    def listUser(self,users,color=True):
        """takes a list of users and updates the Userlist of the room"""
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
        """displays the topic in the upper Divider"""
        self.Topictext=topic
        self.Topic.set_text(("dividerstate",str("Topic: "+topic)))

    def onKeyPressed(self, size, key):
        rattlekekzPrivTab.onKeyPressed(self, size, key)
        if key in ('meta up', 'meta down'):
            self.Userlist.keypress(size, key.split()[1])

    def onClose(self):
        """sends a /part to the controller"""
        self.sendStr("/part")

class rattlekekzMailTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))])
        self.header.set_text("rattlekekz  (Beta: "+self.parent.revision+") - KekzMail")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def sendStr(self,string):
        stringlist=string.split(" ")
        if stringlist[0]==("/refresh"):
            self.parent.refreshMaillist()
        elif stringlist[0]==("/show"):
            self.parent.getMail(stringlist[1])
        elif stringlist[0]==("/del"):
            if stringlist[1]=="all":
                self.parent.deleteAllMails()
            else:
                self.parent.deleteMail(stringlist[1])
            self.parent.refreshMaillist()
        elif stringlist[0]==("/sendm"):
            if not len(stringlist)<3:
                user=stringlist[1]
                msg=" ".join(stringlist[2:])
                self.parent.sendMail(user,str(msg))
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
        rattlekekzBaseTab.onKeyPressed(self, size, key)
        if key == 'enter':
            self.MainView.set_focus(len(self.Output) - 1)
            text = self.Input.get_edit_text()
            if text=="":
                return
            elif text.lower().startswith("/suspend"):
                self.parent.suspendView(text.lower()[9:])
            elif text.lower().startswith("/close"):
                self.onClose()
            else:
                self.sendStr(str(text))
            self.Input.set_edit_text("")
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

class rattlekekzInfoTab(rattlekekzBaseTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Nachrichtenanzeige")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(None)
        self.set_focus('body')

    def onKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
        if key in ('page up', 'page down'):
            self.MainView.keypress(size, key)
        elif key=="q":
            self.onClose()

    def addWhois(self, nick, whois):
        """ add a line to the internal list of lines"""
        while len(self.Output) > self.parent.readhistory:
            del self.Output[0]
        whois.insert(0,("divider","Whois von "+nick))
        whois.append(("divider","Ende des Whois"))
        for i in whois:
            self.Output.append(urwid.Text(i))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

class rattlekekzSecureTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Nachrichtenanzeige")
        self.passwd=""

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
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
            self.MainView.set_focus(len(self.Output) - 1)
            self.parent.sendIdentify(self.passwd)
        else:
            if key not in ('up','down','page up','page down','tab','esc','insert') and key.split()[0] not in ('super','ctrl','shift','meta'):
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

class rattlekekzEditTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("rattlekekz (Beta: "+self.parent.revision+") - Profil editieren ")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        self.name,self.location,self.homepage,self.hobbies,self.signature=name,ort,homepage,hobbies,signature
        self.signature = re.subn("\\n","~n~",self.signature)[0]
        self.integer=0
        self.editPassword=False
        self.blind=False
        self.addLine("\n(Drücken Sie Strg + A um ihr Passwort zu ändern)\nName: ")
        self.Input.set_edit_text(self.parent.stringHandler(self.name))
        self.passwd=""

    def receivedPassword(self):
        self.integer=0
        self.editPassword=True
        self.blind=True
        self.addLine("\nGeben sie ihr altes Passwort ein: (Um um ihr Profil zu ändern drücken Sie Strg + E)")
        self.Input.set_edit_text("")
        self.passwd=""

    def onKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
        if key == 'backspace' and self.blind:
            if self.Input.edit_pos != 0:
                self.passwd = self.passwd[:self.Input.edit_pos-1]+self.passwd[self.Input.edit_pos:]
                self.Input.set_edit_text('*'*len(self.passwd))
                if self.Input.edit_pos != len(self.passwd):
                    self.Input.set_edit_pos(self.Input.edit_pos-1)
        elif key == 'delete' and self.blind:
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
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        elif key == 'home':
            self.Input.set_edit_pos(0)
        elif key == 'enter':
            self.onEnter()
        elif key == 'ctrl e':
            if self.editPassword is True:
                self.receivedProfile(self.name,self.location,self.homepage,self.hobbies,self.signature)
        elif key == 'ctrl a':
            if self.editPassword is False:
                self.receivedPassword()
        elif key == 'meta q':
            self.onClose()
        elif self.blind and key not in ('up','down','page up','page down','tab','esc','insert') and key.split()[0] not in ('super','ctrl','shift','meta'):
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

    def onEnter(self):
        self.MainView.set_focus(len(self.Output) - 1)
        if self.integer==0:
            if self.editPassword:
                self.oldPassword = self.passwd
                self.addLine("*"*len(self.oldPassword)+"\nGeben Sie Ihr neues Passwort ein: ")
                self.Input.set_edit_text("")
                self.passwd=""
            else:
                self.newName=self.Input.get_edit_text()
                self.addLine(self.newName+"\nOrt: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.location))
            self.integer+=1
        elif self.integer==1:
            if self.editPassword:
                self.newPassword = self.passwd
                self.addLine('*'*len(self.newPassword)+"\nWiederholen Sie Ihr neues Passwort: ")
                self.Input.set_edit_text("")
                self.passwd=""
            else:
                self.newLocation=self.Input.get_edit_text()
                self.addLine(self.parent.stringHandler(self.newLocation)+"\nHomepage: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.homepage))
            self.integer+=1
        elif self.integer==2:
            if self.editPassword:
                self.newPasswordagain = self.passwd
                self.addLine("*"*len(self.newPasswordagain))
                self.passwd=""
                if self.newPassword != self.newPasswordagain:
                    self.addLine("Passwörter nicht identisch")
                    self.receivedPassword()
                else:
                    self.parent.changePassword(self.oldPassword,self.newPassword)
                    self.Input.set_edit_text("")
                    self.passwd=""
                    self.integer=-1
                    self.blind=False
            else:
                self.newHomepage=self.Input.get_edit_text()
                self.addLine(self.parent.stringHandler(self.newHomepage)+"\nHobbies: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.hobbies))
                self.integer+=1
        elif self.integer==3:
            self.newHobbies=self.Input.get_edit_text()
            self.addLine(self.parent.stringHandler(self.newHobbies)+"\nFreitext: (~n~ für Zeilenumbrüche)")
            self.Input.set_edit_text(self.parent.stringHandler(self.signature))
            self.integer+=1
        elif self.integer==4:
            self.newSignature=re.subn("~n~","\\n",self.Input.get_edit_text())[0]
            self.addLine(self.parent.stringHandler(self.newSignature)+"\nPasswort zum bestätigen: ")
            self.Input.set_edit_text("")
            self.blind=True
            self.integer+=1
        elif self.integer==5:
            self.addLine("*"*len(self.passwd)+"\nÄndere Profil...")
            self.parent.updateProfile(self.newName,self.newLocation,self.newHomepage,self.newHobbies,self.newSignature,self.passwd)
            self.Input.set_edit_text("")
            self.passwd=""
            self.integer=-1
            self.blind=False
