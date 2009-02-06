#!/usr/bin/env python

from distutils.core import setup

setup(name='Keckz',
      version='0.1',
      packages=['KECKz','KECKz.core','KECKz.cliView'],
      scripts=['bin/keckz'],
      #package_dir = {'keckz': 'lib.keckz'},
      #package_data = {'keckz':['licence/']},
      #libraries=['twisted', 'urwid'],
     )

