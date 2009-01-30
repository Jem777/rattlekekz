#!/usr/bin/env python
# -*- coding: utf-8 -*-

copyright = """
    Copyright 2008, 2009 Moritz Doll and Christian Scharkus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Modules
import sys
from time import time
from OpenSSL.SSL import SSLv3_METHOD, Context

# Modules for twisted
from twisted.internet import reactor, protocol, task, ssl
from twisted.protocols import basic

class KekzClient(basic.LineOnlyReceiver, protocol.Factory):
    """
    This is the main part of the Kekz.net protocol
    This class expects the controller instance as parameter.
    The class establishes an SSL/TLS connection to the server, and
    sends occurring events to the controller, by saying controller.someEvent().
    """

    def __init__(self,controller):
        """Takes one argument: the instance of the controller Class."""
        self.controller=controller
        # this should be checked properly, with a numerical version number comparisation, or something like that.
        # check how to check and compare version numbers in python.
        try:
            import cjson
            self.encoder=lambda x: cjson.encode(x)
            self.decoder=lambda y: cjson.decode(y)
        except:
            import json
            if sys.version.startswith("2.5"):
                self.encoder=lambda x: json.JsonWriter().write(x)
                self.decoder=lambda y: json.JsonReader().read(y)
            else:
                self.encoder=lambda x: json.JSONEncoder().encode(x)
                self.decoder=lambda y: json.JSONDecoder().decode(y)
        self.pingAnswer=False
        self.pwhash=None
        self.nickname=""
        self.delimiter='\n'

    def getContext(self):
        ctx = Context(SSLv3_METHOD)
        ctx.set_options(0x00004000L)
        return ctx

    def startConnection(self,server,port):
        """Initiate the connection."""
        reactor.connectSSL(server, port, self, self)
        reactor.run()

    def buildProtocol(self, addr):
        return self

    def startedConnecting(self, connector):
        self.controller.startedConnection()

    def clientConnectionFailed(self, connector, reason):
        self.controller.failConnection(reason)

    def clientConnectionLost(self, connector, reason):
        self.sendingPings.stop()
        self.controller.lostConnection(reason)

    def sendHandshake(self,hash):
        """The Handshake has to be send first, after a ssl connection is established"""
        self.sendLine('000 '+ hash)

    def sendDebugInfo(self,client,ver,rev,os,java):
        """Sends client informations to the server. used for debugging purposes."""
        Infos={"client":client,"ver":ver,"rev":rev,"os":os,"java":java}
        self.sendLine("001 "+self.encoder(Infos))

    def getRooms(self):
        """Request the List of Rooms for Login. You will receive a receivedRooms()"""
        reactor.callLater(1, lambda: self.sendLine('010'))

    def sendLogin(self,nick,passhash,room):
        """Logs on to the Kekz.net server and joins room "room" """
        self.sendLine('020 %s#%s#%s' % (nick,passhash,room))

    def sendMailLogin(self,nick,passhash):
        """Logs on to the Kekz.net mailsystem"""
        self.sendLine('021 %s#%s' % (nick,passhash))

    def registerNick(self,nick,pwhash,email):
        """Register a new Nick"""
        Daten={"nick":nick,"passwd":pwhash,"email":email}
        self.sendLine("030 "+self.encoder(Daten))

    def changePassword(self,passwd,passwdnew):
        """Change passwd to passwdnew - Both have to be a hash; no hashing in the model"""
        Data={"passwd":passwd,"passwdnew":passwdnew}
        self.sendLine("031 "+self.encoder(Data))
        
    def updateProfile(self,name,location,homepage,hobbies,signature,passwd):
        """Update the Profile - passwd has to be hashed"""
        Data={"name":name,"ort":location,"homepage":homepage,"hobbies":hobbies,"freitext":signature,"passwd":passwd}
        self.sendLine("041 "+self.encoder(Data))

    def sendIdentify(self, data):
        self.sendLine("070 "+data)

    def startPing(self):
        """Should be called after the login. Starts the ping loop, with an initial delay of 10 seconds."""
        self.sendingPings=task.LoopingCall(self.sendPing)
        reactor.callLater(10, lambda: self.sendingPings.start(60))

    def sendPing(self):
        """Sends the ping, this needn't to be called by the controller, just startPing"""
        if self.pingAnswer is False:
            self.sendLine("088")
            self.lastPing = time()
            self.pingAnswer = True
        else:
            self.controller.pingTimeout()
            self.sendingPings.stop()

    def sendMsg(self, channel, msg):
        """Send a message to a channel"""
        if msg.isspace(): pass
        else:
            self.sendLine("100 %s %s" % (channel,msg))

    def sendSlashCommand(self,command,channel,msg):
        """Msg starting with a Slash / """
        if msg.isspace(): pass
        elif command=="/exit": pass
        elif command=="/sendm": pass
        elif command=="/msg" or command=="/p":
            msg=msg.split(" ")
            if not len(msg)<2:
                user=msg[0]
                msg=" ".join(msg[1:])
                self.sendPrivMsg(user,msg)
        else: self.sendLine("101 %s %s %s" % (channel,command,msg))

    def sendPrivMsg(self,nick,msg):
        """Private Msgs, they call be send with /p or in another window like a room"""
        self.sendLine('102 %s %s' % (nick,msg))

    def sendJoin(self,room):
        self.sendLine("223 "+room)

    def sendCPMsg(self,user,msg):
        self.sendLine("310 "+user+" "+msg)

    def sendCPAnswer(self,user,msg):
        self.sendLine("311 "+user+" "+msg)

    def sendMail(self,nick,msg,id):
        mail={"id":id,"tonick":nick,"msg":msg}
        self.sendLine("440 "+self.encoder(mail))

    def getMaillist(self):
        self.sendLine("450")

    def getMailCount(self):
        self.sendLine("460")

    def getMail(self,id):
        self.sendLine("461 "+id)

    def deleteMail(self,id):
        self.sendLine("462 "+id)

    def deleteAllMails(self):
        self.sendLine("463")

    def quitConnection(self):
        """ends the connection, usually getRooms is called afterwards"""
        self.sendLine("900")


# Following Methods are called if the server sends something
    def connectionMade(self):
        """It doesn't fit the naming pattern, i know"""
        self.controller.gotConnection()

    def lineReceived(self,data):
        number=data[:3]
        string=data[4:]
        try:
            attribut=getattr(self, "kekzCode"+number)
        except AttributeError:
            attribut=getattr(self, "kekzCodeUnknown")
            string=data
        attribut(string)


    def kekzCode000(self,data):
        self.pwhash=data
        self.controller.receivedHandshake()
        self.startPing()

    def kekzCode010(self,data):
        """Creates an array of rooms received """
        rooms=self.decoder(data)
        self.controller.receivedRooms(rooms)
    
    def kekzCode020(self,data):
        userdata=self.decoder(data)
        nick,status,room=userdata["nick"],userdata["status"],userdata["room"]
        self.nickname=nick
        self.controller.successLogin(nick,status,room)

    def kekzCode021(self,data):
        self.controller.successMailLogin()

    def kekzCode030(self,data):
        self.controller.successRegister()

    def kekzCode031(self,data):
        if data.startswith("!ERROR "):
            self.controller.gotException(data[7:])
        else:
            self.controller.successNewPassword()

    def kekzCode040(self,data):
        dic=self.decoder(data)
        name,ort,homepage,hobbies,signature=dic["name"],dic["ort"],dic["homepage"],dic["hobbies"],dic["freitext"]
        self.controller.receivedProfile(name,ort,homepage,hobbies,signature)

    def kekzCode041(self,data):
        if data.startswith("!ERROR "):
            self.controller.gotException(data[7:])
        else:
            self.controller.successNewProfile()

    def kekzCode070(self,data):
        self.controller.securityCheck(data)

    def kekzCode088(self,data):
        self.controller.receivedPing(int((time()-self.lastPing)*1000))
        self.pingAnswer=False

    def kekzCode100(self,data):
        foo=data.split(" ")
        channel,nick=foo[0],foo[1]
        msg=" ".join(foo[2:])
        if not msg: return
        self.controller.receivedMsg(nick,channel,msg)

    def kekzCode101(self,data):
        foo=data.split(" ")
        channel=foo[0]
        msg=" ".join(foo[1:])
        if not msg: return
        self.controller.receivedRoomMsg(channel,msg)

    def kekzCode102(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.privMsg(nick,msg)

    def kekzCode103(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.ownprivMsg(nick,msg)

    def kekzCode109(self,data):
        foo=data.split(" ")
        nick=foo[0]
        msg=" ".join(foo[1:])
        self.controller.botMsg(nick,msg)
    
    def kekzCode110(self,data):
        rooms=data.split("#")
        for i in range(len(rooms)):
            rooms[i]=rooms[i].split(",")
        self.controller.receivedRoomlist(rooms) # rooms is build like this: [[roomname,user, max user, roomstatus, sysroom],[nextRoom...]]
    
    def kekzCode200(self,data):
        foo=data.split(" ")
        room=foo[0]
        rawuser=" ".join(foo[1:])
        rawuser=self.decoder(rawuser)
        users=[]
        for i in range(len(rawuser)):
            username=rawuser[i]["name"]
            if rawuser[i].has_key("away") and rawuser[i]["away"]=="z":
                away=True
            else:
                away=False
            if rawuser[i].has_key("stat"):
                status=rawuser[i]["stat"]
            else:
                status="x"
            users.append([username,away,status])
        self.controller.receivedUserlist(room,users) # users is build like this: [[username,away,status],[nextUser,..]]
    
    def kekzCode201(self,data):
        foo=data.split(" ")
        room=foo[0]
        rawuser=foo[1].split(",")
        self.controller.joinUser(room,rawuser[0],rawuser[1],rawuser[2])

    def kekzCode202(self,data):
        foo=data.split(" ")
        room=foo[0]
        rawuser=foo[1].split(",")
        self.controller.quitUser(room,rawuser[0],rawuser[1])

    def kekzCode205(self,data):
        foo=data.split(" ")
        room=foo[0]
        rawuser=foo[1].split(",")
        if rawuser[1]=="z": away=True
        else: away=False
        self.controller.changedUserdata(room,rawuser[0],away,rawuser[2])
 
    def kekzCode220(self,data):
        if data.startswith("!"):
            background=True
            data=data[1:]
        else: background=False
        self.controller.meJoin(data,background)

    def kekzCode221(self,data):
        self.controller.mePart(data)

    def kekzCode222(self,data):
        room=data.split(" ")
        self.controller.meGo(room[0],room[1])

    def kekzCode225(self,data):
        foo=data.split(" ")
        topic=" ".join(foo[1:])
        topic=topic
        self.controller.newTopic(foo[0],topic)

    def kekzCode226(self,data):
        self.controller.newTopic(data,"")

    def kekzCode229(self,data):
        self.controller.loggedOut()
    
    def kekzCode300(self,data):
        self.controller.receivedInformation(data)

    def kekzCode301(self,data):
        data=self.decoder(data)
        self.controller.receivedWhois(data)
    
    def kekzCode310(self,data):
        foo=data.split(" ")
        cpmsg=" ".join(foo[1:])
        user=foo[0]
        cpmsg = cpmsg
        self.controller.receivedCPMsg(user,cpmsg)

    def kekzCode311(self,data):
        foo=data.split(" ")
        cpanswer=" ".join(foo[1:])
        user=foo[0]
        cpanswer=cpanswer
        self.controller.receivedCPAnswer(user,cpanswer)

    def kekzCode440(self,data):
        self.controller.sendMailsuccessful(data)

    def kekzCode450(self,data):
        dic=self.decoder(data)
        userid=dic["quota"]
        mailcount=dic["int"]
        mails=dic["list"]
        self.controller.receivedMails(userid,mailcount,mails)

    def kekzCode460(self,data):
        mails=data.split("#")
        unreadmails,allmails=int(mails[0]),int(mails[1])
        self.controller.receivedMailcount(unreadmails,allmails)

    def kekzCode461(self,data):
        mail=self.decoder(data)
        if mail["type"]=="Error":
            self.controller.requestMailfailed(mail["Error"])
        else:
            self.controller.requestMailsuccessful(mail["from"],mail["date"],mail["body"])

    def kekzCode470(self,data):
        mails=data.split("#")
        nick,header=str(mails[0]),str("#".join(mails[1:]))
        self.controller.receivedNewMail(nick,header)

    def kekzCode901(self,data):
        self.controller.gotHandshakeException(data)

    def kekzCode920(self,data):
        self.controller.gotLoginException(data)

    def kekzCode921(self,data):
        self.controller.gotException(data)

    def kekzCode930(self,data):
        self.controller.gotException(data)

    def kekzCode940(self,data):
        self.controller.gotException(data)

    def kekzCode941(self,data):
        dic=self.decoder(data)
        id,msg=dic["id"],dic["msg"]
        self.controller.sendMailfailed(id,msg)

    def kekzCode988(self,data):
        self.controller.gotException(data)

    def kekzCodeUnknown(self,data):
        self.controller.gotException(data)
