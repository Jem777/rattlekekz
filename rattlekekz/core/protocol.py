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
import sys, os
import time
from OpenSSL.SSL import SSLv3_METHOD, Context
from rattlekekz.core import pluginmanager

import erlastic, bert

# Modules for twisted
from twisted.internet import reactor, protocol, task, ssl
from twisted.protocols import basic

class KekzChatClient(basic.Int16StringReceiver, protocol.Factory, pluginmanager.iterator): # TODO: Maybe don't use interhitance for pluginmanagement
    """
    This is the main part of the Kekz.net protocol
    This class expects the controller instance as parameter.
    The class establishes an SSL/TLS connection to the server, and
    sends occurring events to the controller, by saying controller.someEvent().
    """

    def __init__(self,controller):
        """Takes one argument: the instance of the controller Class."""
        pluginmanager.iterator.__init__(self)
        self.controller=controller
        self.pingAnswer=True
        self.pwhash=None
        self.nickname=""
        self.connector=None
        self.reconnecting=False
        self.isConnected=False
        self.tries = 0

    def getPlugin(self):
        pass

    def getContext(self):
        ctx = Context(SSLv3_METHOD)
        ctx.set_options(0x00004000L)
        return ctx

    def startConnection(self,server,port):
        """Initiate the connection."""
        self.connector = reactor.connectSSL(server, port, self, self)
        reactor.run()

    def startReconnect(self):
        self.reconnecting=True
        if not self.tries:
            self.connector.connect()
        elif self.tries <= 10:
            reactor.callLater(10,self.connector.reconnect())
        self.tries+=1

    def buildProtocol(self, addr):
        return self

    def sendTuple(self,data): # TODO: review this in context of plugins.
        """sends a line to the server if connected"""
        if self.isConnected:
            data=bert.encode((bert.Atom(data[0]),)+data[1:])
            try:
                self.sendString(data)
            except basic.StringTooLongError:
                self.controller.gotException("you're trying to send to much data at once")
        else:
            self.controller.gotException("not connected")

    def startedConnecting(self, connector):
        """starts the connection"""
        self.isConnected=True
        self.iterPlugins('startedConnection')

    def clientConnectionFailed(self, connector, reason):
        """called if the client couldn't connect to the server"""
        print ":".join(map(str,time.localtime(time.time())[3:6])),"connection failed"
        try:
            self.sendingPings.stop()
        except:
            #pass
            raise
        self.isConnected=False
        self.startReconnect()
        self.iterPlugins('failConnection',[reason])

    def clientConnectionLost(self, connector, reason):
        """called if the Connection was lost"""
        print ":".join(map(str,time.localtime(time.time())[3:6])),"connection lost"
        try:
            self.sendingPings.stop()
        except:
            #pass
            raise
        self.isConnected=False
        self.startReconnect()
        self.iterPlugins('lostConnection',[reason])

    def sendHandshake(self,hash):
        """The Handshake has to be send first, after a ssl connection is established"""
        data=("handshake",hash)
        self.sendTuple(data)

    def sendIdentify(self,client,ver,os,python):
        """Sends client informations to the server. used for debugging purposes."""
        if type(ver) != (int or float):
            try:
                ver = float(ver)
            except:
                print "version has to be float or int!"
                raise
            else:
                if ver.is_integer:
                    ver = int(ver)
        data=("identify",client,ver,os,python)
        self.sendTuple(data)

    def getRooms(self):
        """Request the List of Rooms for Login. You will receive a receivedRooms()"""
        self.sendTuple(("get_roomlist",))

    def sendLogin(self,nick,passhash,room):
        """Logs on to the Kekz.net server and joins room "room" """
        data=("login",nick,passhash,room)
        self.sendTuple(data)

    def registerNick(self,nick,pwhash,email):
        """Register a new Nick"""
        data=("register",nick,email,pwhash)
        self.sendTuple(data)

    def changePassword(self,passwd,passwdnew):
        """Change passwd to passwdnew - Both have to be a hash; no hashing in the model"""
        Data=("change_password",passwd,passwdnew)
        self.sendTuple(data)

    def updateProfile(self,name,location,homepage,hobbies,signature,passwd):
        """Update the Profile - passwd has to be hashed"""
        data=("update_profile",name,passwd,location,homepage,hobbies,signature)
        self.sendTuple(data)

    def startPing(self):
        """Should be called after the login. Starts the ping loop, with an initial delay of 10 seconds."""
        self.pingAnswer = True
        self.sendingPings=task.LoopingCall(self.sendPing)
        reactor.callLater(10, lambda: self.sendingPings.start(60))

    def sendPing(self):
        """Sends the ping, this needn't to be called by the controller, just startPing"""
        if self.pingAnswer:
            try:
                self.sendTuple(("ping",))
            except:
                type,value,traceback = sys.exc_info()
                sys.excepthook(type,value,traceback)
            print ":".join(map(str,time.localtime(time.time())[3:6])),"sending ping"
            self.lastPing = time.time()
            self.pingAnswer = False
        else:
            print ":".join(map(str,time.localtime(time.time())[3:6])),"shit timeouted"
            self.iterPlugins('pingTimeout')
            self.sendingPings.stop()

    def sendPublic(self, channel, msg):
        """Send a message to a channel"""
        if msg.isspace(): pass
        else:
            data=("public",channel,msg)
            self.sendTuple(data)

    def sendCommand(self,command,channel,msg):
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
        else:
            data = ("command",channel,command+" "+msg)
            self.sendTuple(data)

    def sendPrivate(self,nick,msg):
        """Private Msgs, they call be send with /p or in another window like a room"""
        data = ("private",nick,msg)
        self.sendTuple(data)

    def sendJoin(self,room):
        data = ("join",room)
        self.sendTuple(data)

    def sendWhoisClose(self,user):
        data = ("whois_close",user)
        self.sendTuple(data)

    def sendCtcpRequest(self,user,msg):
        print "request send to",user,"with",msg
        data = ("ctcp_request",user,msg)
        self.sendTuple(data)

    def sendCtcpReply(self,user,msg):
        print "reply send to",user,"with",msg
        data = ("ctcp_reply",user,msg)
        self.sendTuple(data)

    def sendMail(self,nick,msg,id):
        data = ("send_mail",id, nick, msg)
        self.sendTuple(data)

    def getMailStubs(self):
        data = ("get_mail_stubs",)
        self.sendTuple(data)

    def getMailCount(self):
        data = ("get_mail_count",)
        self.sendTuple(data)

    def getMail(self,id):
        data = ("get_mail",int(id))
        self.sendTuple(data)

    def deleteMail(self,id):
        data = ("delete_mail",id)
        self.sendTuple(data)

    def deleteAllMails(self):
        data = ("delete_all_mails",)
        self.sendTuple(data)

    def quitConnection(self):
        """ends the connection, usually getRooms is called afterwards"""
        data = ("logout",)
        self.sendTuple(data)

# Following Methods are called if the server sends something
    def connectionMade(self):
        """It doesn't fit the naming pattern, i know"""
        self.tries = 0
        self.iterPlugins('gotConnection')

    def stringReceived(self,data):
        data = bert.decode(data)
        command = str(data[0])
        params = data[1:]
        try:
            attribut=getattr(self, command)
        except AttributeError:
            attribut=getattr(self, "unknown")
            params=data
        attribut(params)

    def handshake_ok(self,data):
        print ":".join(map(str,time.localtime(time.time())[3:6])),"got handshake"
        self.pwhash=data[0]
        self.iterPlugins('receivedHandshake')
        self.startPing()

    def roomlist(self,data):
        """Creates an array of rooms received"""
        rooms=[]
        for i in data[0]:
            rooms.append({"name":i[0],"users":i[1],"max":i[2]})
        self.iterPlugins('receivedRooms',[rooms])

    def login_ok(self,data):
        nick,room,status=data
        self.nickname=nick
        self.iterPlugins('successLogin',[nick,status,room])

    def register_ok(self,data):
        self.iterPlugins('successRegister')

    def change_password_ok(self,data):
        self.iterPlugins('successNewPassword')

    def change_password_error(self,data):
        self.iterPlugins('gotException',[data[0]])

    def profile(self,data):
        name,ort,homepage,hobbies,signature=data
        self.iterPlugins('receivedProfile',[name,ort,homepage,hobbies,signature])

    def change_profile_ok(self,data):
        self.iterPlugins('successNewProfile')

    def change_profile_error(self,data):
        self.iterPlugins('gotException',[data[0]])

    def ping(self,data):
        print ":".join(map(str,time.localtime(time.time())[3:6])),"got ping answer"
        self.iterPlugins('receivedPing',[int((time.time()-self.lastPing)*1000)])
        self.pingAnswer=True

    def public(self,data):
        channel,nick,msg=data
        self.iterPlugins('receivedMsg',[nick,channel,msg])

    def rawmessage(self,data):
        channel,msg=data
        self.iterPlugins('receivedRoomMsg',[channel,msg])

    def private(self,data):
        nick,msg=data
        self.iterPlugins('privMsg',[nick,msg])

    def private_ok(self,data):
        nick,msg=data
        self.iterPlugins('ownprivMsg',[nick,msg])

    def offline_notication(self,data):
        print "104"
        nick = data[0]
        self.iterPlugins('privOffline',[nick])

    def botmessage(self,data):
        nick,msg=data
        self.iterPlugins('botMsg',[nick,msg])

    def userlist(self,data):
        room,rawuser=data
        users = []
        for i in rawuser:
            username,status,away=i
            users.append([username,away,str(status)])
        self.iterPlugins('receivedUserlist',[room,users]) # users is build like this: [[username,away,status],[nextUser,..]]

    def add_userlist(self,data):
        room,nick,status,message=data
        self.iterPlugins('joinUser',[room,nick,str(status),str(message)])

    def remove_userlist(self,data):
        room,nick,message=data
        self.iterPlugins('quitUser',[room,nick,str(message)])

    def update_userlist(self,data):
        room,nick,away,status=data
        self.iterPlugins('changedUserdata',[room,nick,away,status])

    def join_ok(self,data):
        self.iterPlugins('meJoin',[data[0],False])

    def join_bg_ok(self,data):
        self.iterPlugins('meJoin',[data[0],True])

    def part_ok(self,data):
        self.iterPlugins('mePart',[data[0]])

    def go_ok(self,data):
        self.iterPlugins('meGo',[data[0],data[1]])

    def new_topic(self,data):
        room,topic=data
        self.iterPlugins('newTopic',[room,topic])

    def delete_topic(self,data):
        room = data[0]
        self.iterPlugins('newTopic',[room,""])

    def user_quit(self,data):
        self.iterPlugins('loggedOut')

    def whois(self,data):
        whois=[]
        for i in data[0]:
            whois.append(str(i[0]))
            whois.append(i[1])
        self.iterPlugins('receivedWhois',[whois])
    
    def send_ctcp_reply(self,data):
        user,cpanswer = data
        self.iterPlugins('receivedCtcpReply',[user,cpanswer])

    def send_ctcp_request(self,data):
        user,cpmsg=data
        self.iterPlugins('receivedCtcpRequest',[user,cpmsg])

    def popup_url(self,data):
        self.iterPlugins('openURL',[data[0]])

    def send_mail_ok(self,data):
        id = data[0]
        self.iterPlugins('sendMailsuccessful',[id])

    def send_mail_error(self,data):
        id,reason=data
        self.iterPlugins('sendMailfailed',[id,reason])

    def mail_stubs(self,data):
        count,mails=data
        mail_list=[]
        if mails:
            for i in mails:
                mail_list.append({"mid":i[0],"from":i[1],"stub":i[2],"date":i[3],"unread":i[4]})
        self.iterPlugins('receivedMails',[0,count,mail_list])

    def mail_count(self,data):
        unreadmails,allmails=int(data[0]),int(data[1])
        self.iterPlugins('receivedMailcount',[unreadmails,allmails])

    def get_mail_ok(self,data):
        sender,date,mail=data
        self.iterPlugins('requestMailsuccessful',[sender,date,mail])

    def get_mail_error(self,data):
        reason = data[0]
        self.iterPlugins('requestMailfailed',[reason])

    def kekzCode470(self,data):
        nick,header=data
        self.iterPlugins('receivedNewMail',[nick,header])

    def handshake_error(self,data):
        self.iterPlugins('gotHandshakeException',["client to old"])

    def login_error(self,data):
        reason = str(data[0])
        self.iterPlugins('gotLoginException',[reason])

    def register_error(self,data):
        reason = str(data[0])
        self.iterPlugins('gotException',[reason])

    def protocol_error(self,data):
        self.iterPlugins('gotException',["998, faggot!"])

    def unknown(self,data):
        self.iterPlugins('gotException',[data])