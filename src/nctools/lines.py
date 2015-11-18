# file: lines.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-11-14 18:56:39 +0100
# Last modified: 2015-11-17 22:57:47 +0100
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


def closed(line):
    """
    Determine if a list of line segments is closed.

    Arguments:
        line: list of 2-tuples (x, y)

    Returns:
        True if the last point in the line equals the first point. False
        otherwise.
    """
    first, last = line[0], line[-1]
    return first[0] == last[0] and first[1] == last[1]


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
