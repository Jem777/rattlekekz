#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import locale
from curses import textpad
from twisted.internet import reactor
from hashlib import sha1 #the hash may be moved to controller

    #clientident="" #"Ze$8hAbeVe0y" das muss später alles weg
    #verInt=""      #"0"
    #netVer=""      #"netkekZ4 beta 20080910"

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        self.buildDisplay()
        Input(self.controller,self.y,self.x)
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()
    
    def buildDisplay(self):
        self.scrn = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        self.y,self.x,self.cline,self.uline = self.scrn.getmaxyx()[0],self.scrn.getmaxyx()[1],0,0
        self.scrn.vline(1,self.x-18,0,self.y-3)
        self.scrn.hline(self.y-3,0,0,self.x)
        self.current = curses.newpad(200,self.x-18)
        self.userlist = curses.newpad(50,16)
        self.scrn.refresh()

    def receivedPreLoginData(self,rooms,array):
        pass

    def listUser(self,room,users):
        for i in users:
            self.userlist.addstr(self.uline,0,i[0],curses.color_pair(1))
            self.uline = self.uline+1
        self.userlist.refresh(self.uline-self.y-4,0,1,self.x-17,self.y-4,self.x-1)

    def printMsg(self,nick,msg,channel,status):
        string = nick+': '+msg
        self.current.addstr(self.cline,0,string.encode(self.code))
        self.current.refresh(self.cline-self.y-4,0,1,0,self.y-4,self.x-19)
        self.cline=self.cline+1+(len(string)/(self.x-18))

class Input:
    def __init__(self,controller,y,x):
        self.controller = controller
        self.input = curses.newwin(1,x,y-2,0)
        self.input.keypad(1)
        self.input.nodelay(1)
        curses.cbreak()
        self.y,self.x = self.input.getmaxyx()
        self.searchText = ''
        reactor.addReader(self)

    def doRead(self):
        curses.noecho()
        c = self.input.getch() # read a character

        if c == curses.KEY_BACKSPACE or c == 127:
            self.searchText = self.searchText[:-1]

        elif c == curses.KEY_ENTER or c == 10:
            self.controller.sendMsg('dev', self.searchText)
            self.input.refresh()
            self.searchText = ''

        else:
            if len(self.searchText) == self.x-2: return
            self.searchText = self.searchText + chr(c)

        self.input.addstr(self.y-1, 0, 
                           self.searchText + (' ' * (
                           self.x-len(self.searchText)-2)))
        self.input.move(0, len(self.searchText))
        self.input.refresh()

    def connectionLost(self,reason):
        pass

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self):
        return 'View' #we may change this later. who knows?