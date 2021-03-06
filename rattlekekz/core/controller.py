#!/usr/bin/env python
# -*- coding: utf-8 -*-

copyright = """
    Copyright 2008, 2009 Moritz Doll and Christian Scharkus

    This file is part of rattlekekz.

    rattlekekz is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    rattlekekz is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with rattlekekz.  If not, see <http://www.gnu.org/licenses/>.
"""

from rattlekekz.core import protocol, pluginmanager
import os, sys, re, time, base64, random, webbrowser, urllib
from hashlib import sha1, md5
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread


class ConfigFile:
    def __init__(self, dict = {}, path = ""):
        self.config = dict
        self.path = path

    def getValue(self, key):
        if self.config.has_key(key):
            return self.config[key]

    def setValue(self, key, value):
        self.config[key] = value

    def createEmptyConf(self, text):
        path = os.path.dirname(self.path)
        if not os.path.exists(path):
            os.mkdir(path)
        try:
            config = open(self.path, "w")
            config.write(text)
            config.flush()
        except IOError, Arg:
            print "Error when writing configfile: \n" + str(Arg)
            sys.exit()

    def readConf(self):
        configfile = open(self.path)
        lines = configfile.readlines()
        parsed_conf = self.parseConf(lines)
        if parsed_conf.has_key("readhistory"):
            try:
                parsed_conf["readhistory"] = int(parsed_conf["readhistory"])
            except ValueError:
                del parsed_conf["readhistory"]
        if parsed_conf.has_key("writehistory"):
            try:
                parsed_conf["writehistory"] = int(parsed_conf["writehistory"])
            except ValueError:
                del parsed_conf["writehistory"]
        if parsed_conf.has_key("timestamp"):
            parsed_conf["timestamp"] = parsed_conf["timestamp"]+" "
        if parsed_conf.has_key("clock"):
            parsed_conf["clock"] = parsed_conf["clock"]+" "
        self.config.update(parsed_conf)

    def writeConf(self):
        pass

    def parseConf(self, Conf):
        config = {}
        for i in Conf:
            if not (i.isspace() or i.startswith("#")) and (i.find("=")!=-1):
                a=i.split("=")
                a=a[:2]
                config[a[0].strip()] = a[1].strip()
        return config

class ImageLoader:
    def __init__(self,controller):
        self.controller = controller
        self.id = 0
        self.images = {}
        self.ids = {}

    def loadImage(self,url):
        self.images[self.id]={"getter":None,"data":None,"finished":False,"ids":[self.id],"url":url}
        d = deferToThread(self.reallyLoadImage,url,self.id)
        d.addCallback(self.finishedImage)
        self.id+=1
        return ("id",self.id-1)

    def reallyLoadImage(self,url,id):
        self.images[id]["getter"]=urllib.urlopen(url)
        self.images[id]["data"]=self.images[id]["getter"].read() # TODO: return chunks
        return (url,id)

    def finishedImage(self,result):
        url,id=result
        self.images[id]["getter"].close()
        del self.images[id]["getter"]
        self.images[id]["finished"]=True
        self.controller.view.loadedImage(id,self.images[id]["data"])

    def getImage(self,id):
        return self.images[id]["data"]

class KekzController(pluginmanager.manager): # TODO: Maybe don't use interhitance for pluginmanagement
    def __init__(self, interface, host, kwds):
        self.model = protocol.KekzChatClient(self)
        self.view = interface(self)
        pluginmanager.manager.__init__(self)
        if kwds.has_key("debug"):
            debug = kwds.pop("debug")
        else:
            debug = False
        if kwds.has_key("config"):
            path = kwds.pop("config")
            self.initConfig(debug, kwds, path)
        else:
            self.initConfig(debug, kwds)
        self.view.finishedReadingConfigfile()

        try:
            self.browser=webbrowser.get()
        except:
            self.browser=False

        self.nickname=""
        self.nickpattern = re.compile("",re.IGNORECASE)

        self.linkLists={}
        self.urls=re.compile(r"(?=\b)((?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|edu|pro|asia|cat|coop|int|tel|post|xxx|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?)(?=\b)",re.I)
        self.linkSyntax=re.compile(r"(?:(tail|head)(?::(\d+))?)|(?:(file):(\w*(?:\.\w*)?))|(?:(copy)(?::(-?\d+))?)",re.I)

        self.uid=0

        self.joinInfo=["Join","Login","Invite"]
        self.partInfo=["Part","Logout","Lost Connection","Nick-Collision","Ping Timeout","Kick"]

        self.receivedFirstRoomList = False
        self.loggedIn = False

        self.version="20100806"

        self.lookupMailId=[]

    def initConfig(self, debug, kwds, alt_conf = None):
        default_conf = {"timestamp" : "[%H:%M] ",
                "clock" : "[%H:%M:%S] ",
                "writehistory" : 200,
                "readhistory" : 5000,
                "nick" : "",
                "room" : "",
                "passwd" : ""}
        if alt_conf != None: 
            escapedtilde = os.path.expanduser(alt_conf)
            path = os.path.abspath(escapedtilde)
        else: 
            path = os.path.expanduser("~")+os.sep+".rattlekekz"+os.sep+"config"
        self.conf = ConfigFile(default_conf, path)
        if not debug:
            if not os.path.isfile(path):
                self.conf.createEmptyConf("""# this is the rattlekekz config. for more information visit the wiki at kekz.net
                                          #uncomment the following line to enable autologin. You have to insert nick, passwd and room for this to work
                                          #autologin = 1
                                          nick =
                                          #room have to be a comma seperated list of rooms
                                          room =
                                          #to generate the sha1 hash of your passwd execute this line: python -c 'import hashlib; print hashlib.sha1("YOUR_PASSWD").hexdigest()'
                                          passwd=
                                          
                                          #possible values for timestamp and clock are [%H:%M], [%H:%M:%S], %H%M and others
                                          timestamp = [%H:%M]
                                          #formating for the clock in the lower divider of the cliView
                                          clock = [%H:%M:%S]
                                          
                                          #the next two values are how many lines are stored in the history of the inputfield and the chatwindow
                                          writehistory=200
                                          readhistory=5000""")
            self.conf.readConf()

        def addKeyword(key, value):
            if key in ["clock", "timestamp"]:
                value = value + " "
            elif key in ["writehistory", "readhistory"]:
                try:
                    value = int(value)
                except:
                    return None
            self.conf.setValue(key, value)
        map(lambda (x,y): addKeyword(x,y), kwds.items())

    def getValue(self, key):
        value = self.conf.getValue(key)
        return value

    def startConnection(self,server,port):
        self.model.startConnection(server,port)

    def startReconnect(self):
        self.model.connector.disconnect()

    def decode(self, string):
        if type(string) is str:
            array=string.split("°")
        elif type(string) is unicode:
            array=string.split(u"°")
        textlist=[""]
        formatlist=["normal"]
        output={}
        for i in range(len(array)):
            nicks = []
            newtextlist,newformatlist = [""],["normal"]
            if i%2==0:
                pattern = self.nickpattern
                nicks = pattern.findall(array[i])
                if len(nicks) is 0:
                    textlist[-1]=textlist[-1]+array[i]
                else:
                    crap = pattern.split(array[i])
                    while (len(nicks) and len(crap)) is not 0:
                        if not crap[0].isspace():
                            newtextlist.append(crap.pop(0))
                            newformatlist.append(formatlist[-1])
                        else:
                            newtextlist[-1] = newtextlist[-1] + crap.pop(0)
                        newtextlist.append(nicks.pop(0))
                        newformatlist.append(("ownnick",formatlist[-1]))
                        newtextlist.append("")
                        newformatlist.append(formatlist[-1])
                    if (len(nicks) or len(crap)) is not 0:
                        if len(crap) is not 0:
                            for x in crap:
                                if not x.isspace():
                                    newtextlist.append(x)
                                    newformatlist.append(formatlist[-1])
                                else:
                                    newtextlist[-1] = newtextlist[-1] + x
                        elif len(nicks) is not 0:
                            for x in nicks:
                                newtextlist.append(x)
                                newformatlist.append(("ownnick",formatlist[-1]))
                                newtextlist.append("")
                                newformatlist.append(formatlist[-1])
                    textlist.extend(newtextlist)
                    formatlist.extend(newformatlist)
                continue
            elif len(array[i])==0:
                textlist[-1]=textlist[-1]+"°"
                continue
            if array[i].startswith("!"):
                array[i]="$http://kekz.net/imgstore/"+array[i][1:]
            if array[i].startswith("$"):
                textlist.append(array[i][1:])
                if formatlist[-1]=="normal":
                    formatlist.append("imageurl")
                else:
                    formatlist.append(formatlist[-1]+",imageurl")
                formatlist.append(formatlist[-2])
            if array[i].startswith("i"):
                textlist.append(array[i][1:])
                if formatlist[-1]=="normal":
                    formatlist.append("sb")
                else:
                    formatlist.append(formatlist[-1]+",sb")
                formatlist.append(formatlist[-2])
            if array[i].startswith("n"):
                textlist.append("\n")
                formatlist.append("newline")
                if array[i]=="nu": 
                    textlist.append(" > > > ")
                    formatlist.append(formatlist[-2])
                elif array[i]=="np":
                    textlist.append("\n")
                    formatlist.append("newline")
                    formatlist.append(formatlist[-3])
                    textlist.append("")
                elif array[i]=="nr":
                    textlist.append("")
                    formatlist.append("hline")
                    formatlist.append(formatlist[-2])
                    textlist.append("")
                else:
                    formatlist.append(formatlist[-2])
                    textlist.append("")
                continue
            if array[i].startswith("l"):
                if array[i][1:].startswith("/"):
                    textlist.append(array[i][1:])
                else:
                    textlist.append("/"+array[i][1:])
                formatlist.append("button")
                formatlist.append(formatlist[-2])
            if len(array[i])==2:
                formatlist=self.formatopts(formatlist,array[i])
            textlist.append("")
        if len(textlist)!=len(formatlist):
            formatlist=formatlist[:len(textlist)]
            textlist=textlist[:len(formatlist)]
        for i in range(len(textlist)):
            if textlist[i]=="" and formatlist[i]=="":
                del textlist[i]
                del formatlist[i]
        return textlist,formatlist

    def formatopts(self, formlist, opt):
        kekzformat={"cr":"red",
                    "cb":"blue",
                    "cg":"green",
                    "ca":"gray",
                    "cc":"cyan",
                    "cm":"magenta",
                    "co":"orange",
                    "cp":"pink",
                    "cy":"yellow",
                    "cw":"white",
                    "cx":"reset",
                    "fi":"italic",
                    "fb":"bold"}
        if opt=="fx":
            formlist.append("normal")
        if kekzformat.has_key(opt):
            if formlist[-1]=="normal":
                formlist.append(kekzformat[opt])
            elif formlist[-1]==kekzformat[opt]:
                formlist.append("normal")
            elif not formlist[-1].find(kekzformat[opt]+",")==-1:
                formlist.append(formlist[-1].replace(kekzformat[opt]+",",""))
            elif not formlist[-1].find(","+kekzformat[opt])==-1:
                formlist.append(formlist[-1].replace(","+kekzformat[opt],""))
            else:
                formlist.append(formlist[-1]+","+kekzformat[opt])
        return formlist

    def checkPassword(self,password):
        if len(password)>4:
            return True
        else:
            return False

    def openURL(self,url):
        """opens the url given as a string in the default browser"""
        if self.browser:
            self.browser.open(url)
        else:
            self.gotException("no browser detected")

    def appendLinks(self,room,links):
        if self.linkLists.has_key(room.lower()):
            self.linkLists[room.lower()].extend(links)
        else:
            self.linkLists[room.lower()]=links

    def linkTab(self,room,command):
        """opens an infoTab with the list of URLs of the room"""
        command=command.strip()
        if command=="":
            if self.linkLists.has_key(room.lower()):
                self.view.openLinkTab(room,self.linkLists[room.lower()])
            else:
                self.botMsg("","no links for room "+room+".")
        else:
            command=self.linkSyntax.match(command)
            if command:
                if self.linkLists.has_key(room.lower()):
                    if command.group(1) == "head":
                        if command.group(2) == None:
                            self.view.openLinkTab(room,self.linkLists[room.lower()])
                        else:
                            self.view.openLinkTab(room,self.linkLists[room.lower()][:int(command.group(2))])
                    elif command.group(1) == "tail":
                        if command.group(2) == None:
                            self.view.openLinkTab(room,self.linkLists[room.lower()])
                        else:
                            self.view.openLinkTab(room,self.linkLists[room.lower()][-int(command.group(2)):])
                    elif command.group(3) == "file":
                        file=open(os.path.expanduser("~")+os.sep+command.group(4),"w")
                        for i in self.linkLists[room.lower()]:
                            file.write(i+"\n")
                        file.close()
                    elif command.group(5) == "copy":
                        print "STUB: implement this" #TODO: do this
                else:
                    self.botMsg("rattlekekz","no links for room "+room+".")
            else:
                self.botMsg("rattlekekz","usage: /links [(head|tail)[:linecount], copy[:+/-lines], file:path].")

    def loadImage(self,url):
        try:
            return self.ImageLoader.loadImage(url)
        except AttributeError:
            self.ImageLoader = ImageLoader(self)
            return self.ImageLoader.loadImage(url)

    def getImage(self,id):
        return self.ImageLoader.getImage(id)

    """following methods transport data from the View to the model"""
    def sendLogin(self, nick, passwd, rooms):
        self.nick,self.rooms=nick, rooms
        self.passwd=sha1(passwd).hexdigest()
        self.rooms.strip()
        re.sub("\s","",self.rooms)
        self.nick.strip()
        self.model.sendLogin(self.nick, self.passwd, self.rooms)

    def registerNick(self,nick,passwd,email):
        if not self.checkPassword(passwd):
            self.view.gotException("password is to short")
        else:
            self.model.registerNick(nick,sha1(passwd).hexdigest(),email)

    def changePassword(self,passwd,passwdnew):
        if not self.checkPassword(passwdnew):
            self.view.gotException("password is to short")
        else:
            self.model.changePassword(sha1(passwd).hexdigest(),sha1(passwdnew).hexdigest())
        
    def updateProfile(self,name,location,homepage,hobbies,signature,passwd):
        self.model.updateProfile(name,location,homepage,hobbies,signature,sha1(passwd).hexdigest())

    def sendStr(self,channel, string):
        if string.startswith("/"):
            self.sendSlashCommand(channel,string)
        elif channel.startswith("#"):
            self.model.sendPrivate(channel[1:],string)
        else:
            self.model.sendPublic(channel,string)

    def sendSlashCommand(self,channel,string):
        if string.lower().startswith("/m ") or string.lower() is "/m":
            #self.view.addRoom("$mail","MailRoom")
            #self.view.changeTab("$mail")
            self.view.openMailTab()
            self.refreshMaillist()
        elif string.lower().startswith("/reconnect"):
            self.startReconnect()
        elif string.lower().startswith("/load"):
            string = string[6:].split(' ')
            self.loadPlugin(string.pop(0),string)
        elif string.lower().startswith("/unload"):
            string = string[8:].split(' ')
            self.unloadPlugin(string.pop(0))
        elif string.lower().startswith('/links'):
            self.linkTab(channel,string[6:])
        elif string.lower().startswith('/sendfile'):
            string = string[10:].split(" ")
            target = string.pop(0)
            path = " ".join(string)
            self.offerFile(target,path)
        elif string.lower().startswith("/quit"):
            self.view.quit()
        elif string.lower().startswith("/showtopic"):
            if not channel.startswith("#"):
                self.view.showTopic(channel)
        elif string.lower().startswith("/ctcp"):
            cpmsg=string.split(' ')[1:]
            if len(cpmsg) > 1:
                user=cpmsg.pop(0)
                cpmsg=" ".join(cpmsg)
                self.sendCtcpRequest(user,cpmsg)
        elif string.lower().startswith("/sendm"):
            mail=string.split(' ')[1:]
            if len(mail) > 1:
                user=mail.pop(0)
                mail=" ".join(mail)
                self.sendMail(user,mail)
        elif string.lower().startswith("/p ") or string.lower() is "/p" or string.lower().startswith("/msg"):
            string=string.split(' ')[1:]
            if len(string) > 1:
                user=string.pop(0)
                string=" ".join(string)
                self.model.sendPrivate(user,string)
        elif not channel.startswith("#"):
            liste=string.split(" ")
            self.model.sendCommand(liste[0],channel," ".join(liste[1:]))

    def sendJoin(self,room):
        self.model.sendJoin(room)

    def sendMail(self,nick,msg):
        self.sendMailCount+=1
        uid="Mail_"+str(self.sendMailCount)
        self.lookupSendId.update({uid:nick})
        self.model.sendMail(nick,msg,uid)

    def refreshMaillist(self):
        self.model.getMailCount()
        self.model.getMailStubs()

    def getMail(self,index):
        try:
            uid=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("mail number"+str(index)+" does not exist")
        else:
            self.model.getMail(str(uid))

    def deleteMail(self,index):
        try:
            uid=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("mail number"+str(index)+" does not exist")
        else:
            self.model.deleteMail(uid)

    def deleteAllMails(self):
        self.model.deleteAllMails()

    def quitConnection(self):
        self.model.quitConnection()

    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.view.fubar()

    def startedConnection(self):
        """indicates that the model is connecting."""
        self.view.startedConnection()

    def lostConnection(self, reason):
        self.view.connectionLost(reason)

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        self.view.connectionFailed()

    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendIdentify(self.view.name, self.version, sys.platform, "Python "+pythonversion[0])
        self.model.getRooms()

    def receivedRooms(self,rooms):
        if self.model.reconnecting:
            rooms=",".join(self.view.getRooms())
            self.model.sendLogin(self.nick,self.passwd,rooms)
        else:
            if not self.receivedFirstRoomList:
                array = map(self.getValue, ["autologin", "nick", "passwd", "room"])
                self.view.receivedPreLoginData(rooms,array[1:])
                self.receivedFirstRoomList=True
                if array[0]=="True" or array[0]=="1":
                    self.nick,self.passwd,self.rooms=array[1],array[2],array[3]
                    self.model.sendLogin(array[1],array[2],array[3])
                # now the array is: [nick,passwd,room]
            else:
                self.view.updateRooms(rooms)


    def successLogin(self,nick,status,room):
        self.loggedIn = True
        self.nickname=nick
        regex = self.conf.getValue("regex")
        if regex != None:
            self.nickpattern = re.compile(regex, re.IGNORECASE)
        else:
            self.nickpattern = re.compile(self.nickname,re.IGNORECASE)
        self.lookupSendId={}
        self.sendMailCount=0
        self.Userlist={room:[]}
        if self.model.reconnecting:
            self.view.successLogin(nick,status,room,True)
            self.model.reconnecting = False
        else:
            self.view.successLogin(nick,status,room)
        autoload_plugins = self.getValue("autoload_plugins")
        if autoload_plugins != None:
            map(lambda x: self.loadPlugin(x.strip()), autoload_plugins.split(","))

    def successMailLogin(self):
        self.sendMailCount=0
        self.lookupSendId={}
        self.lookupMailId=[]
        self.getMaillist()

    def successRegister(self):
        self.view.successRegister()

    def successNewPassword(self):
        self.view.successNewPassword()

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        self.view.addRoom("$edit","EditRoom")
        self.view.receivedProfile(name,ort,homepage,hobbies,signature)

    def successNewProfile(self):
        self.view.successNewProfile()

    def receivedPing(self,deltaPing):
        self.view.receivedPing(deltaPing)

    def pingTimeout(self):
        self.lostConnection("PingTimeout")

    def receivedMsg(self,nick,room,msg):
        self.printMsg(nick,msg,room,0)

    def receivedRoomMsg(self,room,msg):
        self.printMsg("",msg,room,1)

    def privMsg(self,nick,msg):
        self.printMsg(nick,msg,"",2)

    def privOnline(self,nick):
        self.printMsg("",nick+" is now online.","#"+nick,4)

    def privOffline(self,nick):
        self.printMsg("",nick+" has gone offline.","#"+nick,4)

    def ownprivMsg(self,nick,msg):
        self.printMsg(nick,msg,"",3)

    def botMsg(self,nick,msg):
        self.printMsg(nick,msg,"",4)

    def printMsg(self,nick,message,room,state):
        self.appendLinks(room,self.urls.findall(message))
        activeTab=self.view.getActiveTab()
        msg=[]
        msg.append(self.view.timestamp(time.strftime(self.getValue("timestamp") ,time.localtime(time.time()))))
        if state==0 or state==2 or state==4:
            if nick!="":
                if nick.lower()==self.nickname.lower():
                    msg.append(self.view.colorizeText("green",nick+": "))
                else:    
                    msg.append(self.view.colorizeText("blue",nick+": "))
        elif state==3:
            msg.append(self.view.colorizeText("green",str(self.nickname)+": "))
        if state==2 or state==3:
            room="#"+nick
            self.view.addRoom(room,"PrivRoom")
        if state==4:
            pre,room=self.view.minorInfo(room,nick)
            if pre!=None:
                msg.append(pre)
        if not activeTab == "$login":
            importance=2
            if (self.nickpattern.search(message) is not None) or state==2:
                importance=3 
            elif state==5:
                importance=1
            else:
                importance=2
            if  nick.lower()!=self.nickname.lower():
                self.view.highlightTab(room,importance)
        if state==5:
            msg.append(self.view.colorizeText("blue",self.view.escapeText(message)))
        else:
            msg.extend(self.view.deparse(message))
        self.view.printMsg(room,msg)

    def gotHandshakeException(self, message):
        self.view.gotException("rattlekekz have to be updated")

    def gotLoginException(self, message):
        self.view.gotLoginException(message)

    def gotException(self, message):
        self.view.gotException(message)

    def receivedUserlist(self,room,users):
        self.Userlist[room]=users
        self.Userlist[room].sort(key=lambda x: self.stringHandler(x[0]).lower())
        self.view.listUser(room,users)

    def joinUser(self,room,nick,state,joinmsg):
        self.Userlist[room].append([nick,False,state])
        self.Userlist[room].sort(key=lambda x: self.stringHandler(x[0]).lower())
        self.view.listUser(room,self.Userlist[room])
        #self.printMsg("","(>>>) "+nick+" enters the room ("+self.joinInfo[int(joinmsg)]+")",room,5)
        self.printMsg("","(>>>) "+nick+" enters the room ("+joinmsg+")",room,5)

    def quitUser(self,room,nick,partmsg):
        for i in self.Userlist[room]:
            if i[0]==nick:
                self.Userlist[room].remove(i)
        self.view.listUser(room,self.Userlist[room])
        #self.printMsg("","(<<<) "+nick+" left the room ("+self.partInfo[int(partmsg)]+")",room,5)
        self.printMsg("","(<<<) "+nick+" left the room ("+partmsg+")",room,5)

    def changedUserdata(self,room,nick,away,state):
        for i in self.Userlist[room]:
            if i[0].lower()==nick.lower():
                i[1],i[2]=away,state
        self.view.listUser(room,self.Userlist[room])

    def meJoin(self,room,background):
        self.Userlist.update({room:[]})
        self.view.meJoin(room,background)

    def mePart(self,room):
        del self.Userlist[room]
        self.view.mePart(room)

    def meGo(self,oldroom,newroom):
        del self.Userlist[oldroom]
        self.Userlist.update({newroom:[]})
        self.view.meGo(oldroom,newroom)

    def newTopic(self,room,topic):
        self.view.newTopic(room,topic)

    def loggedOut(self):
        self.view.loggedOut()

    def receivedInformation(self,info):
        self.view.receivedInformation(info)

    def stringHandler(self,string,returnunicode=False):
        if type(string) is not unicode:
            if returnunicode:
                return str(string).decode("utf_8")
            else:
                return str(string)
        else:
            if returnunicode:
                return string
            else:
                return string.encode("utf_8")

    def receivedWhois(self,data):
        Output=[]
        for i in range(0,len(data),2):
            key,value = data[i],data[i+1]
            value=self.stringHandler(value,True)
            if key=="nick":
                nick=value
            if key == "regdata": key=u"registered since "
            elif key == "logindate": key=u"logged in since "
            elif key == "lastseen": key=u"logged out since "
            if key == "state":
                key = u"raw"
                if value == u"off": value=u"the user is currently °fb°°cr°offline°fx°.°nn°"
                elif value == u"on": value=u"the user is currently °fb°°cg°online°fx°.°nn°"
                elif value == u"mail": value=u"the user is currently °fb°°cr°offline°fx°, but receives °fb°°cb°mail°fx°.°nn°"
                else:
                    value=u"the status is unknown.°nn°"
            if key == "kekz":
                key=u"raw"
                table={"0":"no","1":"one","2":"two","3":"three","4":"four","5":"five","6":"six","7":"seven","8":"eight","9":"nine"}
                if table.has_key(value):
                    value=table[value]
                if not value == "one":
                    value=u"°cb° %s got °fb°%s°fb° cookies left." % (nick,value)
                else:
                    value=u"°cb° %s got °fb°%s°fb° cookie left." % (nick,value)
            if key == "usertext":
                key=u"raw"
            if key == "header":
                key=u"raw"
                value=u"°nn°°nn°°cb°°fb°%s°fb°°cb°" % (value.capitalize())
            if not key == u"raw":
                key = self.stringHandler(key.capitalize(),True)
                value=u"°fb°%s:°fb° %s" % (key,value)
            value = self.stringHandler(value)
            Output.append(value)
        self.view.receivedWhois(self.stringHandler(nick), Output)

    def closedWhois(self,user):
        self.model.sendWhoisClose(user)

    def receivedCtcpRequest(self,user,cpmsg):
        self.printMsg(user+' [CTCP]',cpmsg,self.view.getActiveTab(),0)
        if cpmsg.lower() == 'version':
            self.sendCtcpReply(user,cpmsg+' '+self.view.name+' ('+str(self.view.version)+') [core: '+self.version+']')
        elif cpmsg.lower() == 'ping':
            self.sendCtcpReply(user,cpmsg+' ping')
        else:
            self.sendCtcpReply(user,cpmsg+' (unknown)')

    def sendCtcpReply(self,user,cpmsg):
        self.model.sendCtcpReply(user,cpmsg)

    def sendCtcpRequest(self,user,cpmsg):
        self.model.sendCtcpRequest(user,cpmsg)

    def receivedCtcpReply(self,user,cpanswer):
        self.printMsg(user+' [CTCPAnswer]',cpanswer,self.view.getActiveTab(),0)

    def sendMailsuccessful(self,uid):
        self.view.MailInfo("the mail to "+self.lookupSendId[uid]+" was transmitted succesfully")
        del self.lookupSendId[uid]

    def sendBullshit(self,bullshit):
        self.model.sendHandshake(bullshit)

    def sendMailfailed(self,uid,msg):
        self.view.MailInfo("the mail to "+self.lookupSendId[uid]+" could not be transmitted: "+msg)
        del self.lookupSendId[uid]

    def receivedMails(self,userid,mailcount,mails):
        for i in range(len(mails)):
            self.lookupMailId.append(mails[i]["mid"])
            del mails[i]["mid"]
            mails[i].update({"index":i})
        self.view.receivedMails(userid,mailcount,mails)

    def receivedMailcount(self,unreadmails,allmails):
        self.view.MailInfo(str(unreadmails)+" unread messages, "+str(allmails)+" messages")

    def requestMailfailed(self,error):
        self.view.MailInfo("the mail wasn't found: "+error)

    def requestMailsuccessful(self,user,date,mail):
        self.view.printMail(user,date,mail)

    def receivedNewMail(self,nick,header):
        #self.view.minorInfo("You received a message from "+nick+": "+header)
        self.printMsg("","You received a message from "+nick+": "+header,"",4)

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)

