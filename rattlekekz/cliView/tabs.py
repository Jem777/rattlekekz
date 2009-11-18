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

def stringHandler(string):
    if type(string) is unicode:
        return string.encode("utf_8")
    else:
        return str(string)

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
        self.header = titleWidget("rattlekekz","0.99")
        
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
        if key == 'ctrl d':
            self.onClose()
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

class titleWidget(urwid.Text):
    def __init__(self, name = "", version = "", tabname = ""):
        self.name = name
        self.version = version
        self.tabname = tabname
        self.formatstring = "%s (v %s) - %s"
        title = self.formatstring % (self.name, self.version, self.tabname)
        urwid.Text.__init__(self, title, "center")

    def set_text(self, tabname):
        self.tabname = tabname
        title = self.formatstring % (self.name, self.version, self.tabname)
        urwid.Text.set_text(self, title)

class editWidget(urwid.Edit):
    def __init__(self, parent):
        self.parent = parent
        urwid.Edit.__init__(self)
        self.history = [""]
        self.count = 0
        self.tab = False

    def keypress(self, size, key):
        if key == 'tab':
            pos = self.edit_pos
            text = self.get_edit_text()
            before = stringHandler(text[:pos])
            after = stringHandler(text[pos:])
            self.tabcompletion(before, after)
            return
        self.tab = False
        if key == 'enter':
            text = self.get_edit_text()
            self.set_edit_text('')
            self.sendStr(text)
        elif key == 'up':
            self.scrollUp()
        elif key == 'down':
            self.scrollDown()
        else:
            urwid.Edit.keypress(self, size, key)

    def scrollUp(self):
        if self.count != 0: 
            text = self.get_edit_text()
            self.history[self.count] = text
            self.count -= 1
            new_text = self.history[self.count]
            self.set_edit_text(new_text)
            self.set_edit_pos(len(new_text))

    def scrollDown(self):
        if self.count != (len(self.history)-1):
            text = self.get_edit_text()
            self.history[self.count] = text
            self.count += 1
            new_text = self.history[self.count]
            self.set_edit_text(new_text)
            self.set_edit_pos(len(new_text))

    def tabcompletion(self, before, after):
        if self.tab == True:
            self.parent.addLine(" ".join(self.solutions))
            return
        listofwords = before.split(" ")
        word = listofwords.pop()
        if len(listofwords) == 0:
            bol = True
        else:
            bol = False
            prefix = " ".join(listofwords)
        all = self.parent.getSolutions(bol)
        solutions = filter(lambda x: x.lower().startswith(word.lower()), all)
        if len(solutions) == 1:
            new_word = solutions[0]
            if bol:
                before = new_word
            else:
                before = prefix + " " + new_word
            self.set_edit_text(before + after)
            self.set_edit_pos(len(before))
            self.tab = False
        elif len(solutions) == 0:
            self.tab = False
        else:
            new_word = self.trySolutions(word, solutions)
            if word == new_word:
                self.solutions = solutions
                self.tab = True
            else:
                if bol:
                    before = new_word
                else:
                    before = prefix + " " + new_word
                self.set_edit_text(before + after)
                self.set_edit_pos(len(before))
                self.tab = False

    def trySolutions(self, before, solutions):
        index = len(before)
        for i in solutions[1:]:
            try:
                if solutions[0][index].lower() != i[index].lower():
                    return before
            except IndexError:
                if len(solutions[0]) < len(i):
                    return solutions[0]
                else:
                    return i
        before += solutions[0][index]
        return self.trySolutions(before, solutions)

    def sendStr(self, string):
        """sends the string to the tab"""
        if string.strip() == "":
            return
        self.parent.sendStr(str(string))
        if self.count != (len(self.history)-1):
            del self.history[self.count]
        del self.history[-1]
        self.history.append(string)
        self.history.append("")
        self.count = (len(self.history)-1)
        self.set_edit_text("")

class rattlekekzLoginTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)
        self.hasInput = True

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile([
            ("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), 
            self.MainView,
            ("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))
            ])
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("welcome at kekznet | "+self.room)

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
            self.addLine("\nplease enter your nickname: (to register a new nickname press ctrl + r)")
        else:
            self.addLine("\nenter your nickname:")
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
        self.addLine("\nenter your nickname: (to register a new nickname press ctrl + r)")

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
                    self.addLine(self.nick+"\nenter your password: ")
                else:
                    self.addLine(self.nick+"\nenter a password: ")
                self.Input.set_edit_text('*'*len(self.passwd))
                self.integer+=1
            elif self.integer==0:
                if key != 'shift tab':
                    if self.register is False:
                        self.addLine('*'*len(self.passwd)+"\nenter a room you want to join: ")
                        self.Input.set_edit_text(self.room)
                    else:
                        self.addLine('*'*len(self.passwd)+"\nenter your mail-adress: ")
                        self.Input.set_edit_text(self.mail)
                    self.integer+=1
                else:
                    if self.register is False:
                        self.addLine("\nenter your nickname: (to register a new nickname press ctrl + r)")
                    else:
                        self.addLine("\nenter a nickname: (press ctrl + L for login)")
                    self.Input.set_edit_text(self.nick)
                    self.integer-=1
            elif self.integer==1:
                if key != 'shift tab':
                    if self.register is False:
                        self.room = self.Input.get_edit_text()
                        self.addLine(self.room+"\nlogging in")
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
                        self.addLine(self.nick+"\nenter your password: ")
                    else:
                        self.addLine(self.nick+"\nenter a password: ")
                    self.Input.set_edit_text('*'*len(self.passwd))
                    self.integer-=1
            self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        else:
            if key == 'ctrl r':
                if self.register is False:
                    self.integer,self.register=-1,True
                    self.nick,self.passwd,self.mail='','',''
                    self.addLine("\nenter a nickname: (press ctrl + l for login)")
            elif key == 'ctrl l':
                if self.register is True:
                    self.integer,self.register=-1,False
                    self.nick,self.passwd,self.room='','',''
                    self.addLine("\nenter your nickname: (to register a new nickname press ctrl + r)")
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
        self.Input = editWidget(self)
        rattlekekzBaseTab.__init__(self,room, parent)
        self.hasInput = True

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile([
            ("flow",urwid.AttrWrap(self.upperDivider, 'divider')), 
            self.MainView, 
            ("flow",urwid.AttrWrap(self.lowerDivider, 'divider'))
            ])
        self.header.set_text("private conversation "+self.room)
        self.completion=[self.room[1:]]

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        rattlekekzBaseTab.onKeyPressed(self, size, key)
        self.keypress(size, key)

    def sendStr(self,string):
        """sends the string to the controller"""
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.sendStr(self.room,string)

    def getSolutions(self, bol = True):
        if bol:
            solutions = map(lambda x: stringHandler(x + ", "), self.completion)
            return solutions
        else:
            solutions = map(lambda x: stringHandler(x), self.completion)
            return solutions

class rattlekekzMsgTab(rattlekekzPrivTab):
    def buildOutputWidgets(self):
        self.Userlistarray=[urwid.Text('Userliste: ')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.Topictext=''
        self.Topic=urwid.Text(("dividerstate",""), "left", "clip")
        self.upperCol=urwid.Columns([("weight",4,self.Topic), self.upperDivider])
        self.hsizer=urwid.Columns([self.MainView, ("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' )),("fixed",18,self.Userlist)], 1, 0, 16)
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperCol, 'divider' )), self.hsizer,("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("room: "+self.room)

    def listUser(self,users,color=True):
        """takes a list of users and updates the Userlist of the room"""
        self.completion=[]
        for i in range(0,len(self.Userlistarray)):
            del(self.Userlistarray[0])
        self.Userlistarray.append(urwid.Text('userlist: '))
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
                if i[1]:
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
                if i[1]:
                    self.Userlistarray.append(urwid.Text(self.color+"("+i[0]+")"))
                else:
                    self.Userlistarray.append(urwid.Text(self.color+i[0]))
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

class rattlekekzMailTab(rattlekekzPrivTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile([
            ("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), 
            self.MainView,
            ("flow",urwid.AttrWrap( self.lowerDivider, 'divider'  ))
            ])
        self.header.set_text("KekzMail")
        solutions = ["/help", "/del", "/show", "/sendm", "/refresh"]
        solutions = map(lambda x: stringHandler(x), solutions)
        solutions.sort()
        self.completion = solutions

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def sendStr(self,string):
        stringlist=string.split(" ")
        stringlist[0] = stringlist[0].lower()
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
        refresh mails: /refresh
        show mail: /show index
        delete mail: /del index 
        delete all readed mails: /del all 
        send mail: /sendm nick msg""")
        elif stringlist[0] == ("/suspend"):
            self.parent.suspendView(" ".join(stringlist[1:]))
        elif stringlist[0] == ("/close"):
            self.onClose()
        else:
            self.addLine("you've entered a invalid comand")

    def getSolutions(self, bol = True):
        return self.completion

class rattlekekzInfoTab(rattlekekzBaseTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("information")

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
        whois.insert(0,("divider","whois of "+nick))
        whois.append(("divider","end of whois"))
        for i in whois:
            self.Output.append(urwid.Text(i))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

class rattlekekzSecureTab(rattlekekzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        rattlekekzBaseTab.__init__(self,room, parent)
        self.hasInput = True

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView, ("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.header.set_text("secure identify")
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
        self.hasInput = True

    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("flow",urwid.AttrWrap( self.lowerDivider, 'divider' ))])
        self.hasOutput=False
        self.hasInput=True
        self.header.set_text("edit profile")

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
        self.addLine("\n(press ctrl + a to change your password)\nname: ")
        self.Input.set_edit_text(self.parent.stringHandler(self.name))
        self.passwd=""

    def receivedPassword(self):
        self.integer=0
        self.editPassword=True
        self.blind=True
        self.addLine("\nenter your old password: (to edit your profile press ctrl + e)")
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
                self.addLine("*"*len(self.oldPassword)+"\nenter your new password: ")
                self.Input.set_edit_text("")
                self.passwd=""
            else:
                self.newName=self.Input.get_edit_text()
                self.addLine(self.newName+"\nlocation: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.location))
            self.integer+=1
        elif self.integer==1:
            if self.editPassword:
                self.newPassword = self.passwd
                self.addLine('*'*len(self.newPassword)+"\nretype your new password: ")
                self.Input.set_edit_text("")
                self.passwd=""
            else:
                self.newLocation=self.Input.get_edit_text()
                self.addLine(self.parent.stringHandler(self.newLocation)+"\nhomepage: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.homepage))
            self.integer+=1
        elif self.integer==2:
            if self.editPassword:
                self.newPasswordagain = self.passwd
                self.addLine("*"*len(self.newPasswordagain))
                self.passwd=""
                if self.newPassword != self.newPasswordagain:
                    self.addLine("passwords do not match")
                    self.receivedPassword()
                else:
                    self.parent.changePassword(self.oldPassword,self.newPassword)
                    self.Input.set_edit_text("")
                    self.passwd=""
                    self.integer=-1
                    self.blind=False
            else:
                self.newHomepage=self.Input.get_edit_text()
                self.addLine(self.parent.stringHandler(self.newHomepage)+"\nhobbies: ")
                self.Input.set_edit_text(self.parent.stringHandler(self.hobbies))
                self.integer+=1
        elif self.integer==3:
            self.newHobbies=self.Input.get_edit_text()
            self.addLine(self.parent.stringHandler(self.newHobbies)+"\nsignature: (~n~ for newlines)")
            self.Input.set_edit_text(self.parent.stringHandler(self.signature))
            self.integer+=1
        elif self.integer==4:
            self.newSignature=re.subn("~n~","\\n",self.Input.get_edit_text())[0]
            self.addLine(self.parent.stringHandler(self.newSignature)+"\npassword for validation: ")
            self.Input.set_edit_text("")
            self.blind=True
            self.integer+=1
        elif self.integer==5:
            self.addLine("*"*len(self.passwd)+"\nchanging profile ...")
            self.parent.updateProfile(self.newName,self.newLocation,self.newHomepage,self.newHobbies,self.newSignature,self.passwd)
            self.Input.set_edit_text("")
            self.passwd=""
            self.integer=-1
            self.blind=False
