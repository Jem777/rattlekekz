#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules
import json, time
#from hashlib import sha1

# Modules for twisted
from twisted.internet import reactor, protocol, task, ssl
from twisted.protocols import basic


class KekzClient(basic.LineOnlyReceiver):
    """This is the main part of the Kekz.net protocol
    
    blablablubb
    
    TODO: alle Kommentare entfernen, die alten code beinhalten; mehr Methoden"""

    def __init__(self,controller):
        """Called, when an object of the KekzClient class is created"""
        self.controller=controller
        self.pingAnswer=False
        self.pwhash=None
        self.nickname=""

    def startConnection(self,server,port):
        """starts the ssl connection"""
        f = KekzFactory(self)
        # connect factory to this host and port
        # reactor.listenSSL(23002, f, ssl.ClientContextFactory(), backlog=50)
        # reactor.connectSSL("kekz.net", 23002, f, ssl.ClientContextFactory())
        reactor.connectSSL(server, port, f, ssl.ClientContextFactory())
        reactor.run()  

    def sendHandshake(self,hash):
        """The Handshake has to be send first, after a ssl connection is established"""
        self.sendLine('000 '+ hash)

    def sendDebugInfo(self,client,ver,os,java):
        """Sends the information for the Debugger"""
        Infos={"client":client,"ver":ver,"os":os,"java":java}
        self.sendLine("001 "+json.JSONEncoder().encode(Infos))

    def getRooms(self):
        """Request the List of Rooms for Login"""
        self.sendLine('010')

    def sendLogin(self,nick,passhash,room):
        """Logs on to the Kekz.net server and joins room "room" """
        self.sendLine('020 %s#%s#%s' % (nick,passhash,room))

    def registerNick(self,nick,pwhash,email):
        """Register a new Nick"""
        Daten={"nick":nick,"passwd":pwhash,"email":email}
        self.sendLine("030 "+json.JSONEncoder().encode(Daten))

    def changePassword(self,passwd,passwdnew):
        """Change passwd to passwdnew - Both have to be a hash"""
        Daten={"passwd":passwd,"passwdnew":passwdnew}
        self.sendLine("031 "+json.JSONEncoder().encode(Daten))

    def updateProfile(self,name,ort,homepage,hobbies,passwd):
        """Update the Profile - passwd has to be hashed"""
        Daten={"name":name,"ort":ort,"homepage":homepage,"hobbies":hobbies,"passwd":passwd}
        self.sendLine("040 "+json.JSONEncoder().encode(Daten))

    def startPing(self):
        """Starts to Ping"""
        reactor.callLater(10,task.LoopingCall(self.sendPing,self).start(60))
        
        #task.LoopingCall(self.sendPing,self).start(60)

    def sendPing(self):
        """Sends the ping, this needn't to be called by the controller, just startPing"""
        if self.pingAnswer is False:
            self.sendLine("088")
            self.lastPing = time.time()
            self.pingAnswer = True
        else:
            self.controller.pingTimeout()

    def sendMsg(self, channel, msg):
        """Send a message to a channel"""
        if msg.isspace(): pass
        else:
            if msg.startswith("/"):
                list=msg.split(" ")
                self.sendSlashCommand(list[0],channel," ".join(list[1:]))
            self.sendLine("100 %s %s" % (channel,msg))

    def sendSlashCommand(self,command,channel,msg):
        """Msg starting with a Slash / """
        if msg.isspace(): pass
        if command=="/exit": pass #self.exit()
        elif command=="/sendm": pass
        elif command=="/msg" or "/p": self.sendPrivMsg(channel,msg)
        else: self.sendLine("101 %s %s %s" % (channel,command,msg))

    def sendPrivMsg(self,nick,msg):
        """Private Msgs, they call be send with /m or in another window like a room"""
        self.sendLine('102 %s %s' % (nick,msg))

    def quitConnection(self):
        """ends the connection, usually getRooms is called afterwards"""
        self.sendLine("900")


# Following Methods are called if the server sends something
    def connectionMade(self):
        """It doesn't fit the naming pattern, i know"""
        self.controller.gotConnection()

    def lineReceived(self,data):
        nummer=data[:3]
        string=data[4:]
        try:
            attribut=getattr(self, "kekzCode"+nummer)
        except AttributeError:
            attribut=getattr(self, "kekzCodeUnknown")
            string=data
        attribut(string)


    def kekzCode000(self,data):
        self.pwhash=data
        self.controller.receivedHandshake()
        self.startPing()

    def kekzCode010(self,data):
        """Creats an array of rooms received """
        rooms=json.JSONDecoder().decode(data) #decoder.decode(data)
        self.controller.receivedRooms(rooms)
    
    def kekzCode020(self,data):
        userdata=json.JSONDecoder().decode(data)
        nick,status,room=userdata["nick"],userdata["status"],userdata["room"]
        self.nickname=nick
        self.controller.successLogin(nick,status,room)

    def kekzCode030(self,data):
        self.controller.successRegister()

    def kekzCode031(self,data):
        self.controller.successNewPassword()

    def kekzCode040(self,data):
        dic=json.JSONDecoder().decode(data)
        name,ort,homepage,hobbies=dic["name"],dic["ort"],dic["homepage"],dic["hobbies"]
        self.controller.receivedProfile(name,ort,homepage,hobbies)

    def kekzCode041(self,data):
        self.controller.successNewProfile()

    def kekzCode088(self,data):
        self.controller.receivedPing(self.lastPing-time.time())
        self.pingAnswer=False

    def kekzCode100(self,data):
        foo=data.split(" ")
        channel,nick=foo[0],foo[1]
        msg=" ".join(foo[2:])
        if not msg: return
        self.controller.receivedMsg(nick,channel,msg)

    def kekzCode102(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.receivedMsg(nick,self.Nickname,msg)

    def kekzCode103(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.privMsg(nick,msg)

    def kekzCode109(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.botMsg(nick,msg)
    
    def kekzCode110(self,data):
        pass

    def kekzCode901(self,data):
        self.controller.Error(data)

    def kekzCode920(self,data):
        self.controller.Error(data)

    def kekzCode921(self,data):
        self.controller.Error(data)

    def kekzCode930(self,data):
        self.controller.Error(data)

    def kekzCode940(self,data):
        self.controller.Error(data)

    def kekzCode941(self,data):
        dic=json.JSONDecoder().decode(data)
        id,msg=dic["id"],dic["msg"]
        self.controller.Error(id+" "+msg)

    def kekzCode988(self,data):
        self.controller.Error(data)

    def kekzCodeUnknown(self,data):
        self.controller.Error(data)



class KekzFactory(protocol.ClientFactory):
    """A factory for KECKz. It produces various kinds of Kekzes
    """
    # the class of the protocol to build when new connection is made
    protocol = KekzClient
    def __init__(self,Object):
        self.Object=Object
    def clientConnectionLost(self, connector, reason):
        self.Object.controller.Error("Verbindung verloren: "+reason)
    def clientConnectionFailed(self, connector, reason):
        self.Object.controller.Error("Verbindung kann nicht hergestellt werden: "+reason)
        reactor.stop()