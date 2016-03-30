# vim:fileencoding=utf-8
# Copyright © 2013-2016 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Last modified: 2016-03-30 22:12:13 +0200
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

import glob
import os.path
from nctools import lines


def outname(inname, extension, addenum=''):
    """Creates the name of the output filename based on the input filename.

    Arguments:
        inname: Name + path of the input file.
        extension: Extension of the output file.
        addenum: String to append to filename.

    Returns:
        Output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if rv.startswith('.') or rv.isspace():
        raise ValueError("Invalid file name!")
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    return rv + addenum + extension


def xpand(args):
    """Expand command line arguments for operating systems incapable of doing
    so.

    Arguments:
        args: List of arguments.

    Returns:
        Expanded argument list.
    """
    xa = []
    for a in args:
        g = glob.glob(a)
        if g:
            xa += g
        else:
            xa += [a]
    return xa


# Key functions for sorting segments
def distkey(s):
    """
    Sort key for sorting segments by distance from the origin.

    Argument:
        s: Segment; list of 2-tuples (x,y)

    Returns:
        The square of the distance from the lower-left corner of the bounding
        box to the origin.
    """
    bx, by, _, _ = lines.bbox(s)
    return bx*bx+by*by


def bbxykey(s):
    """
    Sort key for segments first by the left of the bounding box and then
    by the bottom.

    Argument:
        s: Segment; list of 2-tuples (x,y)

    Returns:
        A 2-tuple that is the lower left corner of the bounding box.
    """
    bb = lines.bbox(s)
    return (bb[0], bb[1])


def bbyxkey(s):
    """
    Sort key for segments first by the bottom of the bounding box and then
    by the left.

    Argument:
        s: Segment; list of 2-tuples (x,y)

    Returns:
        A 2-tuple that is the reversed lower left corner of the bounding box.
    """
    bb = lines.bbox(s)
    return (bb[1], bb[0])
