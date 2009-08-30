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
import os, sys, re, time, base64, random
from hashlib import sha1, md5
from twisted.internet.task import LoopingCall


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
            except:
                del parsed_conf["readhistory"]
        if parsed_conf.has_key("writehistory"):
            try:
                parsed_conf["writehistory"] = int(parsed_conf["writehistory"])
            except:
                del parsed_conf["writehistory"]
        self.config.update(self.parseConf(lines))

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

class FileTransfer:
    def __init__(self, encoder, decoder):
        self.offered = []
        self.transfers = {}
        self.decodeJSON = decoder
        self.encodeJSON = encoder

    def sendJSON(self,user,comand): # TODO: implement error handling (e.g. unreachable host)
        self.sendCPMsg(user,self.encodeJSON(comand))

    def offerFile(self,user,path):
        if os.path.isfile(path):
            data = open(path,"rb")
            filename = data.name.split(os.sep).pop()
            filesize = os.path.getsize(path)
            comand = {"transfer":"init","filename":filename,"size":filesize}
            self.offered.append(comand)
            self.offered[-1]["file"]=data
            self.offered[-1]["user"]=user
            self.sendJSON(user,{"transfer":"init","filename":filename,"size":filesize})
        elif os.path.isdir(path):
            self.botMsg("filetransfer",path+" is a directory") # implement directory-transmission?
        else:
            self.botMsg("filetransfer",path+" does not exist")

    def acceptOffer(self,uid):
        self.sendJSON(self.transfers[uid]["user"],{"transfer":"accept", "filename":self.transfers[uid]["filename"], "id":uid})

    def startSubmit(self,uid):
        self.transfers[uid]["hash"]=md5()
        self.transfers[uid]["loop"]=LoopingCall(self.doSubmit,uid)
        self.transfers[uid]["loop"].start(1)

    def doSubmit(self,uid):
        data = self.transfers[uid]["file"].read(2684355) # only read 64 percent of 4kib because of 36 percent overhead by base64
        self.transfers[uid]["hash"].update(data)
        if data is not "":
            data = base64.b64encode(data)
            self.sendJSON(self.transfers[uid]["user"],{"transfer":"data", "id":uid, "base64":data})
        else:
            self.transfers[uid]["loop"].stop()
            self.sendJSON(self.transfers[uid]["user"],{"transfer":"finished", "id":uid, "hash":self.transfers[uid]["hash"].hexdigest()})

    def receivedData(self,uid,base64_data):
        data = os.environ["HOME"]+os.sep+".rattlekekz"+os.sep+"transfers"+os.sep+self.transfers[uid]["filename"] # TODO: implement choosen filename and location
        filepath = os.path.dirname(data)
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                pass
            else:
                self.botMsg("filetransfer",filepath+" is not a directory!")
        else:
            os.makedirs(filepath)
        if not os.path.exists(data):
            self.transfers[uid]["file"] = open(data,"ab")
            self.transfers[uid]["file"].write(base64.b64decode(base64_data))
            self.transfers[uid]["file"].flush()
        else:
            if self.transfers[uid].has_key("file"): # TODO: implement continue
                self.transfers[uid]["file"].write(base64.b64decode(base64_data))
                self.transfers[uid]["file"].flush()
            else:
                self.botMsg("filetransfer",data+"already exists!")

    def finishedTransfer(self,uid,hash):
        self.transfers[uid]["file"].close()
        self.transfers[uid]["file"]=open(os.environ["HOME"]+os.sep+".rattlekekz"+os.sep+"transfers"+os.sep+self.transfers[uid]["filename"],"rb")
        self.transfers[uid]["hash"]=hash
        self.transfers[uid]["ownHash"]=md5()
        self.transfers[uid]["loop"]=LoopingCall(self.getHash,uid)
        self.transfers[uid]["loop"].start(1)

    def getHash(self,uid):
        data = self.transfers[uid]["file"].read()
        if data is not "":
            self.transfers[uid]["ownHash"].update(data)
        else:
            self.transfers[uid]["loop"].stop()
            if self.transfers[uid]["hash"] == self.transfers[uid]["ownHash"].hexdigest():
                self.botMsg("filetransfer",self.transfers[uid]["filename"]+" successful received and hashed.")
            else:
                self.botMsg("filetransfer",self.transfers[uid]["filename"]+" hash error")
            self.transfers[uid]["file"].close() # TODO: remove references from self.transfers

class KekzController(pluginmanager.manager, FileTransfer): # TODO: Maybe don't use interhitance for pluginmanagement
    def __init__(self, interface, kwds):
        self.model = protocol.KekzChatClient(self)
        self.view = interface(self)
        pluginmanager.manager.__init__(self)
        FileTransfer.__init__(self, self.model.encoder, self.model.decoder)
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

        self.nickname=""
        self.nickpattern = re.compile("",re.IGNORECASE)
        
        self.joinInfo=["Join","Login","Invite"]
        self.partInfo=["Part","Logout","Lost Connection","Nick-Collision","Ping Timeout","Kick"]

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
            path = os.environ["HOME"]+os.sep+".rattlekekz"+os.sep+"config"
        self.conf = ConfigFile(default_conf, path)
        if not debug:
            if not os.path.isfile(path):
                self.conf.createEmptyConf("# this is the kekznet config. for more information visit the wiki at kekz.net")
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

    def sendIdentify(self,passwd):
        sha1_hash=sha1(passwd).hexdigest()
        md5_hash= md5.new(sha1_hash).hexdigest()
        self.model.sendIdentify(md5_hash)

    def sendStr(self,channel, string):
        if string.startswith("/"):
            self.sendSlashCommand(channel,string)
        elif channel.startswith("#"):
            self.model.sendPrivMsg(channel[1:],string)
        else:
            self.model.sendMsg(channel,string)

    def sendSlashCommand(self,channel,string):
        if string.lower().startswith("/m ") or string.lower() is "/m":
            #self.view.addRoom("$mail","MailRoom")
            #self.view.changeTab("$mail")
            self.view.openMailTab()
            self.refreshMaillist()
        elif string.lower().startswith("/load"):
            string = string[6:].split(' ')
            self.loadPlugin(string.pop(0),string)
        elif string.lower().startswith("/unload"):
            string = string[8:].split(' ')
            self.unloadPlugin(string.pop(0))
        elif string.lower().startswith('/sendfile'):
            string = string[10:].split(" ")
            target = string.pop(0)
            path = " ".join(string)
            self.offerFile(target,path)
        elif string.lower().startswith('/accept'):
            uid=re.findall("\d\d\d",string[8:])
            if len(uid) is 0:
                uid=re.findall("\d\d",string[8:])
                if len(uid) is 0:
                    uid=re.findall("\d",string[8:])
                    if len(uid) is not 1:
                        self.botMsg("filetransfer","usage: /accept [id]")
                    else:
                        uid = int(uid[0])
                else:
                    uid = int(uid[0])
            elif len(uid) is not 1:
                self.botMsg("filetransfer","please type a proper id.")
            else:
                uid = int(uid[0])
            if self.transfers.has_key(uid):
                self.acceptOffer(uid)
            else:
                self.botMsg("filetransfer","id doesn't exist.")
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
                self.sendCPMsg(user,cpmsg)
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
                self.model.sendPrivMsg(user,string)
        elif not channel.startswith("#"):
            liste=string.split(" ")
            self.model.sendSlashCommand(liste[0],channel," ".join(liste[1:]))

    def sendJoin(self,room):
        self.model.sendJoin(room)

    def sendMail(self,nick,msg):
        self.sendMailCount+=1
        id="Mail_"+str(self.sendMailCount) # TODO: Fix usage of id to for example uid
        self.lookupSendId.update({id:nick})
        self.model.sendMail(nick,msg,id)

    def refreshMaillist(self):
        self.model.getMailCount()
        self.model.getMaillist()

    def getMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("mail number"+str(index)+" does not exist")
        else:
            self.model.getMail(str(id))

    def deleteMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("mail number"+str(index)+" does not exist")
        else:
            self.model.deleteMail(str(id))

    def deleteAllMails(self):
        self.model.deleteAllMails()

    def quitConnection(self):
        self.model.quitConnection()

    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.view.fubar()

    def startedConnection(self):
        """indicates that the model is connecting. Here should be a call to the view later on"""
        pass # TODO: Add this call

    def lostConnection(self, reason):
        self.view.connectionLost(reason)

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        self.view.connectionFailed()

    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.view.name, self.view.version, self.view.revision, sys.platform, "Python "+pythonversion[0])
        self.model.getRooms()

    def receivedRooms(self,rooms):
        array = map(self.getValue, ["autologin", "nick", "passwd", "room"])
        if array[0]=="True" or array[0]=="1":
            self.model.sendLogin(array[1],array[2],array[3])
        else:
            self.view.receivedPreLoginData(rooms,array[1:])
            # now the array is: [nick,passwd,room]


    def successLogin(self,nick,status,room):
        self.nickname=nick
        regex = self.conf.getValue("regex")
        if regex != None:
            self.nickpattern = re.compile(regex, re.IGNORECASE)
        else:
            self.nickpattern = re.compile(self.nickname,re.IGNORECASE)
        self.lookupSendId={}
        self.sendMailCount=0
        self.Userlist={room:[]}
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

    def securityCheck(self, infotext):
        self.view.securityCheck(infotext)

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

    def ownprivMsg(self,nick,msg):
        self.printMsg(nick,msg,"",3)
        
    def botMsg(self,nick,msg):
        self.printMsg(nick,msg,"",4)

    def printMsg(self,nick,message,room,state):
        activeTab=self.view.getActiveTab()
        msg=[]
        msg.append(self.view.timestamp(time.strftime(self.getValue("timestamp") ,time.localtime(time.time()))))
        if state==0 or state==2 or state==4:
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
            if len(self.view.lookupRooms)==1:
                self.view.addRoom("$info","InfoRoom")
                self.view.changeTab("$info")
                activeTab="$info"
            room=activeTab
        if not (activeTab == "$login" or room.lower() == self.view.getActiveTab()):
            importance=2
            if (self.nickpattern.search(message) is not None) or state==2:
                importance=3 
            elif state==5:
                importance=1
            else:
                importance=2
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
        self.view.listUser(room,users)

    def joinUser(self,room,nick,state,joinmsg):
        self.Userlist[room].append([nick,False,state])
        self.Userlist[room].sort(key=lambda x: self.stringHandler(x[0]).lower())
        for i in self.Userlist[room]:
            if i[0].startswith("~"):
                index=self.Userlist[room].index(i)
                self.Userlist[room].insert(0,i)
                del self.Userlist[room][index+1] 
        self.view.listUser(room,self.Userlist[room])
        self.printMsg("","(>>>) "+nick+" enters the room ("+self.joinInfo[int(joinmsg)]+")",room,5)

    def quitUser(self,room,nick,partmsg):
        for i in self.Userlist[room]:
            if i[0]==nick:
                self.Userlist[room].remove(i)
        self.view.listUser(room,self.Userlist[room])
        self.printMsg("","(<<<) "+nick+" left the room ("+self.partInfo[int(partmsg)]+")",room,5)

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
                key = u"<raw>"
                if value == u"off": value=u"the user is currently °fb°°cr°offline°fx°.°nn°"
                elif value == u"on": value=u"the user is currently °fb°°cg°online°fx°.°nn°"
                elif value == u"mail": value=u"the user is currently °fb°°cr°offline°fx°, but receives °fb°°cb°mail°fx°.°nn°"
                else:
                    value=u"the status is unknown.°nn°"
            if key == "kekz":
                key=u"<raw>"
                value=u"°cb° %s got °fb°%sx°fb° cookies left." % (nick,value)
            if key == "usertext":
                key=u"<raw>"
            if key == "<h1>":
                key=u"<raw>"
                value=u"°nn°°nn°°cb°°fb°%s°fb°°cb°" % (value.capitalize())
            if not key == u"<raw>":
                key = self.stringHandler(key.capitalize(),True)
                value=u"°fb°%s:°fb° %s" % (key,value)
            value = self.stringHandler(value)
            Output.append(value)
        self.view.receivedWhois(self.stringHandler(nick), Output)

    def receivedCPMsg(self,user,cpmsg):
        try:
            data = self.decodeJSON(cpmsg)
            if not type(data) == dict:
                raise ValueError("json not a dictionary.")
            if data.has_key("transfer"):
                if data["transfer"] != "init":
                    uid = data["id"]
                    if data["transfer"] == "data":
                        self.receivedData(data[uid],data["base64"])
                    elif data["transfer"] == "resume":
                        self.botMsg("filetransfer ["+user+"]","resume not implemented yet.") # TODO: well ... implement it fuck0r :P
                    elif data["transfer"] == "accept":
                        for i in range(len(self.offered)):
                            if self.offered[i]["filename"] == data["filename"]:
                                if not self.transfers.has_key(uid):
                                    self.transfers[uid]=self.offered[i]
                                    self.transfers[uid]["transfer"]=data["transfer"]
                                    self.startSubmit(uid)
                                else:
                                    self.sendJSON(user,{"transfer":"error","id":uid,"description":"You accepted my transfer with an id I am already using"})
                                del self.offered[i]
                            elif i == len(self.offered)-1:
                                self.sendJSON(user,{"transfer":"error","id":uid,"description":"You accepted a transfer I didn't offer"})
                    elif data["transfer"] == "reject":
                        for i in range(len(offered)):
                            if self.offered[i]["filename"] == data["filename"]:
                                self.controller.botMsg("filetransfer",user+" rejected Transmission of "+data["filename"])
                                del offered[i]
                    elif data["transfer"] == "finished":
                        self.finishedTransfer(uid,data["hash"])
                    elif data["transfer"] == "error": # TODO: handling for failed transmissions
                        self.controller.botMsg("filetransfer",data["description"])
                else:
                    filename,size = data["filename"],data["size"]
                    count=0
                    while size > 1024:
                        size = size/1024
                        count=+1
                    if count != 0:
                        if count == 1:
                            disp_size=str(size)+" KiB"
                        elif count == 2:
                            disp_size=str(size)+" MiB"
                        elif count == 3:
                            disp_size=str(size)+" GiB"
                        elif count == 4:
                            disp_size=str(size)+" TiB"
                        size = size*(1024**count)
                    uid = random.randint(1,999)
                    self.transfers[uid]=data
                    self.transfers[uid]["user"]=user
                    self.botMsg("filetransfer",str(user)+" offered Transmission of "+str(filename)+" ("+disp_size+"). Type /accept "+str(uid)+" to accept the Transmission.")
            else:
                raise ValueError("not a filetransfer dictionary.")
        except ValueError:
            self.printMsg(user+' [CTCP]',cpmsg,self.view.getActiveTab(),0)
            if cpmsg.lower() == 'version':
                self.sendCPAnswer(user,cpmsg+' '+self.view.name+' ('+self.view.version+')')
            elif cpmsg.lower() == 'ping':
                self.sendCPAnswer(user,cpmsg+' ping')
            else:
                self.sendCPAnswer(user,cpmsg+' (unknown)')

    def sendCPAnswer(self,user,cpmsg):
        self.model.sendCPAnswer(user,cpmsg)

    def sendCPMsg(self,user,cpmsg):
        self.model.sendCPMsg(user,cpmsg)

    def receivedCPAnswer(self,user,cpanswer):
        self.printMsg(user+' [CTCPAnswer]',cpanswer,self.view.getActiveTab(),0)

    def sendMailsuccessful(self,id):
        self.view.MailInfo("the mail to "+self.lookupSendId[id]+" was transmitted succesfully")
        del self.lookupSendId[id]

    def sendBullshit(self,bullshit):
        self.model.sendHandshake(bullshit)

    def sendMailfailed(self,id,msg):
        self.view.MailInfo("the mail to "+self.lookupSendId[id]+" could not be transmitted: "+msg)
        del self.lookupSendId[id]

    def receivedMails(self,userid,mailcount,mails):
        self.lookupMailId=[]
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
        self.view.minorInfo("You received a message from "+nick+": "+header)

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)
