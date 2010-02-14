#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name='rattlekekz',
      version='20100214',
      author="Moritz Doll, Christian Scharkus",
      author_email="mail [dot] sensenmann [at] gmail [dot] com",
      packages=['rattlekekz','rattlekekz.core','rattlekekz.cliView'],
      scripts=['bin/rattlekekz'],
      requires=['twisted(>=8.1.0)','urwid','simplejson','OpenSSL'],
      url="http://github.com/Jem777/rattlekekz",
      license="GPL v3 or higher",
      data_files=[('share/emoticons/rattlekekz',glob("rattlekekz/emoticons/*.png")),
        ('share/emoticons/rattlekekz/kekz',glob("rattlekekz/emoticons/kekz/*.png"))]
     )
