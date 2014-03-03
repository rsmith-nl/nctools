#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS AS IS'' AND
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

"""Drawing entities."""

import math
import bbox

__version__ = '$Revision$'[11:-2]

class Line(object):
    """A class for a line entity, from point (x1, y1) to (x2, y2).
    The class attribute delta contains the maximum distance in x and y
    direction between eindpoints that are considered coincident.
    """

    def __init__(self, x1, y1, x2, y2, index=None, layer='0'):
        """Creates a line from (x1, y1) to (x2, y2).

        :x1, y1: start point of the entity
        :x2, y2: end point of the entity
        :index: sequence number
        :layer: name of the layer the entity belongs to
        """
        # x and y contain point coordinates.
        self.x = (float(x1), float(x2))
        self.y = (float(y1), float(y2))
        # index is a arbitrary sequence number °
        self.index = index
        self.name = 'line'
        self.layer = layer

    def __repr__(self):
        s = "<{} from ({},{}) to ({},{}), layer {}>"
        return s.format(self.name, self.x[0], self.y[0],
                        self.x[-1], self.y[-1], self.layer)

    def move(self, dx, dy):
        """Move the entity.

        :dx: movement in the x direction
        :dy: movement in the y direction
        """
        self.x = tuple(j + dx for j in self.x)
        self.y = tuple(k + dy for k in self.y)

    def flip(self):
        """Reverse the direction of a line.
        """
        self.x = tuple(reversed(self.x))
        self.y = tuple(reversed(self.y))

    def hsplit(self, x):
        b = self.bbox
        if x < b.minx or x >  b.maxx:
            return [self] # no split
        else:
            frac = (x - self.x[0])/(self.x[1] - self.x[0])
            y = self.y[0] + frac*(self.y[1] - self.y[0])
            a = Line(self.x[0], self.y[0], x, y, self.index, self.layer)
            b = Line(x, y, self.x[1], self.y[1], self.index, self.layer)
            if self.x[0] < self.x[1]:
                return [a], [b]
            return [b], [a]

    @property
    def points(self):
        """Returns the end points of the entity."""
        return (self.x[0], self.y[0]), (self.x[-1], self.y[-1])

    @property
    def bbox(self):
        """Get the bounding box.

        :returns: bounding box of the entity in the form of a 4-tuple (xmin,
        xmax, ymin, ymax)
        """
        return bbox.BBox(zip(self.x, self.y))

    @property
    def length(self):
        """Returns the length of the entity."""
        dx = self.x[1]-self.x[0]
        dy = self.y[1]-self.y[0]
        return math.sqrt(dx*dx+dy*dy)


class Arc(Line):
    """A class for an arc entity, centering in (cx, cy) with radius R from
    angle a1 to a2.
    """

    def __init__(self, cx, cy, R, a1, a2, index=None, layer='0', ccw=True):
        """Creates a Arc centering in (cx, cy) with radius R and running from
        a1 to a2 radians. The default is ccw.

        :cx, cy: center point
        :R: radius
        :a1: starting angle in radians. It should be in [0, 2π]
        :a2: ending angle in radians. It should be in [0, 2π]
        :index: sequence of the element in the DXF file.
        """
        a1 = float(a1)
        a2 = float(a2)
        self.ccw = ccw
        self.cx = float(cx)
        self.cy = float(cy)
        self.R = float(R)
        self.a = (a1, a2)
        self.sa = a1
        if ccw:
            if a2 > a1:
                self.da = a2 - a1
            else:
                self.da = 2 * math.pi - a1 + a2
        else: # CW
            if a1 < a2:
                self.da = a2 - a1
            else:
                self.da = a2 - a1 - 2 * math.pi
        x1 = cx+R*math.cos(a1)
        y1 = cy+R*math.sin(a1)
        x2 = cx+R*math.cos(a2)
        y2 = cy+R*math.sin(a2)
        Line.__init__(self, x1, y1, x2, y2, index, layer)
        self.name = 'arc'

    def move(self, dx, dy):
        Line.move(self, dx, dy)
        self.cx += dx
        self.cy += dy

    def flip(self):
        """Reverse the direction of a line.
        """
        Line.flip(self)
        self.ccw = not self.ccw
        self.a = (self.a[1], self.a[0])
        self.sa = self.sa + self.da
        self.da = -self.da


    def hsplit(self, x):
        xfrac = (x - self.cx)/self.R
        if xfrac > 1 or xfrac < -1:
            # no split
            return [self]
        start = self.sa
        p0 = math.acos(xfrac)
        p1 = _clamp(math.pi*2-p0 - start)
        p0 = _clamp(p0 - start)
        print "p0: {}, p1: {}".format(p0, p1)
        if self.da > 0:
            ip = [j for j in (p0,  p1) if 0 <= j <= self.da]
        else:
            ip = [j for j in (p0, p1) if self.da <= j <= 0]
        ip.insert(0, 0.0)
        ip.append(self.da)
        ip = [_clamp(i + start) for i in ip]
        rv = []
        for sa, ea in zip(ip, ip[1:]):
            rv.append(Arc(self.cx, self.cy, self.R, sa, ea, self.index,
                          self.layer))
        left, right = [], []
        for e in rv:
            if e.bbox.minx < x:
                left.append(e)
            else:
                right.append(e)
        return left, right


    def segments(self, devlim=1):
        """Create a list of points that approximates the arc.

        :devlim: Maximum distance that the line segments are to deviate from
                 the arc.
        :returns: A list of points
        """
        sa, da = self.sa, self.da
        devlim = float(devlim)
        if devlim > self.R:
            cnt = 1
        else:
            step = 2*math.acos(1-devlim/float(self.R))
            if da < 0:
                step = -step
            cnt = int(math.fabs(da/step)) + 1
        step = da/float(cnt)
        angs = [sa+i*step for i in range(int(cnt)+1)]
        pnts = [(self.cx+self.R*math.cos(a),
                 self.cy+self.R*math.sin(a)) for a in angs]
        return pnts

    @property
    def bbox(self):
        """Get the bounding box.

        :returns: bounding box of the entity in the form of a 4-tuple (xmin,
        xmax, ymin, ymax)

        We're using degrees here because it is convenient for the calculation.
        """
        sa = math.degrees(self.sa)
        da = int(math.degrees(self.da))
        if da > 0:
            angles = [sa + t for t in range(0, da+1, 1)]
        else:
            angles = [sa + t for t in range(0, da-1, -1)]
        cx, cy, R = self.cx, self.cy, self.R
        sin, cos, rad = math.sin, math.cos, math.radians
        points = [(cx+R*cos(rad(k)), cy+R*sin(rad(k))) for k in angles]
        return bbox.BBox(points)

    @property
    def length(self):
        if self.ccw:
            angle = self.a[1]-self.a[0]
        else:
            angle = self.a[0]-self.a[1]
        return self.R*angle


class Contour(Line):
    """A contour is a list of connected entities."""

    def __init__(self, entities, index=None, layer='0'):
        """Create a Contour from a list of entities.

        :entities: A list of connected entities.
        """
        if len(entities) == 1:
            raise ValueError('a contour should have more than one entity')
        self.entities = tuple(entities)
        # Now initiate the base class.
        x0, y0 = entities[0].points[0]
        x1, y1 = entities[-1].points[1]
        if index == None:
            index = entities[0].index
        Line.__init__(self, x0, y0, x1, y1, index, layer)
        self.name = 'contour'

    def move(self, dx, dy):
        Line.move(self, dx, dy)
        for e in self.entities:
            e.move(dx, dy)

    def flip(self):
        """Contour cannot be reversed.
        """
        pass

    @property
    def bbox(self):
        return bbox.merge([e.bbox for e in self.entities])

    @property
    def length(self):
        return sum(e.length for e in self.entities)


def arcdata(sp, ep, angs):
    """Calculate arc properties for a curved polyline section

    :sp: startpoint
    :ep: endpoint
    :angs: enclosed angle. positive = CCW, negative = CW
    :returns: center point, radius, start angle, end angle
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
    return (xc, yc), R, a0, a1


def _clamp(a):
    """Clamp an angle to the range [0,2π]

    :a: angle in radians
    :returns: angle in the range [0,2π]
    """
    c = 2*math.pi
    while a < 0.0:
        a += c
    while a > c:
        a -= c
    return a


def _dist2(a, b):
    """Calculate the square of the distance between two points. Since this
    measure is only used for comparison purposes, there is no need to perform
    the square root calculation.

    :a: first point (a 2-tuple)
    :b: second point
    :returns: the square of the distance between the points
    """
    x, y = a
    j, k = b
    return (x-j)**2 + (y-k)**2


def _chkdist(p, e, lim):
    """Check wether a point is near enough to other points to

    :p: a point (2-tuple)
    :e: either a point or a 2-tuple of points
    :lim: maximum square of the distance between two points considered equal
    :returns: True is the distance to one of the endpoints is ≤ 0.5.
    """
    if isinstance(e[0], tuple):
        a, b = e
        return min(_dist2(p, a), _dist2(p, b)) <= lim
    return _dist2(p, e) <= lim


def _contour(se, ent, lim):
    """Find a contour in a list of entities.

    :se: starting entity
    :ent: list of entities
    :lim: maximum square of the distance between two points considered equal
    """
    ent.remove(se)
    cl = [se]
    while True:
        # Look for connections at the end point
        _, ep = cl[-1].points
        ce = [e for e in ent if _chkdist(ep, e.points, lim)]
        if ce:
            newend = ce[0]
            if _chkdist(ep, newend.points[1], lim):
                newend.flip()
            ent.remove(newend)
            cl.append(newend)
        else:
            # Look for connections at the start point
            sp, _ = cl[0].points
            cs = [e for e in ent if _chkdist(sp, e.points, lim)]
            if cs:
                newstart = cs[0]
                if _chkdist(sp, newstart.points[0], lim):
                    newstart.flip()
                ent.remove(newstart)
                cl.insert(0, newstart)
            else:
                break
    # If no additional entities are found, it's not a contour.
    if len(cl) == 1:
        ent.append(se)
        return None
    return Contour(cl)


def findcontours(ent, lim=0.25):
    """Find contours in a list of entities.

    :ent: list of entities
    :lim: maximum square of the distance between two points considered equal
    """
    contours = [_contour(e, ent, lim) for e in ent]
    contours = [c for c in contours if c != None]
    return contours, ent
