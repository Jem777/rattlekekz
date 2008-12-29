#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt

letters = 'H:v:?hl'
keywords = ['host=','view=','help','localhost']
opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)


class main():
    def __init__(self):
        self.host = 'kekz.net'
        self.view = 'cliView'
        for o,p in opts:
            if o in ['-H','--host']:
                self.host = p
            elif o in ['-v','--view']:
                self.view = p
            elif o in ['-l','--localhost']:
                self.host = '127.0.0.1'
            elif o in ['-?','-h','--help']:
                print 'Usage: keckz [-h, -?, --help][-H, --host <host>][-v, --view <view>]'
                print '-?, -h, --help: Display this help'
                print '-H, --host: Host to connect, Default: kekz.net'
                print '-l, --localhost: Connects to localhost (127.0.0.1)'
                print '-v, --view: View to use, Default: cli'
                sys.exit()

    def startKeckz(self, host, view="cli"):
        try:
            exec("from "+view+" import *")
        except:
            print "No View found"
            sys.exit()
        if str(type(View))=="""<type 'classobj'>""": #TODO: We'll have to have a check whether foo.View exists
            import controllerKeckz
            kekzControl=controllerKeckz.Kekzcontroller(View)
            kekzControl.view.startConnection(host,23002)
        else:
            print 'not implemented yet'
            sys.exit()

f = main()
f.startKeckz(f.host, f.view)