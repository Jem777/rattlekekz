#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, cli, test
import os, sys

# Line for tester / test:
# 020 tester#68358d5d9cbbf39fe571ba41f26524b6#dev

class Kekzcontroller():
    def __init__(self):
        self.model = kekzprotocol.KekzClient(self)
        self.view = cli.View(self)
        #self.view = test.view(self)

    def startConnection(self,server,port):
        self.model.startConnection(server,port)

    def readConfigfile(self):
        filepath=os.environ["HOME"]+os.sep+".kekznet.conf"
        if os.path.exists(filepath) == False:
            dotkeckz=open(filepath, "w")
            dotkeckz.write("# Dies ist die kekznet Konfigurationsdatei. Für nähere Infos siehe Wiki unter kekz.net")
            dotkeckz.flush()
        dotkeckz=open(filepath)
        array=dotkeckz.readlines()
        self.configfile={}
        for i in array:
            if i.isspace() == False or i.startswith("#")==False or i.find("=")==-1:
                a=i.split("=")
                a=a[:2]
                self.configfile.update({a[0].strip():a[1].strip()})
        if self.configfile.has_key("ok") and self.configfile["ok"]=="1":
            pass
        else:
            self.configfile={}


    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        print 'connection ready'
        self.model.sendHandshake(self.view.fubar())

    def startedConnection(self):
        """indicates that the model is connecting. Here should be a call to the view later on"""
        print 'connecting ...'

    def lostConnection(self, reason):
        """the connection was clean closed down. Here should be a call to the view later on"""
        print 'Verbindung beendet:'+str(reason)

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        print 'Verbindungsversuch fehlgeschlagen:'+str(reason)

    def receivedHandshake(self):
        print 'Handshake succeed'
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.view.name, self.view.version, sys.platform, "Python "+pythonversion[0])
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
        #self.model.sendLogin(array[1],array[2],array[3])
        self.model.sendLogin()


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
        view.displayMsg(str(deltaPing))

    def receivedMsg(self,nick,channel,msg):
        print nick+'@'+channel+':'+msg

    def privMsg(self,nick,msg):
        print nick+'(privat):'+msg

    def botMsg(self,nick,msg):
        print nick+':'+msg

    def gotException(self, message):
        print message

    def unknownMethod(self):
        print "Shit happens: The Controller wasn't able to respond to a call from the server"

    def __getattr__(self, name):
        return self.unknownMethod