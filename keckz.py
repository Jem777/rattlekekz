#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt

letters = 'H:v:?hlnt:'
keywords = ['host=','view=','help','localhost','nousercolors','timestamp=']
opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)


class main():
    def __init__(self):
        self.host = 'kekz.net'
        self.view = 'cliView'
        self.vargs = {'usercolors':True, 'timestamp':0}
        for o,p in opts:
            if o in ['-H','--host']:
                self.host = p
            elif o in ['-v','--view']:
                self.view = p
            elif o in ['-l','--localhost']:
                self.host = '127.0.0.1'
            elif o in ['-n','--nousercolors']:
                if self.view in 'cliView':
                    self.vargs['usercolors'] = False
            elif o in ['-t','--timestamp']:
                if self.view in 'cliView':
                    self.vargs['timestamp'] = int(p) # TODO: implement this into wxView
            elif o in ['-?','-h','--help']:
                print 'Usage: keckz [-h, -?, --help][-H, --host <host>][-v, --view <view>][-n, --nocolors][-t, --timestamp <integer>]'
                print '-?, -h, --help: Display this help'
                print '-H, --host: Host to connect, Default: kekz.net'
                print '-l, --localhost: Connects to localhost (127.0.0.1)'
                print '-v, --view: View to use, Default: cliView'
                print '-n, --nousercolors: This Option disables colors of the Userlist in cliView'
                print '-t, --timestamp: Determines the timestampformat to be used:'
                print '1 ... [HH:MM] (default, if not overridden by kekznet.conf)'
                print '2 ... [HH:MM:SS]'
                print '3 ... [HHMM]'
                sys.exit()

    def startKeckz(self, host, view="cliView", *args, **kwds):
        try:
            exec("from "+view+" import *")
        except:
            print "No View found"
            sys.exit()
        if str(type(View))=="""<type 'classobj'>""": #TODO: We'll have to have a check whether foo.View exists
            import controllerKeckz
            kekzControl=controllerKeckz.Kekzcontroller(View, *args, **kwds)
            kekzControl.view.startConnection(host,23002)
        else:
            print 'Error: Nullpointer Exception'
            sys.exit()

f = main()
f.startKeckz(f.host, f.view, usercolors=f.vargs['usercolors'], timestamp=f.vargs['timestamp'])