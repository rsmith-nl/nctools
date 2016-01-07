# file: lines.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-11-14 18:56:39 +0100
# Last modified: 2016-01-08 00:06:41 +0100
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

"""A module for dealing with line segments.
Basically, a line segment is a list of two or more
2-tuples (x,y).

Since line segments are lists, standard member functions like reverse() and
len() can be used.
"""

import math


devlim = 1  # maximum deviation from arc, spline


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


def combine_segments(segments):
    """
    Combine the segments where possible.

    Arguments:
        segments: List of segments. A segment is a list of two or more
            (x,y) tuples. This list will be consumed by this function.

    Returns:
        A list of closed segments and a list of open segments.
    """
    openseg = []
    loops = []
    while len(segments) > 1:
        sp, ep = segments[0][0], segments[0][-1]
        rem = segments[1:]
        sprem, eprem = [s[0] for s in rem], [s[-1] for s in rem]
        if sp in sprem:
            idx = sprem.index(sp) + 1
            frag = segments.pop(idx)[1:]
            frag.reverse()
            newseg = frag + segments[0]
        elif sp in eprem:
            idx = eprem.index(sp) + 1
            newseg = segments.pop(idx)[:-1] + segments[0]
        elif ep in sprem:
            idx = sprem.index(sp) + 1
            newseg = segments[0] + segments.pop(idx)[1:]
        elif ep in eprem:
            idx = eprem.index(ep) + 1
            frag = segments.pop(idx)[:-1]
            frag.reverse()
            newseg = segments[0] + frag
        else:
            # no connections found
            head = segments.pop()
            if closed(head):
                loops.append(head)
            else:
                openseg.append(head)
            continue
        segments[0] = newseg
    if closed(segments[0]):
        loops.append(segments[0])
    else:
        openseg.append(segments[0])
    return loops, openseg


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


def length(line):
    """
    Determine the total line length of a list of line segments.

    Arguments:
        line: list of 2-tuples (x, y)

    Returns:
        The sum of the lengths of the line segments between the listed points.
    """
    dist = [math.sqrt((c-a)**2+(d-b)**2) for ((a, b), (c, d))
            in zip(line, line[1:])]
    return sum(dist)


def closed(line, delta=1e-3):
    """
    Determine if a list of line segments is closed.

    Arguments:
        line: list of 2-tuples (x, y)
        delta: significant distance between points

    Returns:
        True if the last point in the line equals the first point. False
        otherwise.
    """
    first, last = line[0], line[-1]
    return abs(first[0]-last[0]) < delta and abs(first[1]-last[1]) < delta


def setstart(line, newstart):
    """Change the start point of a closed line segment.

    Arguments:
        line: list of 2-tuples (x, y)
    """
    if not closed(line):
        raise ValueError('line is not closed')
    line.pop()  # Remove last point
    i = line.index(newstart)  # raises ValueError when newstart not in list.
    line[:] = line[i:] + line[:i]
    line.append(line[0])


def bbox(line):
    """
    Calculate the bounding box around a line.

    Arguments:
        line: list of 2-tuples (x, y)

    Returns:
        a 4-tuple (minx, miny, maxx, maxy).
    """
    x = [p[0] for p in line]
    y = [p[1] for p in line]
    return (min(x), min(y), max(x), max(y))


def bbox_area(line):
    """
    Calculate the area of the bounding box around a line.

    Arguments:
        line: list of 2-tuples (x, y)

    Returns:
        The product of width*height.
    """
    a, b, c, d = bbox(line)
    return (c-a)*(d-b)


def merge_bbox(bboxes):
    """
    Merge bounding boxes.

    Arguments:
        bboxes: iterator of bbox tuples.

    Returns:
        An encompassing bbox.
    """
    minx, miny = [], []
    maxx, maxy = [], []
    for a, b, c, d in bboxes:
        minx.append(a)
        miny.append(b)
        maxx.append(c)
        maxy.append(d)
    return (min(minx), min(miny), max(maxx), max(maxy))
