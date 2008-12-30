#!/usr/bin/env python
# -*- coding: utf-8 -*-

revision = "$Revision$"

import controllerKeckz, time, re 

# Urwid
import urwid
from urwid import curses_display

# Twisted imports
from twisted.internet import reactor, ssl

rev=re.search("\d+",revision).group()


class TextTooLongError(Exception):
    pass

class View:
    def __init__(self, controller, args):
        self.controller=controller
        self.vargs = args # List of Arguments e.g. if Userlist got colors.
        self.name,self.version="KECKz","0.0"
        tui = curses_display.Screen()
        colors =[('normal','default','default'), # TODO: More colors
            ('admin','dark red','default'),
            ('chatop','yellow','default'),
            ('roomop','dark blue','default'),
            ('special','dark green','default'),
            ('user','white','default'),
            ('adminaway','dark red','light gray'),
            ('chatopaway','yellow','light gray'),
            ('roomopaway','dark blue','light gray'),
            ('specialaway','dark green','light gray'),
            ('useraway','white','light gray'),
            ('divider', 'white', 'dark blue', 'standout'),
            ("myMsg","light green","default"),
            ("userMsg","light blue","default"),
            ("timestamp","dark green","default")]
        tui.register_palette(colors)
        reactor.addReader(self)
        reactor.callWhenRunning(self.init)
        self.tui = tui
        self.lookupRooms={}


    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return "".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))


    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def logPrefix(self): return 'CursesClient'

    def init(self):
        self.size = self.tui.get_cols_rows()

    def startConnection(self,server,port):
        reactor.connectSSL(server, port, self.controller.model, ssl.ClientContextFactory())
        self.tui.run_wrapper(reactor.run)

    def redisplay(self):
        """ method for redisplaying lines 
            based on internal list of lines """

        canvas = self.lookupRooms[self.ShownRoom].render(self.size, focus = True)
        self.tui.draw_screen(self.size, canvas)

    def doRead(self):
        """ Input is ready! """
        keys = self.tui.get_input()

        for key in keys:
            if key == 'window resize':
                self.size = self.tui.get_cols_rows()
            elif key == "ctrl n" or key=="ctrl p":
                array=self.lookupRooms.keys()
                index=array.index(self.ShownRoom)
                if array[index]==array[-1] and key=="ctrl n":
                    index=0
                elif key=="ctrl n":
                    index=index+1
                elif array[index]==array[0]:
                    index=-1
                else:
                    index=index-1
                self.ShownRoom=array[index]
                self.lookupRooms[self.ShownRoom]
            else:
                self.lookupRooms[self.ShownRoom].onKeyPressed(self.size, key)
        self.redisplay()

    def successLogin(self,nick,status,room):
        self.Ping="Ping: 0ms"
        self.nickname=nick
        self.ShownRoom=room
        self.lookupRooms.update({room:KeckzMsgTab(room,self)})
        self.lookupRooms[self.ShownRoom].addLine("Logged successful in as "+nick+"\nJoined room "+room)

    def receivedPing(self,deltaPing):
        self.Ping="Ping: "+str(deltaPing)+"ms"
        for i in self.lookupRooms:
            self.lookupRooms[i].setPing(self.Ping)
        self.redisplay()

    def printMsg(self,nick,msg,room,state):
        if state==0 or state==2 or state==4:
            if nick==self.nickname:
                msg=[("myMsg",nick+": "),msg]
            else:    
                msg=[("userMsg",nick+": "),msg]
        elif state==3:
            msg=[("myMsg",self.nickname+": "),msg]
            
        if state==2 or state==3:
            room="#"+nick
            if self.lookupRooms.has_key(room)==False:
                self.lookupRooms.update({room:KeckzPrivTab(room, self)})
                self.lookupRooms[room].setPing(self.Ping)
        if state==4:
            room=self.ShownRoom
        if not type(msg) == """<type 'list'>""":
            msg=[msg]
        msg.insert(0,("timestamp",time.strftime("[%H:%M] ",time.localtime(time.time()))))
        self.lookupRooms[room].addLine(msg)
        
        
        """text,format=controllerKeckz.decode(msg)        #TODO this is just how it work in wxView
        for i in range(len(text)):
            form=format[i].split(",")
            styleTupel=wx.TextAttr()
            wxFont=wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
            if "bold" in form:
                wxFont.SetWeight(wx.BOLD)
            if "italic" in form:
                wxFont.SetStyle(wx.ITALIC)
            for a in ["red", "blue", "green", "gray", "cyan", "magenta", "orange", "pink", "yellow"]:
                if a in form:
                    styleTupel.SetTextColour(a.upper())
                else:
                    styleTupel.SetTextColour("BLACK")
            if "imageurl" in form:
                pass
            styleTupel.SetFont(wxFont)
            self.lookupRooms[room].addLine(text[i])
            #room.printMsg(text[i],styleTupel)"""

    def gotException(self, message):
        self.lookupRooms[self.ShownRoom].addLine("Fehler: "+message)

    def listUser(self,room,users):
        self.lookupRooms[room].listUser(users,self.vargs['usercolors'])

    def meJoin(self,room,background):
        self.lookupRooms.update({room:KeckzMsgTab(room, self)})
        self.lookupRooms[room].setPing(self.Ping)
        if not background:
            self.ShownRoom=room
            self.redisplay()

    def mePart(self,room):
        if room==self.ShownRoom:
            array=self.lookupRooms.keys()
            index=array.index(self.ShownRoom)
            if array[index]==array[0]:
                index=-1
            else:
                index=index-1
            self.ShownRoom=array[index]
        del self.lookupRooms[room]
        self.redisplay()

    def meGo(self,oldroom,newroom):
        self.lookupRooms.update({newroom:KeckzMsgTab(newroom, self)})
        self.lookupRooms[newroom].setPing(self.Ping)
        self.ShownRoom=newroom
        del self.lookupRooms[oldroom]
        self.redisplay()

    def newTopic(self,room,topic):
        self.lookupRooms[room].addLine("Neues Topic: "+topic)

    def loggedOut(self):
        pass

    def receivedInformation(self,info):
        if not self.lookupRooms.has_key("$infos"):
            self.lookupRooms.update({"$infos":KeckzInfoTab("$infos", self)})
            self.lookupRooms[self.ShownRoom].setPing(self.Ping)
        self.ShownRoom="$infos"
        self.lookupRooms[self.ShownRoom].addLine(info)

    def receivedWhois(self,nick,array):
        pass

    def MailInfo(self,info):
        pass

    def receivedMails(self,userid,mailcount,mails):
        pass

    def printMail(self,user,date,mail):
        pass

    def quit(self):
        self.controller.quitConnection()  #TODO: afterwarts either the login screen must be shown or the application exit

    def closeActiveWindow(self,window):
        array=self.lookupRooms.keys()
        if len(array)==1:
            self.quit()
        else:
            index=array.index(window)
            if array[index]==array[0]:
                index=-1
            else:
                index=index-1
            del self.lookupRooms[window]
            self.ShownRoom=array[index]
            self.redisplay()

    def connectionLost(self, failure):
        pass

class KeckzBaseTab(urwid.Frame):
    def __init__(self, room, parent):
        self.hasOutput=True
        self.hasInput=False
        self.room=room
        self.parent=parent
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.upperDivider=urwid.Text(("divider","Ping: 0ms"), "right")
        self.header=urwid.Text("KECKz","center")
        
        self.buildOutputWidgets()
        self.connectWidgets()

    def buildOutputWidgets(self):
        """This should be overwritten by derived classes"""

    def connectWidgets(self):
        """This should be overwritten by derived classes"""

    def setPing(self,string):
        self.upperDivider.set_text(string)

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        if key in ('up', 'down', 'page up', 'page down'):
            self.MainView.keypress(size, key)

    def OnClose(self):
        self.parent.closeActiveWindow(self.room)

class KeckzBaseIOTab(KeckzBaseTab):
    def __init__(self,room, parent):
        self.Input = urwid.Edit()
        KeckzBaseTab.__init__(self,room, parent)
        self.hasOutput=True
        self.hasInput=True
 
    def onKeyPressed(self, size, key):
        KeckzBaseTab.onKeyPressed(self, size, key)
        if key == 'enter': 
            text = self.Input.get_edit_text()
            if text=="":
                pass
            elif text=="/quit":
                self.parent.quit()
            elif text=="/close":
                self.OnClose()
            else:
                self.sendStr(str(text))
            self.Input.set_edit_text('')

    def sendStr(self,string):
        pass

class KeckzLoginTab(KeckzBaseTab): # TODO: Make this fuck working
    def __init__(self,rooms,logindata,parent):
        self.hasOutput=False
        self.hasInput=True
        self.room='login'
        self.parent=parent
        self.Output = []
        self.MainView = urwid.ListBox(self.Output)
        self.upperDivider=urwid.Text(("divider","Ping: 0ms"), "right")
        self.header=urwid.Text("KECKz","center")
        
        self.buildOutputWidgets()
        self.connectWidgets()

    def buildOutputWidgets(self):
        """This should be overwritten by derived classes"""

    def connectWidgets(self):
        """This should be overwritten by derived classes"""

    def setPing(self,string):
        self.upperDivider.set_text(string)

    def addLine(self, text):
        """ add a line to the internal list of lines"""
        self.Output.append(urwid.Text(text))
        self.MainView.set_focus(len(self.Output) - 1)
        self.parent.redisplay()

    def onKeyPressed(self, size, key):
        if key in ('up', 'down', 'page up', 'page down'):
            self.MainView.keypress(size, key)

    def OnClose(self):
        self.parent.closeActiveWindow(self.room)

class KeckzPrivTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider'  ))])
        self.header.set_text("KECKz (Alpha: "+rev+") - Private Unterhaltung "+self.room)
        self.completion=[self.room[1:]]

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def onKeyPressed(self, size, key):
        KeckzBaseIOTab.onKeyPressed(self, size, key)
        if key == 'tab': # TODO: work something out for inline nick-completion and review ghost-lines-bug
            input = self.Input.get_edit_text().split()
            if len(input) is not 0:
                nick = input.pop().lower()
                solutions=[]
                for i in self.completion:
                    if nick in i[:len(nick)].lower():
                        solutions.append(i)
                if len(solutions) is not (0 or 1):
                    self.addLine(" ".join(solutions))
                elif len(solutions) is not 0:
                    input.append(solutions[0])
                    if len(input) is not 1:
                        self.Input.set_edit_text(" ".join(input)+" ")
                    else:
                        self.Input.set_edit_text(" ".join(input)+", ")
                    self.Input.set_edit_pos(len(self.Input.get_edit_text()))
        else:
            self.keypress(size, key)

    def sendStr(self,string):
        self.parent.controller.sendPrivMsg(str(self.room[1:]),str(string))

class KeckzMsgTab(KeckzPrivTab):
    def buildOutputWidgets(self):
        self.Userlistarray=[urwid.Text('Userliste: ')]
        self.Userlist = urwid.ListBox(self.Userlistarray)
        self.hsizer=urwid.Columns([self.MainView, ("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' )),("fixed",18,self.Userlist)], 1, 0, 16)
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.hsizer,("fixed",1,urwid.AttrWrap( urwid.SolidFill(" "), 'divider' ))])
        self.header.set_text("KECKz (Alpha: "+rev+") - Raum: "+self.room)

    def listUser(self,users,color=True):
        self.completion=[]
        for i in range(0,len(self.Userlistarray)):
            del(self.Userlistarray[0])
        self.Userlistarray.append(urwid.Text('Userliste: '))
        if color is True:
            for i in users:
                self.completion.append(i[0])
                if i[2] in 'x':
                    self.color='user'
                elif i[2] in 's':
                    self.color='special'
                elif i[2] in 'c':
                    self.color='roomop'
                elif i[2] in 'o':
                    self.color='chatop'
                elif i[2] in 'a':
                    self.color='admin'
                if i[1] == True:
                    self.color=self.color+'away'
                self.Userlistarray.append(painter(i[0],self.color))
        else:
            self.away=''
            for i in users:
                self.completion.append(i[0])
                if i[2] in 'x':
                    self.color=' '
                elif i[2] in 's':
                    self.color='~'
                elif i[2] in 'c':
                    self.color='$'
                elif i[2] in 'o':
                    self.color='@'
                elif i[2] in 'a':
                    self.color='%'
                if i[1] == True:
                    self.away=' A'
                self.Userlistarray.append(urwid.Text(self.color+i[0]+self.A))
        self.Userlist.set_focus(len(self.Userlistarray) - 1)
        self.parent.redisplay()

    def sendStr(self,string):
        self.parent.controller.sendMsg(str(self.room),str(string))

    def OnClose(self):
        self.sendStr("/part")

class KeckzMailTab(KeckzBaseIOTab):
    def buildOutputWidgets(self):
        self.header.set_text("KECKz - KekzMail")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.MainView)
        self.set_footer(self.Input)
        self.set_focus('footer')

    def sendStr(self,string):
        stringlist=sting.split(" ")
        if stringlist[0]==("/refresh"):
            self.parent.controller.refreshMaillist()
        elif stringlist[0]==("/show"):
            self.parent.controller.getMail(stringlist[1])
        elif stringlist[0]==("/del"):
            if stringlist[1]=="all":
                self.parent.controller.deleteAllMails()
            else:
                self.parent.controller.deleteMail(stringlist[1])
            self.parent.controller.refreshMaillist()
        elif stringlist[0]==("/sendm"):
            if not len(stringlist)<3:
                user=stringlist[1]
                msg=" ".join(stringlist[2:])
                self.sendMail(user,msg)
        elif stringlist[0]==("/help"):
            self.addLine("""Hilfe: \nMails neu abrufen: /refresh \n
                         Mail anzeigen: /show index \n
                         Mail löschen: /del index \n
                         Alle gelesenen Mails löschen: /del all \n
                         Mail versenden: /sendm nick msg""")
        else:
            self.addLine("Sie haben keinen gültigen Befehl eingegeben")

class KeckzInfoTab(KeckzBaseTab):
    def buildOutputWidgets(self):
        self.vsizer=urwid.Pile( [("flow",urwid.AttrWrap( self.upperDivider, 'divider' )), self.MainView])
        self.header.set_text("KECKz (Alpha: "+rev+") - Nachrichtenanzeige")

    def connectWidgets(self):
        self.set_header(self.header)
        self.set_body(self.vsizer)
        self.set_footer(None)
        self.set_focus('body')

class painter(urwid.WidgetWrap): # TODO remove unneeded attributes
      def __init__(self, text, color):
          w = urwid.Text(text)
          w = urwid.AttrWrap(w, color, color)
          urwid.WidgetWrap.__init__(self, w)
      def selectable(self):
          return True

if __name__ == '__main__':
    kekzControl=controllerKeckz.Kekzcontroller(View)
    kekzControl.view.startConnection("kekz.net",23002)
