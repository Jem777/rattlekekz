#!/usr/bin/env python
# -*- coding: utf-8 -*-

class plugin():
    def __init__(self,controller,model,view,time='true'):
        self.controller = controller
        self.model = model
        self.view = view
        self.time = time.lower()
        self.controller.botMsg("model",self.model.hiThere('example',self)[2])
        self.controller.botMsg("view",self.view.hiThere('example',self)[2])
    
    def unload():
        self.view.outHere('example',self)
        self.model.outHere('example',self)
    
    def receivedPing(self,caller,time):
        self.controller.botMsg("example plugin","ping!")