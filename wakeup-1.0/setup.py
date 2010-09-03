#!/usr/bin/env python

from distutils.core import setup
import os

data_files=[
          ('share/applications', ['data/wakeup.desktop']),
          ('share/man/man1', ['doc/wakeup.1']),
          ('share/man/man1', ['doc/setalarm.1']),
          ('share/man/man1', ['doc/wakeup-settings.1'])
          ]
for root, dirs, files in os.walk('data/wakeup'):
    for f in files:
        dest = os.path.join('share', root.replace('data/', ''))
        filename = os.path.join(root, f)
        if os.path.isfile(filename):
            data_files.append((dest, [filename]))


setup(name='wakeup',
      version='1.0.0',
      description='Fully customizable and extensible talking alarm clock',
      author='David Glass',
      author_email='dsglass@gmail.com',
      url='http://wakeupalarm.sourceforge.net/',
      license='GPL v3',
      scripts=['data/scripts/wakeup-settings',
               'data/scripts/wakeup',
               'data/scripts/setalarm'],
      data_files=data_files
     )

