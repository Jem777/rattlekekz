#!/usr/bin/env python
# -*- coding: utf-8 -*-

# twisted imports
import KekzProtocol
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
# system imports
import time, sys
from OpenSSL import SSL

class KekzBot(KekzProtocol.KekzClient):
    Nickname = "tester"
    Passwort='a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
    Channel="dev"
    
    def connectionMade(self):
        KekzProtocol.KekzClient.connectionMade(self)
        #self.sendLogin(self.Nickname, self.Passwort, self.factory.channel)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                         time.asctime(time.localtime(time.time())))
        
    def connectionLost(self, reason):
        KekzProtocol.KekzClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                         time.asctime(time.localtime(time.time())))
        self.logger.close()