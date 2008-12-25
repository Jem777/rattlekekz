#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from twisted.internet import reactor
from hashlib import sha1 #the hash may be moved to controller

    #clientident="" #"Ze$8hAbeVe0y" das muss später alles weg
    #verInt=""      #"0"
    #netVer=""      #"netkekZ4 beta 20080910"

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        self.scrn = curses.initscr()
        self.scrn.nodelay(1) # this is used to make input cfls non-blocking
        curses.cbreak()
        self.scrn.keypad(1)
        self.rows, self.cols = self.scrn.getmaxyx() # TODO: reconsider this
        self.lines = []                               # TODO: and this too
        self.searchText = ''
        #curses.start_color() # TODO: This have to be implemented later on.
        reactor.addReader(self)

    def receivedPreLoginData(self,rooms,array):
        pass

    def listUser(self,room,users):
        pass

    def printMsg(self,nick,channel,msg,flag):
        pass

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()

    def addLine(self, text): # TODO: replace this method with a better one.
        """ add a line to the internal list of lines"""
        self.lines.append(text)
        self.redisplayLines()

    def redisplayLines(self):
        """ method for redisplaying lines 
            based on internal list of lines """
        self.scrn.clear()
        i = 0
        index = len(self.lines) - 1
        while i < (self.rows - 3) and index >= 0:
            self.scrn.addstr(self.rows - 3 - i, 0, self.lines[index], 
                               curses.color_pair(2))
            i = i + 1
            index = index - 1
        self.scrn.refresh()

    def doRead(self):
        """ Input is ready! """
        curses.noecho()
        c = self.scrn.getch() # read a character

        if c == curses.KEY_BACKSPACE:
            self.searchText = self.searchText[:-1]

        elif c == curses.KEY_ENTER or c == 10:
            try: self.controller.sendMsg('dev', self.searchText)
            except: pass
            self.scrn.refresh()
            self.searchText = ''

        else:
            if len(self.searchText) == self.cols-2: return
            self.searchText = self.searchText + chr(c)

        self.scrn.addstr(self.rows-1, 0, 
                           self.searchText + (' ' * (
                           self.cols-len(self.searchText)-2)))
        self.scrn.move(self.rows-1, len(self.searchText))
        self.scrn.refresh()

    def connectionLost(self,reason):
        pass

    def close(self):
        """ clean up """

        curses.nocbreak()
        self.scrn.keypad(0)
        curses.echo()
        curses.endwin()

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self):
        return 'View' #we may change this later. who knows?