#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses

    #clientident="" #"Ze$8hAbeVe0y" das muss später alles weg
    #verInt=""      #"0"
    #netVer=""      #"netkekZ4 beta 20080910"

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
    
    def foobar():
        """This function sends bullshit to the controller for debugging purposes"""
        sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()
    
    def buildDisplay():
        screen=curses.initscr()
        screen.newpad(1,1)