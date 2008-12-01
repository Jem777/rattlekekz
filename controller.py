#!/usr/bin/env python
# -*- coding: utf-8 -*-

# twisted imports
import KekzProtocol
from twisted.internet import reactor, protocol, ssl
# system imports
import time, sys
from OpenSSL import SSL

class KekzBot(KekzProtocol.KekzClient):
    Nickname = "tester"
    Passwort='a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
    Channel="dev"
    
    def connectionMade(self):
        KekzProtocol.KekzClient.connectionMade(self)
        print 'verbinde ...'
    
    def startPing(self):
        """startet das Senden des Pings"""
        l = task.LoopingCall(KeckProtocol.KekzClient.sendPing())
        l.start(60.0)
    
    def receivedHandshake(self, passworthash):
        self.startPing()
        self.getRooms()
    
    def getRooms(self):
        KekzProtocol.KekzClient.getRooms(self)
    
    def receivedRooms(self, rooms):
        pass
    
    def receivedPing(self, ping):
        print ping
    
    def connectionLost(self, reason):
        KekzProtocol.KekzClient.connectionLost(self, reason)
        print reason
    
class KekzFactory(protocol.ClientFactory):
    
    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == "__main__":
    f = KekzFactory()
    # connect factory to this host and port
    #reactor.connectSSL("kekz.net", 23002, f, ssl.ClientContextFactory())
    reactor.connectSSL("pitix.ath.cx", 23002, f, ssl.ClientContextFactory())
    # run bot
    reactor.run()