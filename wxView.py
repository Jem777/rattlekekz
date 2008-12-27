#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor
import wx,controllerKeckz
import re



class KECKzLogin(wx.Frame):
    def __init__(self, controller, *args, **kwds):
        self.kekzControl=controller
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.RoomList = wx.ListBox(self, -1, choices=[], style=wx.LB_HSCROLL)
        self.Nickname = wx.TextCtrl(self, -1, "")
        self.Password = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.Rooms = wx.TextCtrl(self, -1, "")

        self.Label1 = wx.StaticText(self, -1, "Nickname:")
        self.Label2 = wx.StaticText(self, -1, "Passwort:")
        self.Label3 = wx.StaticText(self, -1, "Räume:")

        self.button_1 = wx.Button(self, -1, "Login") 
        self.button_2 = wx.Button(self, -1, "Registrieren")

        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnLogin, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnRegister, self.button_2)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.RoomList)

    def __do_layout(self):
        grid_sizer_1 = wx.GridSizer(4, 2, 0, 0)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1.Add(self.Label1, 0, 0, 0)
        grid_sizer_1.Add(self.Nickname, 0, 0, 0)
        grid_sizer_1.Add(self.Label2, 0, 0, 0)
        grid_sizer_1.Add(self.Password, 0, 0, 0)
        grid_sizer_1.Add(self.Label3, 0, 0, 0)
        grid_sizer_1.Add(self.Rooms, 0, 0, 0)
        grid_sizer_1.Add(self.button_1, 0, 0, 0)
        grid_sizer_1.Add(self.button_2, 0, 0, 0)
        sizer_2.Add(self.RoomList, 0, 0, 0)
        sizer_2.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()

    def OnLogin(self, event):
        self.Rooms.Value.strip()
        re.sub("\\w","",self.Rooms.Value)
        self.Nickname.Value.strip()
        self.kekzControl.sendLogin(self.Nickname.Value.encode("utf_8"),self.Password.Value.encode("utf_8"),self.Rooms.Value.encode("utf_8"))


    def OnRegister(self, event): 
        self.RegisterFrame=KECKzRegister(self.kekzControl, self, -1, "KECKz - Registrieren")
        self.RegisterFrame.Show()
        self.Show(False)

    def OnListBox(self, event):
        selectedRoom=self.RoomList.GetString(self.RoomList.GetSelection())
        roomname=selectedRoom.split(" ")
        self.Rooms.Value=roomname[0]


class KECKzRegister(wx.Frame):
    def __init__(self, controller, *args, **kwds):
        self.kekzControl=controller
        # Frame is child of KECKzLogin class
        # called when the user wants to register a nick
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.Lable1 = wx.StaticText(self, -1, "Nickname:")
        self.Nickname = wx.TextCtrl(self, -1, "")
        self.Label2 = wx.StaticText(self, -1, "Passwort:")
        self.Password = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.Label3 = wx.StaticText(self, -1, "Passwort wiederholen:")
        self.PasswordAgain = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.Label4 = wx.StaticText(self, -1, "E-Mail Addresse:")
        self.EMailAddress = wx.TextCtrl(self, -1, "")
        self.Confirm = wx.Button(self, -1, "Absenden")
        self.Cancel = wx.Button(self, -1, "Abbrechen")

        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnClose, self.Cancel)
        self.Bind(wx.EVT_BUTTON, self.OnConfirm, self.Confirm)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

    def __do_layout(self):
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridSizer(4, 2, 0, 0)
        grid_sizer_1.Add(self.Lable1, 0, 0, 0)
        grid_sizer_1.Add(self.Nickname, 2, wx.ALIGN_RIGHT, 0)
        grid_sizer_1.Add(self.Label2, 0, 0, 0)
        grid_sizer_1.Add(self.Password, 2, wx.ALIGN_RIGHT, 0)
        grid_sizer_1.Add(self.Label3, 0, 0, 0)
        grid_sizer_1.Add(self.PasswordAgain, 2, wx.ALIGN_RIGHT, 0)
        grid_sizer_1.Add(self.Label4, 0, 0, 0)
        grid_sizer_1.Add(self.EMailAddress, 2, wx.ALIGN_RIGHT, 0)
        sizer_6.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_6.Add(self.Confirm, 0, 0, 0)
        sizer_6.Add(self.Cancel, 0, 0, 0)
        self.SetSizer(sizer_6)
        sizer_6.Fit(self)
        self.Layout()

    def OnConfirm(self, event):
        self.Password.Value.strip()
        self.PasswordAgain.Value.strip()
        self.Nickname.Value.strip()
        self.EMailAddress.Value.strip()

        if self.Password.Value!=self.PasswordAgain.Value or len(self.Password.Value)<4:
            self.Password.Value,self.PasswordAgain.Value="",""
            dlg=wx.MessageDialog(self, message="Passwörter müssen identisch sein und mindestens 4 Zeichen haben",caption="Error",style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif len(self.Nickname.Value)==0 or len(self.EMailAddress.Value)==0  or self.Password.Value.isspace()==1 or self.Nickname.Value.isspace()==1 or self.EMailAddress.Value.isspace()==1:
            dlg=wx.MessageDialog(self, message="Alle Felder müssen ausgefüllt werden",caption="Error",style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.kekzControl.registerNick(self.Nickname.Value.encode("utf_8"),self.Password.Value.encode("utf_8"),self.EMailAddress.Value.encode("utf_8"))

    def OnClose(self, event):
        self.GetParent().Show()
        self.Destroy()




class KECKzView(wx.Frame):
    def __init__(self, controller, *args, **kwds):
        self.kekzControl=controller
        # begin wxGlade: KECKzView.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.roomnotebook = wx.Notebook(self, -1, style=0)
        self.notebook_panel_1 = wx.Panel(self.roomnotebook, -1)
        self.keckzLogo = wx.StaticBitmap(self, -1, wx.NullBitmap)


        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        self.__do_layout()

    def __do_layout(self):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.keckzLogo, 0, 0, 0)
        self.mainsizer.Add(self.roomnotebook, 1, wx.EXPAND, 0)
        self.SetSizer(self.mainsizer)
        
    def OnClose(self, event):
        self.Destroy()



class KECKzPrivTab(wx.Panel):
    def __init__(self, room, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        self.roomname=room
        self.Topic = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.showPing = wx.TextCtrl(self, -1, "Ping: 0ms", style=wx.TE_READONLY)
        self.OutputText = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.InputText = wx.TextCtrl(self, -1, "")
        self.sendButton = wx.Button(self, -1, "Send")

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.InputText)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.sendButton)
        wx.EVT_CHAR(self.InputText, self.OnKeyPressed)

        self.__do_layout()

    def __do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.Topic, 2, 0, 0)
        sizer_3.Add(self.showPing, 0, 0, 0)
        self.sizer_1.Add(sizer_3, 0, wx.ALIGN_RIGHT|wx.EXPAND, 0)
        self.update_layout()
        sizer_4.Add(self.InputText, 2, 0, 0)
        sizer_4.Add(self.sendButton, 0, 0, 0)
        self.sizer_1.Add(sizer_4, 0, wx.ALIGN_RIGHT|wx.EXPAND, 0)
        self.SetSizer(self.sizer_1)

    def update_layout(self):
        self.sizer_1.Add(self.OutputText, 2, wx.EXPAND, 0)
        self.sizer_1.Fit(self)
        self.Layout()

    def OnEnter(self, event): 
        print "Event handler `OnEnter' not implemented!"
        event.Skip()

    def OnButton(self, event): 
        self.GrandParent.kekzControl.sendMsg(self.roomname,self.InputText.Value.encode("utf_8"))
        self.InputText.Value=""
   
    def OnKeyPressed(self, event):
        if event.GetKeyCode()==13:
            self.OnButton(event)
        else:
            event.Skip()

class KECKzMsgTab(KECKzPrivTab):
    def update_layout(self):
        self.Userlist = wx.ListBox(self, -1, choices=[], style=wx.LB_HSCROLL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.OutputText, 2, wx.EXPAND, 0)
        sizer_2.Add(self.Userlist, 0, wx.EXPAND, 0)
        self.sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.sizer_1.Fit(self)
        self.Layout()



class View:
    def __init__(self,controller):
        self.name,self.version="wxKECKz","0.0"
        self.lookupRooms={}
        self.ping="" #the string, which contains the current ping
        
        # it's a global variable, because of the easier access for the frames (they don't have to call it with self)
        self.kekzControl=controller
        
        self.KECKz = wx.App(0) #starting the app
        wx.InitAllImageHandlers()
        
        self.LoginFrame = KECKzLogin(self.kekzControl, None, -1, "KECKz - Login") # starting the LoginFrame, but not displaying it
        self.KECKz.SetTopWindow(self.LoginFrame)
        reactor.registerWxApp(self.KECKz) # starting the twisted reactor

    def fubar(self):
        """This function sends bullshit to the controller for debugging purposes"""
        return "".join(map(lambda x:chr(ord(x)-42),"\x84\x8fNb\x92k\x8c\x8f\x80\x8fZ\xa3MZM\x98\x8f\x9e\x95\x8f\x95\x84^J\x8c\x8f\x9e\x8bJ\\ZZbZc[Z"))

    def receivedPreLoginData(self,rooms,array):
        for i in range(len(rooms)):
            self.LoginFrame.RoomList.Insert(rooms[i]["name"]+" ("+str(rooms[i]["users"])+")",i)
        self.LoginFrame.Nickname.Value,foo,self.LoginFrame.Rooms.Value=array
        self.LoginFrame.Fit()
        self.LoginFrame.SetMinSize(self.LoginFrame.GetSize())
        self.LoginFrame.SetMaxSize(self.LoginFrame.GetSize())
        self.LoginFrame.Show()

    def successLogin(self,nick,status,room):
        self.LoginFrame.Destroy()
        self.ViewFrame = KECKzView(self.kekzControl, None, -1, "KECKz")
        self.KECKz.SetTopWindow(self.ViewFrame)
        self.ViewFrame.Show()
        self.nickname=nick
        self.lookupRooms.update({room:KECKzMsgTab(room, self.ViewFrame.roomnotebook, -1)})
        self.ViewFrame.roomnotebook.AddPage(self.lookupRooms[room], room)
        self.ViewFrame.mainsizer.Fit(self.ViewFrame)
        self.lookupRooms[room].showPing.Value=self.ping

    def successRegister(self):
        dlg=wx.MessageDialog(None, message="Sie haben sich erfolgreich registriert",caption="Registrierung erfolgreich",style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        self.LoginFrame.RegisterFrame.OnClose(None)

    def securityCheck(self, infotext):
        dlg=wx.TextEntryDialog(None, message=infotext,caption="Authentifikation erforderlich", defaultValue="", style=wx.OK)
        dlg.ShowModal()
        self.kekzControl.sendIdentify(dlg.GetValue())
        dlg.Destroy()

    def receivedPing(self,deltaPing):
        self.ping="Ping: "+str(deltaPing)+"ms"
        for i in self.lookupRooms:
            self.lookupRooms[i].showPing.Value=self.ping

    def printMsg(self,nick,msg,room,state):
        if state==0 or state==2 or state==4:
            msg=nick+": "+msg
        elif state==3:
            msg=self.nickname+": "+msg
        if state==2 or state==3:
            room="#"+nick
            if self.lookupRooms.has_key(room)==False:
                self.lookupRooms.update({room:KECKzPrivTab(room, self.ViewFrame.roomnotebook, -1)})
                self.ViewFrame.roomnotebook.AddPage(self.lookupRooms[room], room)
        msg=msg+"\n"
        if state==4:
            priv=self.ViewFrame.roomnotebook.GetCurrentPage()
            priv.OutputText.SetValue(priv.OutputText.GetValue()+msg.decode("utf_8"))
        else:
            self.lookupRooms[room].OutputText.SetValue(self.lookupRooms[room].OutputText.GetValue()+msg.decode("utf_8"))

    def gotException(self, msg):
        dlg=wx.MessageDialog(None, message="Fehler: "+msg,caption="Error",style=wx.OK|wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def listUser(self,room,users):
        self.lookupRooms[room].Userlist.Clear()
        for i in range(len(users)):
            self.lookupRooms[room].Userlist.Insert(users[i][0],i)
        self.lookupRooms[room].sizer_1.Fit(self.lookupRooms[room])

    def meJoin(self,room,background):
        self.lookupRooms.update({room:KECKzMsgTab(room, self.ViewFrame.roomnotebook, -1)})
        self.ViewFrame.roomnotebook.AddPage(self.lookupRooms[room], room)
        self.lookupRooms[room].showPing.Value=self.ping

    def mePart(self,room):
        self.ViewFrame.roomnotebook.RemovePage(self.lookupRooms[room].GetId())
        del self.lookupRooms[room]

    def meGo(self,oldroom,newroom):
        self.ViewFrame.roomnotebook.RemovePage(self.lookupRooms[oldroom])
        del self.lookupRooms[oldroom]
        self.lookupRooms.update({newroom:KECKzMsgTab(room, self.ViewFrame.roomnotebook, -1)})
        self.ViewFrame.roomnotebook.AddPage(self.lookupRooms[newroom], newroom)
        self.lookupRooms[newroom].showPing.Value=self.ping

    def newTopic(self,room,topic):
        self.lookupRooms[room].OutputText.SetValue(self.lookupRooms[room].OutputText.GetValue()+topic.decode("utf_8")+"\n")
        self.lookupRooms[room].Topic.Value="Topic: "+topic.decode("utf_8")

    def loggedOut(self):
        self.ViewFrame.roomnotebook.DeleteAllPages()
        self.lookupRooms={}
        self.ViewFrame.Close(True)

    def receivedInformation(self,info):
        dlg=wx.MessageDialog(None, message=info,caption="KECKz - Info",style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

if __name__=="__main__":
    import controllerKeckz
    controllerKeckz.Kekzcontroller(View).startConnection("kekz.net",23002)
