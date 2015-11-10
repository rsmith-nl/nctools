# vim:fileencoding=utf-8:ft=python
# file: dxfreader.py
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-04-16 11:57:29 +0200
# Last modified: 2015-06-05 00:32:38 +0200
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
# NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Module for retrieving the drawing entities from DXF files."""


def parse(filename):
    """Read a DXF file and break it into (group, data) tuples.

    :param filename: Name of a DXF file to read.
    :returns: A list of (group, data) tuples
    """
    with open(filename, encoding='cp1252') as dxffile:
        lines = dxffile.readlines()
    lines = [ln.strip() for ln in lines]
    data = list(zip(lines[::2], lines[1::2]))
    return [(int(g), d) for g, d in data]


def entities(data):
    """Isolate the entity data from a list of (group, data) tuples.

    :param data: Input list of DXF (group, data) tuples.
    :returns: A list of drawing entities, each as a dictionary
    keyed by group code.
    """
    soe = [n for n, d in enumerate(data) if d[1] == 'ENTITIES'][0]
    eoe = [n for n, d in enumerate(data) if d[1] == 'ENDSEC' and n > soe][0]
    entdata = data[soe+1:eoe]
    idx = [n for n, d in enumerate(entdata) if d[0] == 0] + [len(entdata)]
    pairs = list(zip(idx, idx[1:]))
    entities = [dict(entdata[b:e]) for b, e in pairs]
    return entities
