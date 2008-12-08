#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, cli
import os, sys, xreadlines

#modell = kekzprotocol(self)
#view = view(self)

class Kekzcontroller():
    def __init__(self):
        self.model = kekzprotocol.KekzClient(self)
        self.view = cli.View(self)
    
    def startConnection(self,server,port):
        self.model.startConnection(server,port)
    

    def readConfigfile(self):
        configfile=os.environ["HOME"]+os.sep+".keckz"
        if os.path.exists(self.config) == False:
            file=open(configfile, "w")
            file.write("# Das ist die KECKz Konfigurationsdatei, für nähere Infos siehe 'man keckz'")
        file=open(configfile)
        array=file.readlines()
        dictionary={}
        for i in array:
            if a.isspace() == False or a.startswith("#")==False or a.find("=")==-1:
                a=i.split("=")
                a=a[:2]
                dic.update({a[0].strip():a[1].strip()})


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