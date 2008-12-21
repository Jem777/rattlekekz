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
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        self.y,self.x,self.cline,self.uline = self.scrn.getmaxyx()[0],self.scrn.getmaxyx()[1],0,0
        self.scrn.vline(1,self.x-18,0,self.y-3)
        self.current = curses.newpad(200,self.x-18)
        self.userlist = curses.newpad(50,16)
        self.textparent = curses.newwin(1,self.x,self.y-2,0)
        self.textinput = textpad.Textbox(self.textparent)
        self.scrn.refresh()
        self.textparent.refresh()

    def receivedPreLoginData(self,rooms,array):
        pass

    def listUser(self,room,users):
        for i in users:
            self.userlist.addstr(self.uline,0,i[0],curses.color_pair(1))
            self.uline = self.uline+1
        self.userlist.refresh(self.uline-self.y-3,0,1,self.x-17,self.y-3,self.x-1)

    def printMsg(self,nick,msg,channel,status):
        self.current.addstr(self.cline,0,nick+': '+msg)
        self.current.refresh(self.cline-self.y-3,0,1,0,self.y-3,self.x-19)
        self.cline=self.cline+1