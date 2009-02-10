#!/usr/bin/env python

from distutils.core import setup

setup(name='Keckz',
      version='0.1',
      author="KECKz Team",
      author_email="egg@spam.de",
      packages=['KECKz','KECKz.core','KECKz.cliView'],
      scripts=['bin/keckz'],
      requires=['twisted(>=8.1.0)','urwid','json','OpenSSL'],
      url="http://kekz.net/",
      license="GPL v3 or higher"
     )
