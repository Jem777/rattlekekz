#!/usr/bin/python

# twisted imports
import KekzProtocol
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
# system imports
import time, sys
from OpenSSL import SSL

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file
    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write("%s %s\n" % (timestamp, message))
        self.file.flush()
    def close(self):
        self.file.close()

class LogBot(KekzProtocol.KekzClient):
    """A logging IRC bot."""
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

    # callbacks for events
    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)
    def msgReceived(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split("!", 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        # Check to see if they're sending me a private message
    def kekzCode901(self,data):
        self.logger.log(data)
    def dataReceived(self):
        self.logger.log("shit!")

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.
    A new protocol instance will be created each time we connect to the server.
    """
    # the class of the protocol to build when new connection is made
    protocol = LogBot
    def __init__(self, filename):
        #self.channel = channel
        self.filename = filename
    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason
    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

if __name__ == "__main__":
    # initialize logging
    log.startLogging(sys.stdout)
    # create factory protocol and application
    f = LogBotFactory("test.log")
    # connect factory to this host and port
    # reactor.listenSSL(23002, f, ssl.ClientContextFactory(), backlog=50)
    reactor.connectSSL("85.165.71.220", 23002, f, ssl.ClientContextFactory())
    # run bot
    reactor.run()
