#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

"""Module for reading DXF files and extracting supported entities."""

import ent

__version__ = '$Revision$'[11:-2]


def Reader(name):
    """Read a DXF file.

    :name: The name of the file to read.
    :returns: A list of entities.
    """
    with open(name, 'r') as f:
        data = [s.strip() for s in f.readlines()]
    soe = data.index('ENTITIES')+1
    eoe = data.index('ENDSEC', soe)
    lines = data[soe:eoe]
    entities = _get_lines(lines)
    entities += _get_arcs(lines)
    entities += _get_polylines(lines)
    entities.sort(key=lambda x: x.index)
    return entities


def _get_lines(lines):
    idx = [x for x in range(len(lines)) if lines[x] == 'LINE']
    rv = []
    for i in idx:
        num = lines.index("8", i) + 1
        layer = lines[num]
        num = lines.index("10", num) + 1
        x1 = float(lines[num])
        num = lines.index("20", num) + 1
        y1 = float(lines[num])
        num = lines.index("11", num) + 1
        x2 = float(lines[num])
        num = lines.index("21", num) + 1
        y2 = float(lines[num])
        rv.append(ent.Line(x1, y1, x2, y2, i, layer))
    #print 'DEBUG: dxf.Reader found {} lines'.format(len(rv))
    return rv


def _get_arcs(lines):
    idx = [x for x in range(len(lines)) if lines[x] == 'ARC']
    rv = []
    for i in idx:
        num = lines.index("8", i) + 1
        layer = lines[num]
        num = lines.index("10", num) + 1
        cx = float(lines[num])
        num = lines.index("20", num) + 1
        cy = float(lines[num])
        num = lines.index("40", num) + 1
        R = float(lines[num])
        num = lines.index("50", num) + 1
        a1 = float(lines[num])
        num = lines.index("51", num) + 1
        a2 = float(lines[num])
        if a2 < a1:
            a2 += 360.0
        rv.append(ent.Arc(cx, cy, R, a1, a2, i, layer))
    #print 'DEBUG: dxf.Reader found {} arcs'.format(len(rv))
    return rv


def _get_polylines(lines):
    idx = [x for x in range(len(lines)) if lines[x] == 'POLYLINE']
    rv = []
    for i in idx:
        num = lines.index("8", i) + 1
        layer = lines[num]
        num = lines.index("70", num) + 1
        closed = int(lines[num]) & 1
        end = lines.index('SEQEND', i)
        vi = [w for w in range(i, end) if lines[w] == 'VERTEX']
        vi = zip(vi, vi[1:]+[end])
        pnts = []
        bulges = []
        for j, k in vi:
            num = lines.index("10", j) + 1
            x = float(lines[num])
            num = lines.index("20", num) + 1
            y = float(lines[num])
            pnts.append((x, y))
            try:
                num = lines.index("42", num) + 1
                if num < k:
                    bulges.append(float(lines[num]))
                else:
                    bulges.append(0)
            except ValueError:
                bulges.append(0)
        rv.append(ent.Polyline(pnts, bulges, i, layer, closed))
    #print 'DEBUG: dxf.Reader found {} polylines'.format(len(rv))
    return rv


# Built-in test.
if __name__ == '__main__':
    pass
