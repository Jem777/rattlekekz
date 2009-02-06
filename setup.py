#!/usr/bin/env python

from distutils.core import setup

setup(name='Keckz',
      version='0.1',
      packages=['KECKz','KECKz.core','KECKz.cliView'],
      data_files=[('/bin',['bin/keckz'])],
      requires=['twisted(>=8.1.0)','urwid','json','OpenSSL']
      #package_dir = {'keckz': 'lib.keckz'},
      #package_data = {'keckz':['licence/']},
      #libraries=['twisted', 'urwid'],
     )