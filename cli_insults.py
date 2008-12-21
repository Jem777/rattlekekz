#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.conch.insults import insults
from hashlib import sha1 #the hash may be moved to controller

class View:
    def __init__(self,controller):
        self.controller=controller
        self.name,self.version="KECKz","0.0"
        self.buildDisplay()
    
    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return sha1("".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))).hexdigest()
    
    def buildDisplay(self):
        pass

    def receivedPreLoginData(self,rooms,array):
        pass

    def listUser(self,room,users):
        pass

    def printMsg(self,nick,msg,channel,status):
        pass