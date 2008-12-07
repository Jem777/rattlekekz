#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, cli

#modell = kekzprotocol(self)
#view = view(self)

class Kekzcontroller():
    def __init__(self):
        self.modell = kekzprotocol.KekzClient(self)
        self.view = cli.View(self)
    
    def startConnection(self,server,port):
        self.modell.startConnection(server,port)
    
    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.modell.sendHandshake(self.view.foobar())
    
    def receivedHandshake(self):
        self.modell.sendDebugInfo()
        
    
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
    
    def unknownMethod(self):
        print "Shit happens: The Controller wasn't able to respond to a call from the server"

    def __getattr__(self, name):
        return self.unknownMethod    