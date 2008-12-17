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
        self.view = 'default'
        for o,p in opts:
            if o in ['-h','--host']:
                self.host = p
            #elif o in ['-v','--view']:
            #    view = p
            elif o in ['-?','--help']:
                print 'Usage: keckz [-?][-h <host>][-v <view>]'
                print '-?, --help: Display this help'
                print '-h, --host: Host to connect, Default: kekz.net'
                print '-v, --view: View to use, Default: cli'
                exit()

    def connect(self, host, view):
        if view in 'default':
            controllerKeckz.Kekzcontroller().startConnection(host,23002)
        else:
            print 'not implemented yet'
            exit()

#controllerKeckz.Kekzcontroller().startConnection('kekz.net',23002)
#controllerKeckz.Kekzcontroller().startConnection('pitix.ath.cx',23002)
#controllerKeckz.Kekzcontroller().startConnection('127.0.0.1',23002)

f = main()
f.connect(f.host, f.view)
print host