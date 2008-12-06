#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, view

#modell = kekzprotocol(self)
#view = view(self)

class Kekzcontroller():
    def __init__(self,Object):
        self.modell = kekzprotocol(self)
        self.view = view(self)
    
    def receivedHandshake(self):
        pass
    
    def receivedRooms(self,rooms):
        pass
    
    def successLogin(self,nick,status,room):
        pass
    
    def successRegister(self):
        pass
    
    def successNewPassword(self):
        pass
    
    def receivedProfil(self,name,ort,homepage,hobbies):
        pass
    
    def successNewProfile(self):
        pass
    
    def receivedPing(self,deltaPing):
        pass
    
    def receivedMsg(self,nick,channel,msg):
        pass
    
    def privMsg(self,nick,msg):
        pass
    
    def botMsg(self,nick,msg):
        pass
    
    def Error(message):
        pass