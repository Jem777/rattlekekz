#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
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
        y,x = scrn.getmaxyx()[0],scrn.getmaxyx()[1]
        curses.newwin(3,x,0,0).box()
        curses.newwin(y-6,18,2,y-18).box()
        curses.newwin(3,x,y-3,0).box()
        curses.newwin(y-4,x-17,2,0)
        scrn.refresh()