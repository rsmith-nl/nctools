# -*- coding: utf-8 -*-
# Installation script for dxfopt
#
# R.F. Smith <rsmith@xs4all.nl>
# $Date$

from distutils.core import setup

ld = """These modules and programs are designed to read DXF files and read and
write g-code files for Gerber cloth cutters (not PCB machines). Also included
is the ability to create PDF files from either XDF or g-code. See the included
README.txt for a longer explanation."""


setup(name='nctools',
      version='$Revision$'[11:-2],
      license='BSD',
      description=\
      'Programs for creating and manipulating nc files for a Gerber cutter',
      author='Roland Smith', author_email='rsmith@xs4all.nl',
      url='http://www.xs4all.nl/~rsmith/software/',
      scripts=['dxfgerber.py', 'dxf2nc.py', 'ncfmt.py', 'nc2pdf.py',
               'dxf2pdf.py'],
      provides='nctools', packages=['nctools'],
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
