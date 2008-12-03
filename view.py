#!/usr/bin/env python
# -*- coding: utf-8 -*-
class View:
    def __init__(self, controller):
        self.controller = controller
        print "[VIEW] initialisizing view"
        
    def outputStuff(self, string):
        print "[VIEW] output: " + string
    