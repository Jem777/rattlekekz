#!/usr/bin/env python

from distutils.core import setup

setup(name='rattleKekz',
      version='0.1',
      author="KECKz Team",
      author_email="egg@spam.de",
      packages=['rattleKekz','rattleKekz.core','rattleKekz.cliView'],
      scripts=['bin/rattleKekz'],
      requires=['twisted(>=8.1.0)','urwid','json','OpenSSL'],
      url="http://kekz.net/",
      license="GPL v3 or higher"
     )
