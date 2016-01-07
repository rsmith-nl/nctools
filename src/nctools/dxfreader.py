# vim:fileencoding=utf-8:ft=python
# file: dxfreader.py
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-04-16 11:57:29 +0200
# Last modified: 2016-01-07 00:37:29 +0100
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

import math
import re

devlim = 1  # maximum deviation from arc, spline


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

    Arguments:
        data: Input list of DXF (group, data) tuples.

    Returns:
        A list of drawing entities, each as a dictionary
        keyed by group code.
    """
    soe = [n for n, d in enumerate(data) if d[1] == 'ENTITIES'][0]
    eoe = [n for n, d in enumerate(data) if d[1] == 'ENDSEC' and n > soe][0]
    entdata = data[soe+1:eoe]
    idx = [n for n, d in enumerate(entdata) if d[0] == 0] + [len(entdata)]
    pairs = list(zip(idx, idx[1:]))
    entities = [dict(entdata[b:e]) for b, e in pairs]
    return entities


def layernames(entities):
    """
    Get all layer names from the entities

    Arguments:
        Entities: An iterable if dictionaries, each containing a DXF entity.

    Returns:
        A sorted list of layer names.
    """
    lnames = list(set(e[8] for e in entities))
    lnames.sort()
    return lnames


def numberedlayers(entities):
    """
    Get all layer names from the entities that contain a number, except for
    layer 0.

    Arguments:
        entities: An iterable of dictionaries, each containing a DXF entity.

    Returns:
        A list of layer names with a number in them, sorted by ascending
        number.
    """
    layers = layernames(entities)
    numbered = [ln for ln in layers if len(re.findall('[1-9]\d*', ln)) == 1]
    numbered.sort(key=lambda ln: int(re.search('[1-9]\d*', ln).group()))
    return numbered


def fromlayer(entities, name):
    """
    Return only the entities from the named layer.

    Arguments:
        entities: An iterable of dictionaries, each containing a DXF entity.
        name: The name of the layer to filter on.

    Returns:
        A list of entities.
    """
    return [e for e in entities if e[8] == name]


def mksegments(entities, ndigits=2):
    """
    Convert an iterable of entities to a list of line segments.

    Arguments:
        entities: An iterable if dictionaries, each containing a DXF entity.
        ndigits: Rounds to ndigits after the decimal point.

    Returns:
        A list of line segments. Line segments are lists of ≥2 (x,y) tuples.
    """
    def fr(n):
        return round(float(n), ndigits)

    def line(e):
        return [(fr(e[10]), fr(e[20])), (fr(e[11]), fr(e[21]))]

    def arc(e):
        cx, cy = fr(e[10]), fr(e[20])
        R = fr(e[40])
        sa, ea = math.radians(float(e[50])), math.radians(float(e[51]))
        if ea > sa:
            da = ea - sa
        else:
            da = 2*math.pi - sa + ea
        if devlim > R:
            cnt = 1
        else:
            maxstep = 2*math.acos(1-devlim/R)
            if da < 0:
                maxstep = -maxstep
            cnt = math.ceil(da/maxstep)
        step = da/cnt
        angs = [sa+i*step for i in range(cnt+1)]
        pnts = [(fr(cx+R*math.cos(a)), fr(cy+R*math.sin(a))) for a in angs]
        return pnts

    # Convert lines
    lines = [line(e) for e in entities if e[0] == 'LINE']
    # Convert arcs
    lines += [arc(e) for e in entities if e[0] == 'ARC']
    # Convert polylines
    pi = [n for n, e in enumerate(entities) if e[0] == 'POLYLINE']
    se = [n for n, e in enumerate(entities) if e[0] == 'SEQEND']
    for start in pi:
        end = [n for n in se if n > start][0]
        poly = entities[start:end]
        points = [(fr(e[10]), fr(e[20])) for e in poly[1:]]
        angles = [math.atan(float(e[42]))*4 if 42 in e else None for e in
                  poly[1:]]
        if 70 in poly[0] and (int(poly[0][70]) & 1):  # closed polyline
            points.append(points[0])
        ends = zip(points, points[1:], angles)
        addition = [points[0]]
        for sp, ep, a in ends:
            if a:
                arcent = _arcdata(sp, ep, a)
                addition += arc(arcent)[1:]
            else:
                addition.append(ep)
        lines += [addition]
    return lines


def _arcdata(sp, ep, angs):
    """Calculate arc properties for a curved polyline section

    Arguments:
        sp: startpoint
        ep: endpoint
        angs: enclosed angle. positive = CCW, negative = CW

    Returns:
        an arc entity
    """
    xs, ys = sp
    xe, ye = ep
    if angs == 0.0:
        raise ValueError('not a curved section')
    xm, ym = (xs + xe)/2.0, (ys + ye)/2.0
    xp, yp = xm - xs, ym - ys
    lp = math.sqrt(xp**2 + yp**2)
    lq = lp/math.tan(angs/2.0)
    f = lq/lp
    if angs > 0:
        xc, yc = xm - f * yp, ym + f * xp
    else:
        xc, yc = xm + f * yp, ym - f * xp
    R = math.sqrt((xc-xs)**2 + (yc-ys)**2)
    twopi = 2*math.pi
    a0 = math.atan2(ys - yc, xs - xc)
    a1 = math.atan2(ye - yc, xe - xc)
    if angs > 0:
        if a0 < 0:
            a0 += twopi
        if a1 <= 0:
            a1 += twopi
    else:
        if a0 <= 0:
            a0 += twopi
        if a1 < 0:
            a1 += twopi
    return {10: xc, 20: yc, 40: R, 50: math.degrees(a0), 51: math.degrees(a1)}
