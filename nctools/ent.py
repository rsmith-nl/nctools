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

    def __init__(self, x1=None, y1=None, x2=None, y2=None, index=None,
                 layer='0'):
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


class Polyline(Line):
    """A class for a polyline entity, consisting if several linked line
    segments.
    """

    def __init__(self, pnts, bulges, index, layer, closed=False):
        x = [x for x, _ in pnts]
        y = [y for _, y in pnts]
        Line.__init__(self, x[0], y[0], x[-1], y[-1],
                      index=index, layer=layer)
        self.angles = tuple(math.atan(b)*4 for b in bulges)
        self.name = 'polyline'
        self.closed = closed
        if closed:
            x.append(x[0])
            y.append(y[0])
        self.x = tuple(x)
        self.y = tuple(y)

    def _fmt(self, i):
        if self.angles[i-1] == 0.0:
            return " line to ({},{}),".format(self.x[i], self.y[i])
        a = math.degrees(self.angles[i-1])
        return " arc {}° to ({}, {}),".format(a, self.x[i], self.y[i])

    def __repr__(self):
        st = "<{} from ({},{})"
        se = " layer {}>"
        rv = [st.format(self.name, self.x[0], self.y[0])]
        rv += [self._fmt(i) for i in range(1, len(self.x))]
        rv += [se.format(self.layer)]
        return ''.join(rv)

    def flip(self):
        Line.flip(self)
        self.angles = tuple(-self.angles[i] for i in
                            xrange(len(self.angles)-1, -1, -1))

    def segments(self):
        """Returns a list detailing each segment in the form
        (start_point, end_point, start_angle)
        """
        pnts = zip(self.x, self.y)
        return zip(pnts, pnts[1:], self.angles)

    @property
    def length(self):
        dx2 = [(a - b)**2 for a, b, h in
               zip(self.x, self.x[1:], self.angles) if h == 0]
        dy2 = [(c - d)**2 for c, d, h in
               zip(self.y, self.y[1:], self.angles) if h == 0]
        slen = sum(math.sqrt(x2 + y2) for x2, y2 in zip(dx2, dy2))

        p = [(a, b, h) for a, b, h in
             zip(self.x, self.x[1:], self.angles) if h != 0]
        q = [(c, d) for c, d, h in
             zip(self.y, self.y[1:], self.angles) if h != 0]
        alen = []
        for (xs, xe, ang), (ys, ye) in zip(p, q):
            _, R, _, _ = arcdata((xs, ys), (xe, ye), ang)
            alen.append(math.fabs(ang*R))
        return slen + sum(alen)


class Arc(Line):
    """A class for an arc entity, centering in (cx, cy) with radius R from
    angle a1 to a2.
    """

    def __init__(self, cx, cy, R, a1, a2, index, layer, ccw=True):
        """Creates a Arc centering in (cx, cy) with radius R and running from
        a1 degrees to a2 degrees. The default is ccw.

        :cx, cy: center point
        :R: radius
        :a1: starting angle in degrees
        :a2: ending angle in degrees
        :index: sequence of the element in the DXF file.
        """
        self.ccw = ccw
        self.cx = float(cx)
        self.cy = float(cy)
        self.R = float(R)
        self.a = (float(a1), float(a2))
        x1 = cx+R*math.cos(math.radians(a1))
        y1 = cy+R*math.sin(math.radians(a1))
        x2 = cx+R*math.cos(math.radians(a2))
        y2 = cy+R*math.sin(math.radians(a2))
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

    def segments(self, devlim=1):
        """Create a list of points that approximates the arc.

        :devlim: Maximum distance that the line segments are to deviate from
                 the arc.
        :returns: A list of points
        """
        devlim = float(devlim)
        da = self.a[1]-self.a[0]
        step = math.degrees(2*math.acos(1-devlim/float(self.R)))
        cnt = da//step + 1
        step = da/cnt
        sa = self.a[0]
        if not self.ccw:
            sa = self.a[1]
            step = -step
        angs = [sa+i*step for i in range(int(cnt)+1)]
        pnts = [(self.cx+self.R*math.cos(math.radians(a)),
                 self.cy+self.R*math.sin(math.radians(a))) for a in angs]
        return pnts

    @property
    def bbox(self):
        """Get the bounding box.

        :returns: bounding box of the entity in the form of a 4-tuple (xmin,
        xmax, ymin, ymax)
        """
        a0, a1 = self.a[0], self.a[1]
        if self.ccw:
            if a0 > a1:
                a0 -= 360.0
            a1, a0 = int(a1), int(a0) + 1
        else:
            if a1 > a0:
                a1 -= 360.0
            a0, a1 = int(a1), int(a0) + 1
        R = self.R
        sin, cos, rad = math.sin, math.cos, math.radians
        points = [(R*cos(rad(k)), R*sin(rad(k))) for k in range(a0, a1)]
        points += zip(self.x, self.y)
        points += [(self.cx, self.cy)]
        return bbox.BBox(points)

    @property
    def length(self):
        if self.ccw:
            angle = math.radians(self.a[1]-self.a[0])
        else:
            angle = math.radians(self.a[0]-self.a[1])
        return self.R*angle


class Contour(Line):
    """A contour is a list of connected entities."""

    def __init__(self, entities):
        """Create a Contour from a list of entities.

        :entities: A list of connected entities.
        """
        if len(entities) == 1:
            raise ValueError('a contour should have more than one entity')
        # Flip the entities if necessary.
        if entities[0].points[1] not in entities[1].points:
            entities[0].flip()
        for a, b in zip(entities, entities[1:]):
            if b.points[0] != a.points[-1]:
                b.flip()
        self.entities = tuple(entities)
        # Now initiate the base class.
        x0, y0 = entities[0].points[0]
        x1, y1 = entities[-1].points[1]
        Line.__init__(self, x0, y0, x1, y1, entities[0].index)
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
        bbox.merge([e.bbox for e in self.entities])

    @property
    def length(self):
        return sum(e.length for e in self.entities)


def findcontours(ent):
    """Finds contours in a list of entities

    :ent: A list of entities
    :returns: A list of contours and a list of remaining entities
    """
    entities = ent[:]
    #print 'DEBUG: #entities:', len(entities)
    uniquepoints = list(set(p for e in entities for p in e.points))
    #print 'DEBUG: #uniquepoints:', len(uniquepoints)
    xrefs = {p: [e for e in entities if p in e.points]
             for p in uniquepoints}
    starters = [p for p in uniquepoints if len(xrefs[p]) == 1]
    #print 'DEBUG: #starters:', len(starters)
    contours = [_mkcontour(p, xrefs, entities) for p in starters]
    contours = [c for c in contours if c != None]
    return contours, entities


def _mkcontour(sp, xref, ent):
    """Find the contour (if any) that starts with sp.

    Starting with a starting point (sp) we find the entity it belongs to.
    This entity is the start of our contour. The starting point is then
    removed from the xref dict.

    Now we start looping over the points that are the keys in xref.
    If the last entry in the ce list is found in a particular dict value,
    it is removed. If the dict then has remaining values, the first one of
    those is appended to the ce list and removed from the entities list.
    We then resume the loop from the first key in the dict with a new last
    entry in ce. If no new entity is found, we quit the loop.

    :sp: Starting point.
    :xref: Dictionary of entities by their points
    :ent: List of entities
    :returns: A Contour or None.
    """
    try:
        #print 'DEBUG: sp', sp
        #print 'DEBUG: xref[sp]', xref[sp]
        ce = [xref[sp][0]]
    except KeyError:
        return None
    del xref[sp] # It has only one entity, and that's used now!
    ent.remove(ce[0])
    cont = True
    while cont:
        cont = False
        for p in xref.keys():
            if ce[-1] in xref[p]:
                xref[p].remove(ce[-1])
                if len(xref[p]) > 0:
                    ce.append(xref[p].pop(0)) # New entity, continue
                    ent.remove(ce[-1])
                    cont = True
                    break
                else:
                    del xref[p] # It's empty. End of the contour!
    if len(ce) == 1:
        ent.append(ce[0])
        return None
    return Contour(ce)


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
    a0 = math.atan2(ys - yc, xs - xc)
    a1 = math.atan2(ye - yc, xe - xc)
    return (xc, yc), R, a0, a1
