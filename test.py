#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses import ascii, textpad
from hashlib import sha1
import time

class view():
    def __init__(self,controller):
        self.controller=controller
        #self.buildInterface()
    
    def buildInterface(self):
        screen=curses.initscr()
        x=int(screen.getmaxyx()[1])
        y=int(screen.getmaxyx()[0])
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        users=curses.newwin(y-3,18,0,x-18)
        users.box()
        chat=curses.newwin(y-3,x-18,0,0)
        chat.box()
        text=curses.newwin(3,x,y-3,0)
        textpad.Textbox(text)
        users.refresh()
        text.refresh()
    
    def exitInterface(self):
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()

    def displayMsg(self,msg):
        print msg+'\n'

    def foobar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()
    