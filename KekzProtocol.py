#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Die Module für die Datenverarbeitung:
import json, re, time
from hashlib import sha1

# Die Module für twisted
from twisted.internet import reactor, protocol
from twisted.protocols import basic


class KekzClient(basic.LineOnlyReceiver):
    Nickname=""
    Password=None
    pingAnswer=False
    #decoder=json.JSONDecoder()
    #encoder=json.JSONEncoder()

    clientident="Ze$8hAbeVe0y" #das muss später alles weg
    verInt="0"
    netVer="netkekZ4 beta 20080910"
    
    def receivedHandshake(self,passworthash):
        """Wird abgerufen, wenn der Server den Handshake beantwortet"""

    def receivedRooms(self,rooms):
        """Wird aufgerufen, wenn beim Login die Rooms empfangen werden
        rooms ist ein dictionary"""
    
    def receivedPing(self, ping):
        """Wird gerufen wenn Ping ermittelt wurde. Selbiger wird als Parameter übergeben"""
    
    def loginDone(self, user):
        """Wird aufgerufen, wenn man sich erfolgreich eingeloggt hat
        user ist ein dictionary"""
    
    def successRegistered(self):
        pass
    
    def successChangedPassword(self):
        pass
    
    def receivedProfile(name,location,homepage,hobbies):
        pass
    
    def successNewProfileSet(self):
        pass
    
    def receivedMsg(self,nick,channel,msg):
        """Diese Methode wird aufgerufen, wenn eine Nachricht emfangen wird"""

    def privMsg(self,nick,msg):
        """privMsg ist die positive Rückmeldung vom Server, dass die Nachricht übermittelt wurde.
        Der Client sollte erst in diesem Moment die Nachricht im PrivateLog darstellen. von KekzNet"""

    def botMsg(self,botname,msg):
        """Die Bot-Nachricht wird verwendet, um Nachrichten vom Systembot (~SilentBot) an den User zu
        übermitteln. Dies kann eine Fehlermeldung oder Informationen sein. Eine solche Nachricht muss
        im aktuell angewählten Fenster sichtbar gemacht werden. von KekzNet"""

    def connectionMade(self):
        """diese Methode wird aufgerufen, wenn die SSL Verbindung aufgebaut wurde"""
        reactor.callLater(10.0, self.startPing)
        self.sendHandshake(self.clientident,self.verInt,self.netVer)

    def connectionLost(self,data):
        pass


    def sendHandshake(self,clientident,verInt,netVer):
        handShakeVersion = sha1(clientident+'#'+verInt+'#'+netVer).hexdigest()
        self.sendLine('000 '+handShakeVersion)

    def sendDebugInfo(self,client,ver,os,java):
        """Sendet die Infos für Debugzwecke auslesbar von Administratoren"""
        Infos={"client":client,"ver":ver,"os":os,"java":java}
        self.sendLine("001 "+json.JSONEncoder().decode(Infos))

    def getRooms(self):
        """Anfordern der Raumliste"""
        self.sendLine('010')

    def sendLogin(self,nick,passhash,room):
        self.sendLine('020 %s#%s#%s' % (nick,passhash,room))

    def registerNick(self,nick,pwhash,email):
        """Registrieren"""
        Daten={"nick":nick,"passwd":pwhash,"email":email}
        self.sendLine("030 "+json.JSONEncoder().decode(Daten))

    def changePasswort(self,passwd,passwdneu):
        """Ändere Passwort in passwdneu - Beide sind schon ein Hash"""
        Daten={"passwd":passwd,"passwdnew":passwdneu}
        self.sendLine("031 "+json.JSONEncoder().decode(Daten))

    def updateProfile(self,name,ort,homepage,hobbies,passwd):
        """Das Profil updaten - passwd ist schon ein Hash"""
        Daten={"name":name,"ort":ort,"homepage":homepage,"hobbies":hobbies,"passwd":passwd}
        self.sendLine("040 "+json.JSONEncoder().decode(Daten))

    def sendPing(self):
        if self.pingAnswer is False:
            self.sendLine("088")
            self.lastPing = time.time()
            self.Ping = True
        else:
            self.pingTimeout()

    def sendMsg(self, channel, msg):
        if msg.isspace(): pass
        else: self.sendLine("100 %s %s" % (channel,msg))

    def sendSlashCommand(self,command,channel,msg):
        if msg.isspace(): pass
        if command=="/exit": pass #self.exit()
        elif command=="/sendm": pass
        elif command=="/msg" or "/p": pass 
        else: self.sendLine("101 %s %s %s" % (channel,command,msg))

    def sendPrivMsg(self,nick,msg):
        self.sendLine('102 %s%s' % (nick,msg))


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

    def kekzCode030(self,data):
        self.erfolgRegistrierung()

    def kekzCode031(self,data):
        self.erfolgNeuesPasswort()

    def kekzCode040(self,data):
        dic=json.JSONDecoder().decode(data)
        name,ort,homepage,hobbies=dic.values()
        self.receivedProfil(name,ort,homepage,hobbies)

    def kekzCode041(self,data):
        self.erfolgNeuesProfil()

    def kekzCode088(self,data):
        self.receivedPing(self.lastPing-time.time())
        self.pingAnswer=false

    def kekzCode100(self,data):
        foo=data.split(" ")
        channel,nick=foo[0],foo[1]
        msg=" ".join(foo[2:])

        if not msg: return

        self.receivedMsg(nick,channel,msg)

    def kekzCode102(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.receivedMsg(nick,self.Nickname,msg)

    def kekzCode103(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.privMsg(nick,msg)

    def kekzCode109(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.botMsg(nick,msg)
    
    def kekzCode110(self,data):
        pass

    def kekzCode901(self,data):
        print data

    def kekzCode920(self,data):
        print data

    def kekzCode988(self, data):
        print data

    def kekzCodeUnknown(self, data):
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

    def pingTimeout(self):
        self.connectionLost("Ping Timeout")