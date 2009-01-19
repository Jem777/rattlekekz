#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kekzprotocol, os, sys, re, time
from hashlib import sha1, md5

def formatopts(formlist, opt):
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

def decode(string,nick):
    array=string.split("°")
    textlist=[""]
    formatlist=["normal"]
    output={}
    for i in range(len(array)):
        nicks = []
        newtextlist,newformatlist = [""],["normal"]
        if i%2==0:
            pattern = re.compile(nick.lower().strip(),re.IGNORECASE)
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
            formatlist=formatopts(formatlist,array[i])
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

class Kekzcontroller():
    def __init__(self, interface, *args, **kwds):
        self.kwds=kwds
        self.model = kekzprotocol.KekzClient(self)
        self.view = interface(self, *args, **kwds)
        self.readConfigfile()
        
        self.joinInfo=["Join","Login","Einladung"]
        self.partInfo=["Part","Logout","Lost Connection","Nick-Kollision","Ping Timeout","Kick"]

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

    """following methods transport data from the View to the model"""
    def sendLogin(self, nick, passwd, rooms):
        self.model.sendLogin(nick, sha1(passwd).hexdigest(), rooms)

    def registerNick(self,nick,passwd,email):
        self.model.registerNick(nick,sha1(passwd).hexdigest(),email)

    def changePassword(self,passwd,passwdnew):
        self.model.changePassword(sha1(passwd).hexdigest(),sha1(passwdnew).hexdigest())
        
    def updateProfile(self,name,ort,homepage,hobbies,signature,passwd):
        self.model.updateProfile(name,ort,homepage,hobbies,signature,sha1(passwd).hexdigest())

    def sendIdentify(self,passwd):
        sha1_hash=sha1(passwd).hexdigest()
        md5_hash= md5.new(sha1_hash).hexdigest()
        self.model.sendIdentify(md5_hash)

    def sendMsg(self, channel, msg):
        if channel.startswith("#"):
            self.model.sendPrivMsg(channel[1:],msg)
        elif msg.startswith("/"):
            liste=msg.split(" ")
            self.model.sendSlashCommand(liste[0],channel," ".join(liste[1:]))
        else:     
            self.model.sendMsg(channel,msg)

    def sendPrivMsg(self,nick,msg):
        self.model.sendPrivMsg(nick,msg)

    def sendJoin(self,room):
        self.model.sendJoin(room)

    def sendMail(self,nick,msg):
        self.sendMailCount=self.sendMailCount+1
        id="Mail_"+str(self.sendMailCount)
        self.lookupSendId.update({id:nick})
        self.model.sendMail(nick,msg,id)

    def refreshMaillist(self):
        self.model.getMailCount()
        self.model.getMaillist()

    def getMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("Mail Nr."+str(index)+" existiert nicht")
        else:
            self.model.getMail(str(id))

    def deleteMail(self,index):
        try:
            id=self.lookupMailId[int(index)]
        except:
            self.view.MailInfo("Mail Nr."+str(index)+" existiert nicht")
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
        pass

    def lostConnection(self, reason):
        self.view.connectionLost(reason)

    def failConnection(self, reason):
        """the try to connect failed. Here should be a call to the view later on"""
        pass

    def receivedHandshake(self):
        pythonversion=sys.version.split(" ")
        self.model.sendDebugInfo(self.view.name, self.view.version, self.view.revision, sys.platform, "Python "+pythonversion[0])
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
        self.nickname=nick
        self.nickpattern = re.compile(self.nickname.lower(),re.IGNORECASE)
        self.lookupSendId={}
        self.sendMailCount=0
        self.Userlist={room:[]}
        self.view.successLogin(nick,status,room)

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

    def printMsg(self,nick,message,room,state): # TODO: Change Terminal-Titel on received Message and back then they were read
        #msg=[("timestamp",time.strftime(self.timestamp,time.localtime(reactor.seconds())))]
        msg=[]
        msg.append(self.view.timestamp(time.strftime(self.timestamp,time.localtime(time.time()))))
        if state==0 or state==2 or state==4:
            if nick.lower()==self.nickname.lower():
                msg.append(("green",nick+": "))
            else:    
                msg.append(("blue",nick+": "))
        elif state==3:
            msg.append(("green",str(self.nickname)+": "))
        if state==2 or state==3:
            room="#"+nick
            self.view.addRoom(room,"PrivRoom")
        if state==4:
            room=self.view.ShownRoom
        if not (self.view.ShownRoom == "$login" or room == self.view.ShownRoom):
            importance=2
            if (self.nickpattern.search(message) is not None) or state==2:
                importance=3 
            elif state==5:
                importance=1
            else:
                importance=2
            self.view.highlightTab(room,importance)
        msg.extend(self.view.deparse(message))
        self.view.printMsg(room,msg)

    def gotHandshakeException(self, message):
        self.view.gotException("KECKz muss geupdatet werden")

    def gotLoginException(self, message):
        self.view.gotLoginException(message)

    def gotException(self, message):
        self.view.gotException(message)

    def receivedUserlist(self,room,users):
        self.Userlist[room]=users
        self.view.listUser(room,users)

    def joinUser(self,room,nick,state,joinmsg):
        self.Userlist[room].append([nick,False,state])
        self.Userlist[room].sort(key=lambda x: x[0].lower())
        for i in self.Userlist[room]:
            if i[0].startswith("~"):
                index=self.Userlist[room].index(i)
                self.Userlist[room].insert(0,i)
                del self.Userlist[room][index+1] 
        self.view.listUser(room,self.Userlist[room])
        self.printMsg("",nick+" betritt den Raum ("+self.joinInfo[int(joinmsg)]+")",room,5)

    def quitUser(self,room,nick,partmsg):
        for i in self.Userlist[room]:
            if i[0]==nick:
                self.Userlist[room].remove(i)
        self.view.listUser(room,self.Userlist[room])
        self.printMsg("",nick+" hat den Raum verlassen ("+self.partInfo[int(partmsg)]+")",room,5)

    def changedUserdata(self,room,nick,away,state):
        for i in self.Userlist[room]:
            if i[0]==nick:
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

    def receivedWhois(self,data):
        Output=[]
        for i in range(0,len(data),2):
            key,value = data[i],data[i+1]
            if key=="nick":
                nick=value
            if key == "regdata": key="Registriert seit "
            elif key == "logindate": key="Eingeloggt seit "
            elif key == "lastseen": key="Ausgeloggt seit "
            if key == "state":
                key = "<raw>"
                if value == "off": value="Der User ist derzeit %fb%%cr%Offline%fx%.%nn%"
                elif value == "on": value="Der User ist derzeit %fb%%cg%Online%fx%.%nn%"
                elif value == "mail": value="Der User ist derzeit %fb%%cr%Offline%fx%, empfängt aber %fb%%cb%Mails%fx%.%nn%"
                else:
                    value="Der Status ist unbekannt.%nn%"
            if key == "kekz":
                key="<raw>"
                value="%cb%" + nick + " kann noch %fb%" + str(value) + "x%fb% kekzen."
            if key == "usertext":
                key="<raw>"
            if key == "<h1>":
                key="<raw>"
                value="%nn%%nn%%cb%%fb%"+value.capitalize()+"%fb%%cb%"
            if not key == "<raw>":
                value="%fb%"+key.capitalize()+":%fb% "+value
            Output.append(value.encode("utf_8"))
        self.view.receivedWhois(nick, Output)

    def receivedCPMsg(self,user,cpmsg):
        self.view.receivedCPMsg(user,cpmsg)

    def sendCPAnswer(self,user,cpmsg):
        self.model.sendCPAnswer(user,cpmsg)

    def sendCPMsg(self,user,cpmsg):
        self.model.sendCPMsg(user,cpmsg)

    def receivedCPAnswer(self,user,cpanswer):
        self.view.receivedCPAnswer(user,cpanswer)

    def sendMailsuccessful(self,id):
        self.view.MailInfo("Die Mail an "+self.lookupSendId[id]+" wurde erfolgreich verschickt")
        del self.lookupSendId[id]

    def sendBullshit(self,bullshit):
        self.model.sendHandshake(bullshit)

    def sendMailfailed(self,id,msg):
        self.view.MailInfo("Die Mail an "+self.lookupSendId[id]+" konnte nicht verschickt werden: "+msg)
        del self.lookupSendId[id]

    def receivedMails(self,userid,mailcount,mails):
        self.lookupMailId=[]
        for i in range(len(mails)):
            self.lookupMailId.append(mails[i]["mid"])
            del mails[i]["mid"]
            mails[i].update({"index":i})
        self.view.receivedMails(userid,mailcount,mails)

    def receivedMailcount(self,unreadmails,allmails):
        self.view.MailInfo(str(unreadmails)+" ungelesene Mails, insgesamt "+str(allmails)+" Mails")

    def requestMailfailed(self,error):
        self.view.MailInfo("Die Mail konnte nicht gefunden werden: "+error)

    def requestMailsuccessful(self,user,date,mail):
        self.view.printMail(user,date,mail)

    def receivedNewMail(self,nick,header):
        self.view.minorInfo("Sie haben eine eine Nachricht von "+nick+" bekommen: "+header)
        #self.view.MailInfo("Sie haben eine eine Nachricht von "+nick+" bekommen: "+header)
        #self.refreshMaillist()

    def unknownMethod(self,name):
        pass

    def __getattr__(self, name):
        return self.unknownMethod(name)
