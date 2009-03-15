#!/usr/bin/env python

from distutils.core import setup

setup(name='rattlekekz',
      version='0.1',
      author="rattlekekz Team",
      author_email="egg@spam.de",
      packages=['rattlekekz','rattlekekz.core','rattlekekz.cliView','rattlekekz.plugins'],
      scripts=['bin/rattlekekz'],
      requires=['twisted(>=8.1.0)','urwid','json','OpenSSL'],
      url="http://kekz.net/",
      license="GPL v3 or higher"
     )
