#!/usr/bin/env python3
# file: build.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-03-31 11:59:23 +0200
# Last modified: 2016-03-31 14:27:23 +0200

"""Build archives for the programs."""

import os
import py_compile
import shutil
import tempfile
import zipfile as z


def buildarchive(name):
    """
    Build an executable archive for a program that needs the nctools module.

    Arguments:
        name: Name of the main file without extension.
    """
    main = '__main__.py'
    tmpf = tempfile.TemporaryFile()
    try:
        os.remove(main)
    except OSError:
        pass  # It is OK for this file not to exist.
    os.link(name + '.py', main)
    # Forcibly compile __main__.py lest we use an old version!
    py_compile.compile(main)
    with z.PyZipFile(tmpf, mode='w', compression=z.ZIP_DEFLATED) as zf:
        zf.writepy(main)
        zf.writepy('nctools')
    os.unlink(main)
    tmpf.seek(0)
    archdata = tmpf.read()
    tmpf.close()
    with open(name, 'wb') as archive:
        archive.write(b'#!/usr/bin/env python3\n')
        archive.write(archdata)
    os.chmod(name, 0o755)


os.chdir('src')
names = [f[:-3] for f in os.listdir('.') if f.endswith('.py')]
for name in names:
    buildarchive(name)
    shutil.copy(name, '../' + name)
    os.remove(name)
