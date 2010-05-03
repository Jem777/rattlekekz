#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name='rattlekekz',
      version='20100503',
      author="Moritz Doll, Christian Scharkus",
      author_email="look@github.com",
      packages=['rattlekekz','rattlekekz.core','rattlekekz.cliView'],
      scripts=['bin/rattlekekz'],
      description="python-based commandline client for the crumbled chat",
      url="http://github.com/Jem777/rattlekekz",
      license="GPL v3 or higher",
      data_files=[('share/emoticons/rattlekekz',glob("rattlekekz/emoticons/*.png"))]
     )
