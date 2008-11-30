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

    clientident="Python" #das muss später alles weg
    verInt="1"
    netVer="netkekZ4 beta 20080910"
    
    def msgReceived(self,nick,channel,msg):
        """Diese Methode wird aufgerufen, wenn eine Nachricht emfangen wird"""

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

    def loginSend(self,nick,passhash,room):
        self.sendLine('020 %s#%s#%s' % (nick,passhash,room))
    


    def kekzCode000(self,data):
        self.pwhash=data
        print "foo"
        self.getRooms()

    def kekzCode010(self,data):
        """Erzeugt List aus Dictionaries der Räume"""
        json.JSONDecoder().decode() #decoder.decode(data)
        self.sendLogin(self.Nickname, self.Passwort, self.Channel)
    
    def kekzCode020(self,data):
        json.JSONDecoder().decode()

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

    def kekzCodeUnbekannt(self, data):
        print "Fehler: unbekannter kekzCode: "

        
    def LineReceived(self,data):
        nummer=data[:3]
        string=data[4:]
        try:
            attribut=getattr(self, "kekzCode"+nummer)
        except AttributeError:
            attribut=getattr(self, "kekzCodeUnbekannt")
        else: 
            attribut(string)