#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor
import urwid
from urwid import raw_display, main_loop
import locale

    #clientident="" #"Ze$8hAbeVe0y" das muss später alles weg
    #verInt=""      #"0"
    #netVer=""      #"netkekZ4 beta 20080910"

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        self.buildDisplay()
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()
        Input(self.controller)

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes""" # TODO: alter this function to remove the return
        return "".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))

    def buildDisplay(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        pass

    def listUser(self,room,users):
        pass

    def printMsg(self,nick,msg,channel,status):
        pass

    def successLogin(self,nick,status,room):
        pass

    def newTopic(self,room,topic):
        pass

    def receivedPing(self, deltaPing):
        pass

class Input:
    def __init__(self,controller):
        self.term = urwid.raw_display.Screen()
        self.controller = controller
        self.size = self.term.get_cols_rows()
        self.input = urwid.Edit()
        self.filler = urwid.Filler(self.input)
        self.canvas = self.filler.render( self.size, focus=True )
        self.term.draw_screen(self.size,self.canvas)
        reactor.addReader(self)

    def fileno(self):
        return 0

    def logPrefix(self):
        return 'CursesClient'

    def doRead(self):
        keys = self.term.get_input_nonblocking()
        for key in keys:
            if key == 'window resize':
                self.size = self.term.get_cols_rows()
            elif key == 'enter':
                text = self.input.get_edit_text()
                controller.sendMsg('dev',text)
                self.input.set_edit_text('')
            else:
                self.filler.keypress(self.size, key)