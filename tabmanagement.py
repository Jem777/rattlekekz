#!/usr/bin/env python
# -*- coding: utf-8 -*-

copyright = """
    Copyright 2008, 2009 Moritz Doll and Christian Scharkus

    This file is part of KECKz.

    KECKz is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KECKz is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KECKz.  If not, see <http://www.gnu.org/licenses/>.
"""

import urwid
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
        self.size = self.tui.get_cols_rows()
        canvas = self.getTab(self.ShownRoom).render(self.size, focus = True)
        try:
            self.tui.draw_screen(self.size, canvas)
        except:
            pass

    def sort(self):
        if self.sortTabs:
            namelist=[]
            lookupRooms=[]
            for i in self.lookupRooms:
                namelist.append(i[0])
            namelist.sort()
            for i in namelist:
                lookupRooms.append(self.lookupRooms[self.getTabId(i)])
            self.lookupRooms=lookupRooms
            self.updateTabs()

    def changeTab(self,tabname):
        number = int(self.getTabId(tabname))
        self.lookupRooms[number][-1]=0
        self.ShownRoom=tabname
        self.updateTabs()
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
            self.sort()

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

