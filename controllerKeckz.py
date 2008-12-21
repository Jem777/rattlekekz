#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, os, sys

# Line for tester / test:
# 020 tester#68358d5d9cbbf39fe571ba41f26524b6#dev

class Kekzcontroller():
    def __init__(self, interface):
        self.model = kekzprotocol.KekzClient(self)
        self.view = interface(self)
        self.readConfigfile()

    def startConnection(self,server,port):
        self.model.startConnection(server,port)

    def readConfigfile(self):
        #filepath=os.environ["HOME"]+os.sep+".kekznet.conf"
        filepath=os.environ["HOME"]+os.sep+"debug.conf"
        if os.path.exists(filepath) == False:
            dotkeckz=open(filepath, "w")
            dotkeckz.write("# Dies ist die kekznet Konfigurationsdatei. Für nähere Infos siehe Wiki unter kekz.net")
            dotkeckz.flush()
        dotkeckz=open(filepath)
        array=dotkeckz.readlines()
        self.configfile={}
        for i in array:
            if not (i.isspace() or i.startswith("#")) or (i.find("=")!=-1):
                a=i.split("=")
                a=a[:2]
                self.configfile.update({a[0].strip():a[1].strip()})
        if self.configfile.has_key("ok") and self.configfile["ok"]=="1":
            pass
        else:
            self.configfile={}


    """following methods transport data from the View to the model"""
    def sendLogin(self, nick, pwhash, rooms):
        self.model.sendLogin(nick.encode("utf_8"), pwhash.encode("utf_8"), rooms.encode("utf_8"))

    def sendMsg(self, channel, msg):
        self.model.sendMsg(channel.encode("utf_8"),msg.encode("utf_8"))


    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.model.sendHandshake(self.view.fubar())

    def startedConnection(self):
        """indicates that the model is connecting. Here should be a call to the view later on"""
        pass

    def lostConnection(self, reason):
        """the connection was clean closed down. Here should be a call to the view later on"""
        pass

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        pass

    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.view.name, self.view.version, sys.platform, "Python "+pythonversion[0])
        self.model.getRooms()

    def receivedRooms(self,rooms):
        array=[]
        for a in ["autologin","nick","passwd","room"]:
            try:
                array.append(self.configfile[a])
            except:
                array.append("")
        if array[0]=="True" or array[0]=="1":
            self.model.sendLogin(array[1],array[2],array[3])
        else:
            self.view.receivedPreLoginData(rooms,array[1:])
            # now the array is: [nick,passwd,room]
            # the view has to give back an array or has to send model.sendLogin by itself


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

    def pingTimeout(self):
        self.lostConnection("PingTimeout")

    def receivedMsg(self,nick,channel,msg):
        self.view.printMsg(nick.decode("utf_8"),msg.decode("utf_8"),channel.decode("utf_8"),0)

    def receivedRoomMsg(self,channel,msg):
        self.view.printMsg("",msg.decode("utf_8"),channel.decode("utf_8"),1)

    def privMsg(self,nick,msg):
        self.view.printMsg(nick.decode("utf_8"),msg.decode("utf_8"),"",2)

    def ownprivMsg(self,nick,msg):
        self.view.printMsg(nick.decode("utf_8"),msg.decode("utf_8"),channel.decode("utf_8"),3)
        
    def botMsg(self,nick,msg):
        self.view.printMsg(nick.decode("utf_8"),msg.decode("utf_8"),"",4)

    def gotException(self, message):
        pass

    def receivedUserlist(self,room,users):
        self.view.listUser(room,users)

    def joinUser(self,room,nick,state,joinmsg):
        pass

    def quitUser(self,room,nick,partmsg):
        pass

    def changedUserdata(self,room,nick,away,state):
        pass

    def meJoin(self,room,background):
        pass

    def mePart(self,room):
        pass

    def meGo(self,oldroom,newroom):
        pass

    def newTopic(self,room,topic):
        pass

    def loggedOut(self):
        pass

    def receivedInformation(self,info):
        pass

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)