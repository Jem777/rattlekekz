#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses import textpad
from hashlib import sha1 #the hash may be moved to controller

    #clientident="" #"Ze$8hAbeVe0y" das muss später alles weg
    #verInt=""      #"0"
    #netVer=""      #"netkekZ4 beta 20080910"

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        self.buildDisplay()
    
    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()
    
    def buildDisplay(self):
        self.scrn = curses.initscr()
        self.y,self.x,self.line = self.scrn.getmaxyx()[0],self.scrn.getmaxyx()[1],0
        x,y = self.x,self.y
        self.scrn.vline(1,x-18,0,y-3)
        self.current = curses.newpad(200,x-16)
        self.userlist = curses.newpad(50,16)
        self.textparent = curses.newwin(1,x,y-2,0)
        self.textinput = textpad.Textbox(self.textparent)
        self.scrn.refresh()
        self.textparent.refresh()

    def receivedPreLoginData(self,rooms,array):
        pass

    def printMsg(self, nick, msg, channel):
        y,x = self.y,self.x
        self.current.addstr(self.line,0,nick+': '+msg)
        self.current.refresh(self.line-y-3,0,2,0,y-3,x-19)
        self.line=self.line+1