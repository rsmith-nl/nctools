# -*- coding: utf-8 -*-
# Installation script for dxfopt
#
# R.F. Smith <rsmith@xs4all.nl>
# $Date$

from distutils.core import setup

with open('README.txt') as f:
    ld = f.read()

setup(name='dxftools',
      version='$Revision$'[11:-2],
      license='BSD',
      description='Programs for processing DXF files for a Gerber cutter',
      author='Roland Smith', author_email='rsmith@xs4all.nl',
      url='http://www.xs4all.nl/~rsmith/software/',
      scripts=['dxfgerber.py', 'dxf2nc.py', 'ncfmt.py', 'nc2pdf.py'],
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
