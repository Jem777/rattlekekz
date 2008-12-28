#!/usr/bin/env python
# -*- coding: utf-8 -*-


import controllerKeckz

# Urwid
import urwid
import urwid.curses_display

# Twisted imports

from twisted.internet import reactor, ssl


class TextTooLongError(Exception):
    pass

class View:
    def __init__(self, controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        tui = urwid.curses_display.Screen()
    
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

    def startConnection(self):
        reactor.connectSSL("kekz.net", 23002, self.controller.model, ssl.ClientContextFactory())
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
            elif key == "ctrl n":
                array=self.lookupRooms.keys()
                index=array.index(self.ShownRoom)
                self.ShownRoom=array[index+1]
                self.lookupRooms[self.ShownRoom]
            else:
                self.lookupRooms[self.ShownRoom].OnKeyPressed(self.size, key)
        self.redisplay()

    def successLogin(self,nick,status,room):
        self.ShownRoom=room
        self.lookupRooms.update({room:KeckzTabs(room,self)})
        self.lookupRooms[self.ShownRoom].addLine("Logged successful in as "+nick+"\nJoined room "+room)

    def receivedPing(self,deltaPing):
        self.lookupRooms[self.ShownRoom].addLine("Ping: "+str(deltaPing)+"ms")

    def printMsg(self,nick,msg,channel,state):
        if state==0 or state==2 or state==4:
            msg=nick+": "+msg
        self.lookupRooms[self.ShownRoom].addLine(msg)

    def gotException(self, message):
        self.lookupRooms[self.ShownRoom].addLine("Fehler: "+message)

    def listUser(self,room,users):
        self.lookupRooms[self.ShownRoom].listUser(users)

    def meJoin(self,room,background):
        pass

    def mePart(self,room):
        pass

    def meGo(self,oldroom,newroom):
        pass

    def newTopic(self,room,topic):
        self.lookupRooms[self.ShownRoom].addLine("Neues Topic: "+topic)

    def loggedOut(self):
        pass

    def receivedInformation(self,info):
        self.lookupRooms[self.ShownRoom].addLine("Infos: "+info)

    def receivedWhois(self,nick,array):
        pass

    def connectionLost(self, failure):
        pass

class KeckzTabs(urwid.Frame):
    def __init__(self, room, parent, *args, **kwds):
        self.room=room
        self.parent=parent
        self.Output = [urwid.Text('starting KECKz...')]
        self.MainView = urwid.ListBox(self.Output)
        self.Userlistarray = [urwid.Text('Userliste')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.sizer=urwid.Columns([self.MainView,self.Userlist], 1, 0, 16)
        self.Input = urwid.Edit()
        self.set_header(None)
        self.set_body(self.sizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def listUser(self,users): #Doesn't work by now
        self.Userlistarray = [urwid.Text('Userliste:')]
        for i in range(len(users)):
            self.Userlistarray.append(urwid.Text(users[i][0]))
            self.Userlist.set_focus(len(self.Userlistarray) - 1)
        self.parent.redisplay()

    def OnKeyPressed(self, size, key):
        if key == 'enter':
            text = self.Input.get_edit_text()
            self.Input.set_edit_text('')
            self.parent.controller.sendMsg(self.room,text)
        elif key in ('up', 'down', 'page up', 'page down'):
            self.MainView.keypress(self.size, key)
        else:
            self.keypress(size, key)

if __name__ == '__main__':

    kekzControl=controllerKeckz.Kekzcontroller(View)
    kekzControl.view.startConnection()
