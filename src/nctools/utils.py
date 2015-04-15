# vim:fileencoding=utf-8
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Utilities for nctools."""

from datetime import datetime
import glob
import os.path


class Msg(object):
    """Message printer"""

    def __init__(self, output=True):
        """Start the timer"""
        self.start = datetime.now()
        self.output = output

    def say(self, *args):
        """Print a message prepended by the elapsed time.

        :param *args: stuff to print
        """
        if not self.output:
            return
        delta = datetime.now() - self.start
        print('['+str(delta)[:-4]+']:', *args)


def outname(inname, extension, addenum=''):
    """Creates the name of the output filename based on the input filename.

    :param inname: name + path of the input file
    :param extension: extension of the output file.
    :param addenum: string to append to filename
    :returns: output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if rv.startswith('.') or rv.isspace():
        raise ValueError("Invalid file name!")
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    return rv + addenum + extension


def skip(error, filename):
    """Skip a file in case of an error

    :param error: exception
    :param filename: name of file to skip
    """
    print("Cannot read file: {}".format(error))
    print("Skipping file '{}'".format(filename))


def xpand(args):
    """Expand command line arguments for operating systems incapable of doing
    so.

    :param args: list of argument
    :returns: expanded argument list
    """
    xa = []
    for a in args:
        g = glob.glob(a)
        if g:
            xa += g
        else:
            xa += [a]
    return xa
