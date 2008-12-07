#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, cli
import sys

#modell = kekzprotocol(self)
#view = view(self)

class Kekzcontroller():
    def __init__(self):
        self.model = kekzprotocol.KekzClient(self)
        self.view = cli.View(self)
    
    def startConnection(self,server,port):
        self.model.startConnection(server,port)
    
    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.model.sendHandshake(self.view.foobar())
    
    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.View.name,self.View.version,sys.platform,"Python "+pythonversion[0])
        self.model.getRooms()
    
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