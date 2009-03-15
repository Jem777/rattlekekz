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

from rattlekekz.core import protocol
import os, sys, re, time
from hashlib import sha1, md5

class KekzController():
    def __init__(self, interface, *args, **kwds):
        self.kwds=kwds
        self.model = protocol.KekzChatClient(self)
        self.view = interface(self, *args, **kwds)
        self.readConfigfile()
        self.revision=self.view.revision
        self.nickname=""
        self.nickpattern = re.compile("",re.IGNORECASE)
        
        self.joinInfo=["Join","Login","Einladung"]
        self.partInfo=["Part","Logout","Lost Connection","Nick-Kollision","Ping Timeout","Kick"]
        self.plugins = {}

    def startConnection(self,server,port):
        self.iterPlugins('startConnection',self.model,[server,port])

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
                textlist[-1]=textlist[-1]+"\n"
                if array[i]=="nu": 
                    textlist[-1]=textlist[-1]+" > > > "
                elif array[i]=="np":
                    textlist[-1]=textlist[-1]+"\n"
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
        while len(textlist)>len(formatlist):
            formatlist.append("")
        while len(textlist)<len(formatlist):
            textlist.append("")
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


    def readConfigfile(self):
        #filepath=os.environ["HOME"]+os.sep+".kekznet.conf"
        filepath=os.environ["HOME"]+os.sep+"debug.conf"
        if os.path.exists(filepath) == False:
            dotkeckz=open(filepath, "w") # TODO: new name
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
            
        if self.kwds['timestamp'] == 1: self.timestamp="[%H:%M] "
        elif self.kwds['timestamp'] == 2: self.timestamp="[%H:%M:%S] "
        elif self.kwds['timestamp'] == 3: self.timestamp="[%H%M] "
        elif self.configfile.has_key("timestamp"):
            self.timestamp=self.configfile["timestamp"]+" "
        else:
            self.timestamp="[%H:%M] "
            
        self.readhistory,self.writehistory=5000,200
        if self.configfile.has_key("readhistory"):
            try:
                self.readhistory=int(self.configfile["readhistory"])
            except:
                pass
        if self.configfile.has_key("writehistory"):
            try:
                self.writehistory=int(self.configfile["writehistory"])
            except:
                pass
        if self.configfile.has_key("clock"):
            self.clockformat=self.configfile["clock"]+" "
        else:
            self.clockformat="[%H:%M:%S] "
        self.iterPlugins('setClock',self.view)


    def checkPassword(self,password):
        if len(password)>4:
            return True
        else:
            return False

    def loadPlugin(self,plugin,params=[]):
        """this option is called by the view to load any plugins."""
        try:
            if not self.plugins.has_key(plugin):
                self.plugins[plugin]=__import__('rattlekekz.plugins',fromlist=[plugin])
                self.plugins[plugin]=getattr(self.plugins[plugin],plugin)
                try:
                    self.plugins[plugin]=self.plugins[plugin].plugin(self,self.model,self.view,*params)
                except:
                    del self.plugins[plugin]
                    self.iterPlugins('gotException',self.view,["Error executing %s." % plugin])
            else:
                self.iterPlugins('gotException',self.view,["%s is already loaded" % plugin])
        except:
            self.iterPlugins('gotException',self.view,["Error due loading of %s. May it doesn't exist, is damaged or some depencies aren't installed?" % plugin])

    def unloadPlugin(self,plugin):
        try:
            self.plugins[plugin].unload()
            del self.plugins[plugin]
        except:
            try:
                del self.view.plugins[plugin]
                del self.model.plugins[plugin]
                del self.plugins[plugin]
            except:
                self.gotException('unable to unload plugin %s.' % plugin)

    def iterPlugins(self,method,dest,kwds=[]):
        taken,handled=False,False
        for i in self.plugins:
            try:
                value = getattr(self.plugins[i], method)(self,*kwds) # TODO: May add dest-param. Just in case
                if value is 'handled':
                    handled=True
                    break
                elif value is 'taken':
                    taken=True
                    continue
            except AttributeError:
                pass # TODO: May add some message or so.
            except:
                pass # TODO: add message for error in plugin xy
        if not handled:
            getattr(dest, method)(*kwds)

    """following methods transport data from the View to the model"""
    def sendLogin(self, nick, passwd, rooms):
        self.nick,self.rooms=nick, rooms
        self.passwd=sha1(passwd).hexdigest()
        self.rooms.strip()
        re.sub("\s","",self.rooms)
        self.nick.strip()
        self.iterPlugins('sendLogin',self.model,[self.nick, self.passwd, self.rooms])

    def registerNick(self,nick,passwd,email):
        if not self.checkPassword(passwd):
            self.iterPlugins('gotException',self.view,["Ungüliges Passwort"])
        else:
            self.iterPlugins('registerNick',self.model,[nick,sha1(passwd).hexdigest(),email])

    def changePassword(self,passwd,passwdnew):
        if not self.checkPassword(passwdnew):
            self.iterPlugins('gotException',self.view,["Ungüliges Passwort"])
        else:
            self.iterPlugins('changePassword',self.model,[sha1(passwd).hexdigest(),sha1(passwdnew).hexdigest()])
        
    def updateProfile(self,name,location,homepage,hobbies,signature,passwd):
        self.iterPlugins('updateProfile',self.model,[name,location,homepage,hobbies,signature,sha1(passwd).hexdigest()])

    def sendIdentify(self,passwd):
        sha1_hash=sha1(passwd).hexdigest()
        md5_hash= md5.new(sha1_hash).hexdigest()
        self.iterPlugins('sendIdentify',self.model,[md5_hash])

    def sendStr(self,channel, string):
        if string.startswith("/"):
            self.sendSlashCommand(channel,string)
        elif channel.startswith("#"):
            self.iterPlugins('sendPrivMsg',self.model,[channel[1:],string])
        else:
            self.iterPlugins('sendMsg',self.model,[channel,string])

    def sendSlashCommand(self,channel,string):
        if string.lower().startswith("/m ") or string.lower() is "/m":
            self.iterPlugins('addRoom',self.view,["$mail","MailRoom"])
            self.refreshMaillist()
            self.iterPlugins('changeTab',self.view,["$mail"])
        elif string.lower().startswith("/load"):
            string = string[6:].split(' ')
            self.loadPlugin(string.pop(0),string)
        elif string.lower().startswith("/unload"):
            string = string[8:].split(' ')
            self.unloadPlugin(string.pop(0),string)
        elif string.lower().startswith("/quit"):
            self.iterPlugins('quit',self.view)
        elif string.lower().startswith("/showtopic"):
            if not channel.startswith("#"):
                self.iterPlugins('showTopic',self.view,[channel])
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
                self.model('sendPrivMsg',self.model,[user,string])
        elif not channel.startswith("#"):
            liste=string.split(" ")
            self.iterPlugins('sendSlashCommand',self.model,[liste[0],channel," ".join(liste[1:])])

    def sendJoin(self,room):
        self.iterPlugins('sendJoin',self.model,[room])

    def sendMail(self,nick,msg):
        self.sendMailCount+=1
        id="Mail_"+str(self.sendMailCount)
        self.lookupSendId.update({id:nick})
        self.iterPlugins('sendMail',self.model,[nick,msg,id])

    def refreshMaillist(self):
        self.iterPlugins('getMailCount',self.model)
        self.iterPlugins('getMaillist')

    def getMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.iterPlugins('MailInfo',self.view,["Mail Nr."+str(index)+" existiert nicht"])
        else:
            self.iterPlugins('getMail',self.model,[str(id)])

    def deleteMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.iterPlugins('MailInfo',self.view,["Mail Nr."+str(index)+" existiert nicht"])
        else:
            self.iterPlugins('deleteMail',self.model,[str(id)])

    def deleteAllMails(self):
        self.iterPlugins('deleteAllMails',self.model)

    def quitConnection(self):
        self.iterPlugins('quitConnection',self.model)

    """the following methods are required by kekzprotocol"""
    def gotConnection(self):
        self.iterPlugins('fubar',self.view)

    def startedConnection(self):
        """indicates that the model is connecting. Here should be a call to the view later on"""
        pass

    def lostConnection(self, reason):
        self.iterPlugins('connectionLost',self.view,[reason])

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        self.iterPlugins('connectionFailed',self.view)

    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.iterPlugins('sendDebugInfo',self.model,[self.view.name, self.view.version, self.view.revision, sys.platform, "Python "+pythonversion[0]])
        self.iterPlugins('getRooms',self.model)

    def receivedRooms(self,rooms):
        array=[]
        for a in ["autologin","nick","passwd","room"]:
            try:
                array.append(self.configfile[a])
            except:
                array.append("")
        if array[0]=="True" or array[0]=="1":
            self.iterPlugins('sendLogin',self.model,[array[1],array[2],array[3]])
        else:
            self.iterPlugins('receivedPreLoginData',self.view,[rooms,array[1:]])
            # now the array is: [nick,passwd,room]
            # the view has to give back an array or has to send model.sendLogin by itself


    def successLogin(self,nick,status,room):
        self.nickname=nick
        if self.configfile.has_key("regex"):
            self.nickpattern = re.compile(self.configfile["regex"], re.IGNORECASE)
        else:
            self.nickpattern = re.compile(self.nickname,re.IGNORECASE)
        self.lookupSendId={}
        self.sendMailCount=0
        self.Userlist={room:[]}
        self.iterPlugins('successLogin',self.view,[nick,status,room])

    def successMailLogin(self):
        self.sendMailCount=0
        self.lookupSendId={}
        self.lookupMailId=[]
        self.getMaillist()

    def successRegister(self):
        self.iterPlugins('successRegister')

    def successNewPassword(self):
        self.iterPlugins('successNewPassword',self.view)

    def receivedProfile(self,name,ort,homepage,hobbies,signature):
        self.iterPlugins('addRoom',self.view,["$edit","EditRoom"])
        self.iterPlugins('receivedProfile',self.view,[name,ort,homepage,hobbies,signature])

    def successNewProfile(self):
        self.iterPlugins('successNewProfile',self.view)

    def securityCheck(self, infotext):
        self.iterPlugins('securityCheck',self.view,[infotext])

    def receivedPing(self,deltaPing):
        self.iterPlugins('receivedPing',self.view,[deltaPing])

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
        activeTab=self.iterPlugins('getActiveTab',self.view)
        msg=[]
        msg.append(self.iterPlugins('timestamp',self.view,[time.strftime(self.timestamp,time.localtime(time.time()))]))
        if state==0 or state==2 or state==4:
            if nick.lower()==self.nickname.lower():
                msg.append(("green",nick+": "))
            else:    
                msg.append(("blue",nick+": "))
        elif state==3:
            msg.append(("green",str(self.nickname)+": "))
        if state==2 or state==3:
            room="#"+nick
            self.iterPlugins('addRoom',self.view,[room,"PrivRoom"])
        if state==4:
            if len(self.view.lookupRooms)==1:
                self.iterPlugins('addRoom',self.view,["$info","InfoRoom"])
                self.view.changeTab="$info"
                activeTab="$info"
            room=activeTab
        if not (activeTab == "$login" or room.lower() == self.view.ShownRoom):
            importance=2
            if (self.nickpattern.search(message) is not None) or state==2:
                importance=3 
            elif state==5:
                importance=1
            else:
                importance=2
            self.iterPlugins('highlightTab',self.view,[room,importance])
        if state==5:
            msg.append(("blue",message))
        else:
            msg.extend(self.iterPlugins('deparse',self.view,[message]))
        self.iterPlugins('printMsg',self.view,[room,msg])

    def gotHandshakeException(self, message):
        self.iterPlugins('gotException',self.view,["rattlekekz muss geupdatet werden"])

    def gotLoginException(self, message):
        self.iterPlugins('gotLoginException',self.view,[message])

    def gotException(self, message):
        self.iterPlugins('gotException',self.view,[message])

    def receivedUserlist(self,room,users):
        self.Userlist[room]=users
        self.iterPlugins('listUser',self.view,[room,users])

    def joinUser(self,room,nick,state,joinmsg):
        self.Userlist[room].append([nick,False,state])
        self.Userlist[room].sort(key=lambda x: x[0].lower())
        for i in self.Userlist[room]:
            if i[0].startswith("~"):
                index=self.Userlist[room].index(i)
                self.Userlist[room].insert(0,i)
                del self.Userlist[room][index+1] 
        self.iterPlugins('listUser',self.view,[room,self.Userlist[room]])
        self.printMsg("","(>>>) "+nick+" betritt den Raum ("+self.joinInfo[int(joinmsg)]+")",room,5)

    def quitUser(self,room,nick,partmsg):
        for i in self.Userlist[room]:
            if i[0]==nick:
                self.Userlist[room].remove(i)
        self.iterPlugins('listUser',self.view,[room,self.Userlist[room]])
        self.printMsg("","(<<<) "+nick+" hat den Raum verlassen ("+self.partInfo[int(partmsg)]+")",room,5)

    def changedUserdata(self,room,nick,away,state):
        for i in self.Userlist[room]:
            if i[0].lower()==nick.lower():
                i[1],i[2]=away,state
        self.iterPlugins('listUser',self.view,[room,self.Userlist[room]])

    def meJoin(self,room,background):
        self.Userlist.update({room:[]})
        self.iterPlugins('meJoin',self.view,[room,background])

    def mePart(self,room):
        del self.Userlist[room]
        self.iterPlugins('mePart',self.view,[room])

    def meGo(self,oldroom,newroom):
        del self.Userlist[oldroom]
        self.Userlist.update({newroom:[]})
        self.iterPlugins('meGo',self.view,[oldroom,newroom])

    def newTopic(self,room,topic):
        self.iterPlugins('newTopic',self.view,[room,topic])

    def loggedOut(self):
        self.iterPlugins('loggedOut',self.view)

    def receivedInformation(self,info):
        self.iterPlugins('receivedInformation',self.view,[info])

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
            if key == "regdata": key=u"Registriert seit "
            elif key == "logindate": key=u"Eingeloggt seit "
            elif key == "lastseen": key=u"Ausgeloggt seit "
            if key == "state":
                key = u"<raw>"
                if value == u"off": value=u"Der User ist derzeit °fb°°cr°Offline°fx°.°nn°"
                elif value == u"on": value=u"Der User ist derzeit °fb°°cg°Online°fx°.°nn°"
                elif value == u"mail": value=u"Der User ist derzeit °fb°°cr°Offline°fx°, empfängt aber °fb°°cb°Mails°fx°.°nn°"
                else:
                    value=u"Der Status ist unbekannt.°nn°"
            if key == "kekz":
                key=u"<raw>"
                value=u"°cb° %s kann noch °fb°%sx°fb° kekzen." % (nick,value)
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
        self.iterPlugins('receivedWhois',self.view,[self.stringHandler(nick), Output])

    def receivedCPMsg(self,user,cpmsg):
        self.printMsg(user+' [CTCP]',cpmsg,self.view.ShownRoom,0)
        if cpmsg.lower() == 'version':
            self.sendCPAnswer(user,cpmsg+' '+self.view.name+' ('+self.view.version+')')
        elif cpmsg.lower() == 'ping':
            self.sendCPAnswer(user,cpmsg+' ping')
        elif cpmsg.lower() in ('rev','revision'):
            self.sendCPAnswer(user,cpmsg+' '+self.revision)
        else:
            self.sendCPAnswer(user,cpmsg+' (unknown)')

    def sendCPAnswer(self,user,cpmsg):
        self.iterPlugins('sendCPAnswer',self.model,[user,cpmsg])

    def sendCPMsg(self,user,cpmsg):
        self.iterPlugins('sendCPMsg',self.model,[user,cpmsg])

    def receivedCPAnswer(self,user,cpanswer):
        self.printMsg(user+' [CTCPAnswer]',cpanswer,self.view.ShownRoom,0)

    def sendMailsuccessful(self,id):
        self.iterPlugins('MailInfo',self.view,["Die Mail an "+self.lookupSendId[id]+" wurde erfolgreich verschickt"])
        del self.lookupSendId[id]

    def sendBullshit(self,bullshit):
        self.iterPlugins('sendHandshake',self.model,[bullshit])

    def sendMailfailed(self,id,msg):
        self.iterPlugins('MailInfo',self.view,["Die Mail an "+self.lookupSendId[id]+" konnte nicht verschickt werden: "+msg])
        del self.lookupSendId[id]

    def receivedMails(self,userid,mailcount,mails):
        self.lookupMailId=[]
        for i in range(len(mails)):
            self.lookupMailId.append(mails[i]["mid"])
            del mails[i]["mid"]
            mails[i].update({"index":i})
        self.iterPlugins('receivedMails',self.view,[userid,mailcount,mails])

    def receivedMailcount(self,unreadmails,allmails):
        self.iterPlugins('MailInfo',self.view,[str(unreadmails)+" ungelesene Mails, insgesamt "+str(allmails)+" Mails"])

    def requestMailfailed(self,error):
        self.iterPlugins('MailInfo',self.view,["Die Mail konnte nicht gefunden werden: "+error])

    def requestMailsuccessful(self,user,date,mail):
        self.iterPlugins('printMail',self.view,[user,date,mail])

    def receivedNewMail(self,nick,header):
        self.iterPlugins('minorInfo',self.view,["Sie haben eine eine Nachricht von "+nick+" bekommen: "+header])

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)
