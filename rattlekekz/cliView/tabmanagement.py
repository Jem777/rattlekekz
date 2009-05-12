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

import urwid
from urwid import raw_display

class TabManager:
    def __init__(self):
        """This the TabManager Class"""
        self.lookupRooms=[[None,None,0]]
        self.sortTabs=False
        self.ShownRoom = None
        self.name,self.version="",""
        self.tui = raw_display.Screen()
        self.tui.set_input_timeouts(0.1)

    def redisplay(self):
        """ method for redisplaying lines 
            based on internal list of lines """
        self.size = self.tui.get_cols_rows()
        canvas = self.getTab(self.ShownRoom).render(self.size, focus = True)
        self.tui.draw_screen(self.size, canvas)

    def sort(self):
        """this sorts the Tabs in alphabetical order if self.sortTabs"""
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

    def changeTab(self, tabname):
        """changes the Tab to tabname"""
        number = int(self.getTabId(tabname))
        self.lookupRooms[number][-1]=0
        self.ShownRoom=tabname
        self.updateTabs()
        self.redisplay()

    def getActiveTab(self):
        """returns the Active Tab"""
        return self.ShownRoom

    def getTab(self, tabname):
        """returns the object of a Tab"""
        Tab=None
        for i in self.lookupRooms:
            if i[0]==tabname.lower():
                Tab=i[1]
                break
        if Tab!=None:
            return Tab
        else: 
            print "No object "+tabname
    
    def getTabId(self, tabname):
        """returns the id of a tab"""
        for i in range(len(self.lookupRooms)):
            if self.lookupRooms[i][0]==tabname.lower():
                integer=i
        return integer

    def updateTabs(self):
        """updates the Tabs and sends the updated Tablist to the active Tab"""
        statelist=[]
        for i in range(len(self.lookupRooms)):
            statelist.append(self.lookupRooms[i][2])
        self.getTab(self.ShownRoom).updateTabstates(statelist)
        self.redisplay()

    def addTab(self, tabname, tab):
        """adds a new Tab with tabname and the object"""
        try:
            self.getTab(tabname.lower())
        except:
            self.lookupRooms.append([tabname.lower(), tab(tabname, self),0])
            self.sort()

    def delTab(self, tab):
        """deletes a Tab"""
        if tab.lower()==self.ShownRoom.lower():
            index=self.getTabId(self.ShownRoom)
            if index==0 or index==1:
                index=2
            else:
                index=index-1
            self.changeTab(self.lookupRooms[index][0])
        del self.lookupRooms[self.getTabId(tab)]
        self.updateTabs()

    def highlightTab(self,tab,highlight):
        """highlights a tab highlight is of type int and tab is of type int (the id) or string (the tabname)"""
        tab = tab.lower()
        try:
            if highlight>self.lookupRooms[tab][2]:
                self.lookupRooms[tab][2]=highlight
            self.updateTabs()
        except:
            if highlight>self.lookupRooms[self.getTabId(tab)][2]:
                self.lookupRooms[self.getTabId(tab)][2]=highlight
            self.updateTabs()

