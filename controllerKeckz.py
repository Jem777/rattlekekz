#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, cli, test
import os, sys

#modell = kekzprotocol(self)
#view = view(self)

class Kekzcontroller():
    def __init__(self):
        self.model = kekzprotocol.KekzClient(self)
        #self.view = cli.View(self)
        self.view = test.view(self)
    
    def startConnection(self,server,port):
        self.model.startConnection(server,port)
    

    def readConfigfile(self):
        filepath=os.environ["HOME"]+os.sep+".keckz"
        if os.path.exists(filepath) == False:
            dotkeckz=open(filepath, "w")
            dotkeckz.write("# Das ist die KECKz Konfigurationsdatei, für nähere Infos siehe 'man keckz'")
            dotkeckz.flush()
        dotkeckz=open(filepath)
        array=dotkeckz.readlines()
        self.configfile={}
        for i in array:
            if i.isspace() == False or i.startswith("#")==False or i.find("=")==-1:
                a=i.split("=")
                a=a[:2]
                self.configfile.update({a[0].strip():a[1].strip()})


    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.model.sendHandshake(self.view.foobar())
    
    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.View.name,self.View.version,sys.platform,"Python "+pythonversion[0])
        self.model.getRooms()
    
    def receivedRooms(self,rooms):
        # at first there has to be some kind of method transfering the rooms to the view
        array=[]
        for a in ["autologin","nick","passwd","room"]:
            try:
                array.append(self.configfile[a])
            except:
                array.append("")
        if array[0]=="":
            pass
            # now the array is: ["","foo","bar",""] for example
            # here the view has to get the information given (the array) and has to give back an array
        self.model.sendLogin(array[1],array[2],array[3])
            
    
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
        view.displayMsg(deltaPing)
    
    def receivedMsg(self,nick,channel,msg):
        pass
    
    def privMsg(self,nick,msg):
        pass
    
    def botMsg(self,nick,msg):
        pass
    
    def gotException(message):
        pass
    
    def unknownMethod(self):
        print "Shit happens: The Controller wasn't able to respond to a call from the server"

    def __getattr__(self, name):
        return self.unknownMethod    