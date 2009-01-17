#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Urwid
from urwid import curses_display

class TabManager:
    def __init__(self):
        self.lookupRooms=[[None,None,0]]
        self.sortTabs=False
        self.ShownRoom = None
        self.name,self.version="",""
        self.tui = curses_display.Screen()
        self.tui.set_input_timeouts(0.1)

    def redisplay(self):
        """ method for redisplaying lines 
            based on internal list of lines """

        canvas = self.getTab(self.ShownRoom).render(self.size, focus = True)
        self.tui.draw_screen(self.size, canvas)

    def changeTab(self,tabname):
        number = int(self.getTabId(tabname))
        self.lookupRooms[number][-1]=0
        self.ShownRoom=tabname
        self.updateTabs()
        sys.stdout.write('\033]0;'+self.name+' - '+self.ShownRoom+' \007') # Set Terminal-Title
        self.redisplay()

    def getTab(self,argument):
        for i in self.lookupRooms:
            if i[0]==argument: Tab=i[1]
        return Tab
    
    def getTabId(self, name):
        for i in range(len(self.lookupRooms)):
            if self.lookupRooms[i][0]==name: integer=i
        return integer

    def updateTabs(self):
        statelist=[]
        for i in range(len(self.lookupRooms)):
            statelist.append(self.lookupRooms[i][2])
        self.getTab(self.ShownRoom).updateTabstates(statelist)
        self.redisplay()

    def addTab(self, tabname, tab):
        try:
            self.getTab(tabname)
        except:
            self.lookupRooms.append([tabname, tab(tabname, self),0])
            if self.sortTabs:
                self.lookupRooms.sort()
                self.updateTabs()

    def delTab(self,room):
        if room==self.ShownRoom:
            index=self.getTabId(self.ShownRoom)
            if index==0 or index==1:
                index=2
            else:
                index=index-1
            self.changeTab(self.lookupRooms[index][0])
        del self.lookupRooms[self.getTabId(room)]
        self.updateTabs()

    def highlightTab(self,tab,highlight):
        try:
            if highlight>self.lookupRooms[tab][2]:
                self.lookupRooms[tab][2]=highlight
            self.updateTabs()
        except:
            if highlight>self.lookupRooms[self.getTabId(tab)][2]:
                self.lookupRooms[self.getTabId(tab)][2]=highlight
            self.updateTabs()

