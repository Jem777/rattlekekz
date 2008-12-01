#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Die Module für die Datenverarbeitung:
import json, re
from hashlib import sha1

# Die Module für twisted
from twisted.internet import reactor, protocol, task
from twisted.protocols import basic


class KekzClient(basic.LineOnlyReceiver):
    Nickname=""
    Password=None
    #decoder=json.JSONDecoder()
    #encoder=json.JSONEncoder()

    clientident="Ze$8hAbeVe0y" #das muss später alles weg
    verInt="0"
    netVer="netkekZ4 beta 20080910"
    
    def receivedMsg(self,nick,channel,msg):
        """Diese Methode wird aufgerufen, wenn eine Nachricht emfangen wird"""

    def receivedHandshake(self,passworthash):
        """Wird abgerufen, wenn der Server den Handshake beantwortet"""

    def receivedRooms(self,rooms):
        """Wird aufgerufen, wenn beim Login die Rooms empfangen werden
        rooms ist ein dictionary"""
    
    def loginDone(self, user):
        """Wird aufgerufen, wenn man sich erfolgreich eingeloggt hat
        user ist ein dictionary"""

    def connectionMade(self):
        #print "Hier fängt alles an"
        self.sendHandshake(self.clientident,self.verInt,self.netVer)

    def connectionLost(self,data):
        pass
    
    def sendMsg(self, channel, msg):
        if msg.isspace(): pass
        else: sendLine("100 %s %s" % (channel,msg))

    def sendSlashCommand(self,command,channel,msg):
        if msg.isspace(): pass
        if command=="/exit": pass #self.exit()
        elif command=="/sendm": pass
        elif command=="/msg" or "/p": pass 
        else: sendLine("101 %s %s %s" % (channel,command,msg))

    def sendHandshake(self,clientident,verInt,netVer):
        handShakeVersion = sha1(clientident+'#'+verInt+'#'+netVer).hexdigest()
        self.sendLine('000 '+handShakeVersion)

    def getRooms(self):
        """Anfordern der Raumliste"""
        self.sendLine('010')

    def sendLogin(self,nick,passhash,room):
        self.sendLine('020 %s#%s#%s' % (nick,passhash,room))
    


    def kekzCode000(self,data):
        self.pwhash=data
        self.receivedHandshake()

    def kekzCode010(self,data):
        """Erzeugt List aus Dictionaries der Räume"""
        rooms=json.JSONDecoder().decode(data) #decoder.decode(data)
        self.receivedRooms(rooms)
    
    def kekzCode020(self,data):
        userdata=json.JSONDecoder().decode(data)
        self.loginDone(userdata)

    def kekzCode088(self,data):
        pass

    def kekzCode100(self,data):
        foo=data.split(" ")
        channel,nick=foo[0],foo[1]
        msg=" ".join(foo[1:])

        if not msg: return

        self.msgReceived(nick,channel,msg)

    def kekzCode901(self,data):
        print data

    def kekzCode920(self,data):
        print data

    def kekzCode988(self, data):
        print data

    def kekzCodeUnbekannt(self, data):
        print "Fehler: unbekannter kekzCode: "

        
    def lineReceived(self,data):
        nummer=data[:3]
        string=data[4:]
        try:
            attribut=getattr(self, "kekzCode"+nummer)
        except AttributeError:
            attribut=getattr(self, "kekzCodeUnbekannt")
        else: 
            attribut(string)
