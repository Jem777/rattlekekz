#!/usr/bin/env python
# -*- coding: utf-8 -*-

import controllerKeckz, sys, getopt

letters = 'h:v:?'
keywords = ['host=','view=','help']
opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)



print opts

class main():
    def __init__(self):
        self.host = 'kekz.net'
        self.view = 'cli'
        for o,p in opts:
            if o in ['-h','--host']:
                self.host = p
            #elif o in ['-v','--view']:
            #    self.view = p
            elif o in ['-?','--help']:
                print 'Usage: keckz [-?][-h <host>][-v <view>]'
                print '-?, --help: Display this help'
                print '-h, --host: Host to connect, Default: kekz.net'
                print '-v, --view: View to use, Default: cli'
                sys.exit()

    def connect(self, host, view="cli"):
        try:
            exec("from "+view+" import *")
        except:
            print "No View found"
            sys.exit()
        if str(type(View))=="""<type 'classobj'>""": #TODO: We'll have to have a check whether foo.View exists
            controllerKeckz.Kekzcontroller(View).startConnection(host,23002)
        else:
            print 'not implemented yet'
            sys.exit()

#controllerKeckz.Kekzcontroller().startConnection('kekz.net',23002)
#controllerKeckz.Kekzcontroller().startConnection('pitix.ath.cx',23002)
#controllerKeckz.Kekzcontroller().startConnection('127.0.0.1',23002)

f = main()
f.connect(f.host, f.view)
print host