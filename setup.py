#!/usr/bin/env python
# file: setup.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2018-01-22 18:05:56 +0100
# Last modified: 2018-05-16T12:50:42+0200

from setuptools import setup

with open('README.rst') as f:
    ld = f.read()

name = 'nctools'
setup(
    name=name,
    version='2b0',
    description='Generate and inspect NC code for a Gerber cloth cutter',
    author='Roland Smith',
    author_email='rsmith@xs4all.nl',
    url='https://github.com/rsmith-nl/nctools',
    extras_require={'PDF': ["pycairo>=1.10"]},
    provides=[name],
    packages=[name],
    entry_points={
        'console_scripts': [
            'dumpgerber = nctools.dumpgerber:main', 'dxf2nc = nctools.dxf2nc:main',
            'dxf2pdf = nctools.dxf2pdf:main [PDF]', 'dxfgerber = nctools.dxfgerber:main',
            'nc2pdf = nctools.nc2pdf:main [PDF]', 'readdxf = nctools.readdxf:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Console',
        'Intended Audience :: Manufacturing', 'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent', 'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ],
    long_description=ld
)
