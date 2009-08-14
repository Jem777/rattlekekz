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

from PyQt4 import QtGui,QtCore

class TabManager():
    def __init__(self):
        pass

    def changeTab(self, tabname):
        """changes the Tab to tabname"""
        Tab = self.getTab(tabname)
        self.tabs.setCurrentWidget(Tab)

    def getTab(self,tabname):
        """returns the object of a Tab"""
        for i in range(self.tabs.count()):
            if str(self.tabs.tabText(i)).lower()==tabname.lower():
                Tab=self.tabs.widget(i)
                break
        return Tab

    def addTab(self,tabname,tab):
        """adds a new Tab with tabname and the object"""
        try:
            self.getTab(tabname.lower())
        except:
            self.tabs.addTab(tab(),tabname)
            self.getTab(tabname)._setup(tabname, self)