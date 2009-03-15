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

import time

class plugin:
    def __init__(self,controller,model,view):
        self.name="awaylog"
        self.controller = controller
        self.model = model
        self.view = view
        self.model.hiThere(self.name,self)
        self.controller.botMsg("rattleKekz",self.view.hiThere(self.name,self)[2])
        
        self.away=False

    def unload(self):
        self.view.outHere(self.name,self)
        self.model.outHere(self.name,self)

    def sendStr(self, channel, string):
        if string.startswith("/away"):
            self.view.addRoom("#AwayLog","InfoRoom")
            self.view.changeTab("#AwayLog")
            self.away=True
        elif self.away==True:
            self.away=False

    def printMsg(self, nick,message,room,state):
        if ((self.controller.nickpattern.search(message) is not None) or state==2) and self.away:
            msg=[]
            msg.append(self.view.timestamp(time.strftime(self.controller.timestamp,time.localtime(time.time()))))
            msg.append(("blue",nick+" in "+room+": "))
            if state==5:
                msg.append(("blue",message))
            else:
                msg.extend(self.view.deparse(message))
            self.view.addRoom("#AwayLog","InfoRoom")
            self.view.printMsg("#AwayLog",msg)