# -*- coding: utf-8 -*-
# Installation script for dxfopt
#
# R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2011-10-17 10:20:27 rsmith>

from distutils.core import setup

with open('README.txt') as f:
    ld = f.read()

setup(name='dxftools',
      version='VERSION',
      license='BSD',
      description='Program for optimizing DXF files for a Gerber cutter',
      author='Roland Smith', author_email='rsmith@xs4all.nl',
      url='http://www.xs4all.nl/~rsmith/software/',
      scripts=['dxfgerber'],
      provides='dxfgerber', 
      py_modules=['dxfgeom'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Manufacturing',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'
                   ],
      long_description = ld
      )
