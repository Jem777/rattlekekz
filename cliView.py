#!/usr/bin/env python
# -*- coding: utf-8 -*-


import controllerKeckz

# Urwid
import urwid
from urwid import curses_display

# Twisted imports

from twisted.internet import reactor, ssl


class TextTooLongError(Exception):
    pass

class View:
    def __init__(self, controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        tui = curses_display.Screen()
        colors =[('normal','default','default'), # TODO: More colors
            ('admin','dark red','default'),
            ('chatop','yellow','default'),
            ('roomop','dark blue','default'),
            ('special','dark green','default'),
            ('user','white','default'),
            ('adminaway','dark red','light gray'),
            ('chatopaway','yellow','light gray'),
            ('roomopaway','dark blue','light gray'),
            ('specialaway','dark green','light gray'),
            ('useraway','white','light gray')]
        tui.register_palette(colors)
        reactor.addReader(self)
        reactor.callWhenRunning(self.init)
        self.tui = tui
        self.lookupRooms={}


    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return "".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))


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
                self.lookupRooms[self.ShownRoom].OnKeyPressed(self.size, key)
        self.redisplay()

    def successLogin(self,nick,status,room):
        self.ShownRoom=room
        self.lookupRooms.update({room:KeckzMsgTab(room,self)})
        self.lookupRooms[self.ShownRoom].addLine("Logged successful in as "+nick+"\nJoined room "+room)

    def receivedPing(self,deltaPing):
        self.lookupRooms[self.ShownRoom].addLine("Ping: "+str(deltaPing)+"ms")

    def printMsg(self,nick,msg,room,state):
        if state==0 or state==2 or state==4:
            msg=nick+": "+msg
        elif state==3:
            msg=self.nickname+": "+msg
            
        if state==2 or state==3:
            room="#"+nick
            if self.lookupRooms.has_key(room)==False:
                self.lookupRooms.update({room:KeckzPrivTab(room, self)})
        if state==4:
            room=self.ShownRoom
        self.lookupRooms[room].addLine(msg)
        """text,format=controllerKeckz.decode(msg)        #TODO this is just how it work in wxView
        for i in range(len(text)):
            form=format[i].split(",")
            styleTupel=wx.TextAttr()
            wxFont=wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
            if "bold" in form:
                wxFont.SetWeight(wx.BOLD)
            if "italic" in form:
                wxFont.SetStyle(wx.ITALIC)
            for a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow"]:
                if a in form:
                    styleTupel.SetTextColour(a.upper())
                else:
                    styleTupel.SetTextColour("BLACK")
            if "imageurl" in form:
                pass
            styleTupel.SetFont(wxFont)
            self.lookupRooms[room].addLine(text[i])
            #room.printMsg(text[i],styleTupel)"""

    def gotException(self, message):
        self.lookupRooms[self.ShownRoom].addLine("Fehler: "+message)

    def listUser(self,room,users):
        self.lookupRooms[room].listUser(users)

    def meJoin(self,room,background):
        self.lookupRooms.update({room:KeckzMsgTab(room, self)})
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
        self.ShownRoom=newroom
        del self.lookupRooms[oldroom]
        self.redisplay()

    def newTopic(self,room,topic):
        self.lookupRooms[room].addLine("Neues Topic: "+topic)

    def loggedOut(self):
        pass

    def receivedInformation(self,info):
        self.lookupRooms[self.ShownRoom].addLine("Infos: "+info)

    def receivedWhois(self,nick,array):
        pass

    def connectionLost(self, failure):
        pass

class KeckzBaseTab(urwid.Frame):
    def __init__(self, room, parent):
        """This is the base-class of tabs, all the other tabs
        are going to be derived"""

class KeckzMsgTab(KeckzBaseTab):
    def __init__(self, room, parent):
        self.room=room
        self.parent=parent
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.Userlistarray=[urwid.Text('Userliste: ')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.sizer=urwid.Columns([self.MainView,("fixed",18,self.Userlist)], 1, 0, 16)
        self.Input = urwid.Edit()
        self.header=urwid.Text("KECKz - Raum: "+self.room,"center")
        self.set_header(self.header)
        self.set_body(self.sizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def listUser(self,users):
        self.completion=[]
        for i in range(0,len(self.Userlistarray)):
            del(self.Userlistarray[0])
        self.Userlistarray.append(urwid.Text('Userliste: '))
        for i in users:
            self.completion.append(i[0])
            if i[2] in 'x':
                self.color='user'
            elif i[2] in 's':
                self.color='special'
            elif i[2] in 'c':
                self.color='roomop'
            elif i[2] in 'o':
                self.color='chatop'
            elif i[2] in 'a':
                self.color='admin'
            if i[1] == True:
                self.color=self.color+'away'
            self.Userlistarray.append(painter(i[0],self.color))
            self.Userlist.set_focus(len(self.Userlistarray) - 1)
        self.parent.redisplay()

    def OnKeyPressed(self, size, key):
        if key == 'enter':
            text = self.Input.get_edit_text()
            self.Input.set_edit_text('')
            self.parent.controller.sendMsg(str(self.room),str(text))
        elif key == 'tab': # TODO: work something out for inline nick-completion
            input = self.Input.get_edit_text().split()
            nick = input.pop().lower()
            solutions=[]
            for i in self.completion:
                if nick in i[:len(nick)].lower():
                    solutions.append(i)
            if len(solutions) is not (0 or 1):
                self.addLine(" ".join(solutions))
            elif len(solutions) is not 0:
                input.append(solutions[0])
                self.Input.set_edit_text(" ".join(input))
                self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        elif key in ('up', 'down', 'page up', 'page down'):
            self.MainView.keypress(size, key)
        else:
            self.keypress(size, key)

class KeckzPrivTab(KeckzBaseTab):
    def __init__(self, room, parent):
        pass

class painter(urwid.WidgetWrap): # TODO remove unneeded attributes
      def __init__(self, text, color):
          w = urwid.Text(text)
          w = urwid.AttrWrap(w, color, color)
          urwid.WidgetWrap.__init__(self, w)
      def selectable(self):
          return True

if __name__ == '__main__':

    kekzControl=controllerKeckz.Kekzcontroller(View)
    kekzControl.view.startConnection("kekz.net",23002)
