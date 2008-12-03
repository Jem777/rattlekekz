#!/usr/bin/env python
# -*- coding: utf-8 -*-
class KekzProtocol:
    def __init__(self, controller):
        self.controller = controller
        print "[MODEL] initialisizing model"
        
    def sendToServer(self, string):
        print "[MODEL] sending to server: " + string
        
