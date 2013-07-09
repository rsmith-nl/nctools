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

__version__ = '$Revision$'[11:-2]

class Entity(object):
    """A base class for a drawing entities.

    The class attribute delta contains the maximum distance in x and y
    direction between eindpoints that are considered coincident. 
    """
    delta = 0.1
    _anoent = "Argument is not an entity!"

    def __init__(self, x1=None, y1=None, x2=None, y2=None, index=None,
                 layer='0'):
        """Creates an Entity from (x1, y1) to (x2, y2).
        
        :x1, y1: start point of the entity
        :x2, y2: end point of the entity
        :index: where the entity started in the ENTITIES section
        :layer: name of the layer the entity belongs to
        """
        # x and y contain point coordinates.
        self.x = (float(x1), float(x2))
        self.y = (float(y1), float(y2))
        # index is a arbitrary sequence number °
        self.index = index
        self.name = ''
        self.layer = layer

    def __repr__(self):
        s = "<{} from ({},{}) to ({},{}), layer {}>"
        return s.format(self.name, self.x[0], self.y[0], 
                        self.x[1], self.y[1], self.layer)

    @property
    def bbox(self):
        """Get the bounding box.

        :returns: bounding box of the entity in the form of a 4-tuple (xmin,
        xmax, ymin, ymax)
        """
        minx, maxx = min(self.x), max(self.x)
        miny, maxy = min(self.y), max(self.y)
        return (minx, maxx, miny, maxy)

    def move(self, dx, dy):
        """Move the entity.
        
        :dx: movement in the x direction
        :dy: movement in the y direction
        """
        self.x = tuple(j + dx for j in self.x)
        self.y = tuple(k + dy for k in self.y)

    @property
    def startpoint(self):
        """Returns the start point of the entity."""
        return self.x[0], self.y[0]

    @property
    def endpoint(self):
        """Returns the end point of the entity."""
        return self.x[-1], self.y[-1]

    def otherpoint(self, pnt):
        """If pnt is one of the ends, return the other.

        :pnt: endpoint
        :returns: other endpoint
        """
        if pnt == self.startpoint:
            return self.endpoint
        elif pnt == self.endpoint:
            return self.startpoint
        else:
            raise ValueError('point not in entity')

    @property
    def length(self):
        """Returns the length of the entity."""
        raise NotImplementedError


class Line(Entity):
    """A class for a line entity, from point (x1, y1) to (x2, y2)"""

    def __init__(self, x1, y1, x2, y2, index, layer):
        """Creates a Line from (x1, y1) to (x2, y2)."""
        Entity.__init__(self, x1, y1, x2, y2, index, layer)
        self.name = 'line'

#    @property
#    def dxfdata(self):
#        lines = ['  0', 'LINE', '  8', 'snijlijnen', ' 10', str(self.x[0]),
#                 ' 20', str(self.y[0]), ' 30', '0.0', ' 11', str(self.x[1]),
#                 ' 21', str(self.y[1]), ' 31', '0.0', '']
#        # empty string for adding a last newline with the join.
#        return lines

    @property
    def length(self):
        dx = self.x[1]-self.x[0]
        dy = self.y[1]-self.y[0]
        return math.sqrt(dx*dx+dy*dy)


class Polyline(Entity):
    """A class for a polyline entity, consisting if several linked line
    segments.
    """

    def __init__(self, pnts, index, layer):
        x = tuple(x for x, _ in pnts)
        y = tuple(y for _, y in pnts)
        Entity.__init__(self, x[0], y[0], x[-1], y[-1], 
                        index=index, layer=layer)
        self.x = x
        self.y = y
        self.name = 'polyline'

    @property
    def dxfdata(self):
        pass

    @property
    def length(self):
        dx2 = [(a - b)**2 for a, b in zip(self.x, self.x[1:])]
        dy2 = [(c - d)**2 for c, d in zip(self.y, self.y[1:])]
        return sum(x2 + y2 for x2, y2 in zip(dx2, dy2))**0.5


class Arc(Entity):
    """A class for an arc entity, centering in (cx, cy) with radius R from
    angle a1 to a2.
    """

    def __init__(self, cx, cy, R, a1, a2, index, layer):
        """Creates a Arc centering in (cx, cy) with radius R and running from
        a1 degrees ccw to a2 degrees.
        
        :cx, cy: center point 
        :R: radius
        :a1: starting angle in degrees
        :a2: ending angle in degrees
        :index: sequence of the element in the DXF file.
        """
        if a2 < a1:
            em = 'Arcs are defined CCW, so a2 must be greater than a1'
            raise ValueError(em)
        self.cx = float(cx)
        self.cy = float(cy)
        self.R = float(R)
        self.a = (float(a1), float(a2))
        x1 = cx+R*math.cos(math.radians(a1))
        y1 = cy+R*math.sin(math.radians(a1))
        x2 = cx+R*math.cos(math.radians(a2))
        y2 = cy+R*math.sin(math.radians(a2))
        Entity.__init__(self, x1, y1, x2, y2, index, layer)
        self.name = 'arc'

    def move(self, dx, dy):
        Entity.move(self, dx, dy)
        self.cx += dx
        self.cy += dy

#    @property
#    def dxfdata(self):
#        lines = ['  0', 'ARC', '  8', 'snijlijnen', ' 10', str(self.cx),
#                 ' 20', str(self.cy), ' 30', '0.0', ' 40', str(self.R),
#                 ' 50', str(self.a[0]), ' 51', str(self.a[1])]
#        return lines

    @property
    def length(self):
        angle = math.radians(self.a[1]-self.a[0])
        return self.R*angle

