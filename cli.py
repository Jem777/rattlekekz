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
        scrn = curses.initscr()
        y,x,line = scrn.getmaxyx()[0],scrn.getmaxyx()[1],0
        scrn.vline(1,x-18,0,y-3)
        current = curses.newpad(200,x-16)
        userlist = curses.newpad(50,16)
        textparent = curses.newwin(1,x,y-2,0)
        input = textpad.Textbox(textparent)
        scrn.refresh()
        textparent.refresh()

    def receivedPreLoginData(self,rooms,array):
        pass

    def printMsg(self, nick, msg, channel):
        self.current.addstr(self.line,0,nick+': '+msg)
        self.current.refresh(self.line-self.y-3,0,2,0,self.y-3,self.x-19)
        self.line=self.line+1