#!/usr/bin/env python
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-05-20 00:21:51 +0200
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to setup.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

from setuptools import setup

setup(
    name="nctools",
    author="Roland Smith",
    author_email="rsmith@xs4all.nl",
    license="BSD",
    version="$Revision$"[11:-2],
    scripts=["dxf2nc", "dxf2pdf", "dxfgerber", "nc2pdf", "readdxf",
             "readnc"],
    package_data={'': ['INSTALL.txt', 'README.txt']},
)
