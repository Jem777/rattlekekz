#!/usr/bin/env python
# -*- coding: utf-8 -*-
import kekzprotocol, view

class Controller:
    def __init__(self):
        print "[CONTROLLER] Initialisizing..."
        print "[CONTROLLER] Spawning model&view"
        self.model = kekzprotocol.KekzProtocol(self)
        self.view = view.View(self)
        
    def gotConnection(self):
        print "[CONTROLLER] we got a connection! lets tell the view"
        self.view.outputStuff("connection made.")
        
    def doSomething(self):
        print "[CONTROLLER] Do something!"
        self.view.outputStuff("doin something!")
        self.model.sendToServer("some stuff")