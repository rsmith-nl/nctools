# -*- coding: utf-8 -*-
#
# Copyright © 2011,2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

"""Converts lines and arcs from a DXF file and organizes them into 
contours."""

__version__ = '$Revision$'[11:-2]

import math


# Class definitions
class Entity:
    """A base class for a DXF entities.

    The class attribute delta contains the maximum distance in x and y
    direction between eindpoints that are considered coincident.
    """
    delta = 0.005
    _anoent = "Argument is not an entity!"

    def __init__(self, x1=0, y1=0, x2=0, y2=0, index=None):
        """Creates an Entity from (x1, y1) to (x2, y2).
        
        :x1, y1: start point of the entity
        :x2, y2: end point of the entity
        """
        # Start- and enpoint
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
        # Bounding box
        self.xmin = min(self.x1, self.x2)
        self.ymin = min(self.y1, self.y2)
        self.xmax = max(self.x1, self.x2)
        self.ymax = max(self.y1, self.y2)
        # Endpoints swapped indicator
        self.sw = False
        # index in the DXF file
        self.index = index

    def fits(self, index, other):
        """Checks if another entity fits onto this one.

        :index: end of the entity to test, either 1 or 2
        :other: entity to test
        :returns: 0 if the other entity doesn't fit. Otherwise returns 1 or 2
                  indicating the new free end of other.
        """
        assert isinstance(other, Entity), Entity._anoent
        if index == 1:
            if (math.fabs(self.x1-other.x1) < Entity.delta and 
                math.fabs(self.y1-other.y1) < Entity.delta):
                # return free end of other
                return 2
            elif (math.fabs(self.x1-other.x2) < Entity.delta and 
                  math.fabs(self.y1-other.y2) < Entity.delta):
                return 1
        elif index == 2:
            if (math.fabs(self.x2-other.x1) < Entity.delta and 
                math.fabs(self.y2-other.y1) < Entity.delta):
                return 2
            elif (math.fabs(self.x2-other.x2) < Entity.delta and 
                  math.fabs(self.y2-other.y2) < Entity.delta):
                return 1
        return 0 # doesn't fit!

    def getbb(self):
        """Returns a tuple containing the bounding box of an entity in the
        format (xmin, ymin, xmax, ymax).
        """
        return (self.xmin, self.ymin, self.xmax, self.ymax)

    def move(self, dx, dy):
        """Move the entity.
        
        :dx: movement in the x direction
        :dy: movement in the y direction
        """
        self.x1 += dx
        self.x2 += dx
        self.xmin += dx
        self.xmax += dx
        self.y1 += dy
        self.y2 += dy
        self.ymin += dy
        self.ymax += dy

    def swap(self):
        """Swap (x1, y1) and (x2, y2)"""
        (self.x1, self.x2) = (self.x2, self.x1)
        (self.y1, self.y2) = (self.y2, self.y1)
        self.sw = not self.sw

    def dxfdata(self):
        """Returns a string containing the entity in DXF format."""
        raise NotImplementedError

    def pdfdata(self):
        """Returns info to create the entity in PDF format."""
        raise NotImplementedError

    def ncdata(self):
        """Returns NC data for the entity. This is a 2-tuple of two
        strings. The first string decribes how to go to the beginning of the
        entity, the second string contains the entity itself.
        """
        raise NotImplementedError

    def length(self):
        """Returns the length of the entity."""
        raise NotImplementedError

    @property
    def startpoint(self):
        """Returns (x1, y1) of the entity."""
        return (self.x1, self.y1)

    @property
    def endpoint(self):
        """Returns (x2, y2) of the entity"""
        return (self.x2, self.y2)

    def __lt__(self, other):
        """The (xmax, ymin) corner of the bounding box will be used for
        sorting. Sort by xmin in descending order first, then ymin in
        ascending order."""
        if self.xmax == other.xmax:
            return self.ymin < other.ymin
        else:
            return self.xmax > other.xmax

    def __gt__(self, other):
        if self.xmax == other.xmax:
            return self.ymin > other.ymin
        else:
            return self.xmax < other.xmax

    def __eq__(self, other):
        return self.xmax == other.xmas and self.ymin == other.ymin


class Line(Entity):
    """A class for a line entity, from point (x1, y1) to (x2, y2)"""

    def __init__(self, x1, y1, x2, y2, index):
        """Creates a Line from (x1, y1) to (x2, y2)."""
        Entity.__init__(self, x1, y1, x2, y2, index)

    def __str__(self):
        fs = "#LINE from ({:.3f},{:.3f}) to ({:.3f},{:.3f}), index {}"
        fs =  fs.format(self.x1, self.y1, self.x2, self.y2, self.index)
        if self.sw:
            fs += " (swapped)"
        return fs

    def dxfdata(self):
        lines = ['  0', 'LINE', '  8', 'snijlijnen', ' 10', str(self.x1),
                 ' 20', str(self.y1), ' 30', '0.0', ' 11', str(self.x2),
                 ' 21', str(self.y2), ' 31', '0.0', '']
        # empty string for adding a last newline with the join.
        return '\n'.join(lines)
        
    def pdfdata(self):
        """Returns a tuple containing the coordinates x1, y1, x2 and y2."""
        return ((self.x1, self.y1), (self.x2, self.y2))

    def ncdata(self):
        """NC code for an individual line in a 2-tuple; (goto, lineto)
        M15 = knife up, M14 = knife down.
        """
        s1 = 'X{}Y{}*'.format(_mmtoci(self.x1), _mmtoci(self.y1))
        s2 = 'M14*X{}Y{}*M15*'.format(_mmtoci(self.x2), _mmtoci(self.y2))
        return (s1, s2)

    def length(self):
        """Returns the length of a Line."""
        dx = self.x2-self.x1
        dy = self.y2-self.x1
        return math.sqrt(dx*dx+dy*dy)


class Polyline(Entity):
    """A class for a polyline entity, consisting if several linked line
    segments.
    """

    def __init__(self, pnts, index):
        self.pnts = pnts
        x1, y1 = pnts[0][0], pnts[0][1]
        x2, y2 = pnts[-1][0], pnts[-1][1]
        Entity.__init__(self, x1, y1, x2, y2, index)
        xvals = [x for x, _ in pnts]
        yvals = [y for _, y in pnts]
        self.xmin = min(xvals)
        self.ymin = min(yvals)
        self.xmax = max(xvals)
        self.ymax = max(yvals)

    def __str__(self):
        s = "#POLYLINE from ({:.3f},{:.3f}) to ({:.3f},{:.3f}), index {}"
        s =  s.format(self.x1, self.y1, self.x2, self.y2, self.index)
        if self.sw:
            s += " (swapped)"
        return s

    def dxfdata(self):
        """Returns a string containing the entity in DXF format."""
        pass

    def pdfdata(self):
        """Returns info to create the entity in PDF format."""
        return self.pnts

    def ncdata(self):
        """Returns NC data for the entity. This is a 2-tuple of two
        strings. The first string decribes how to go to the beginning of the
        entity, the second string contains the entity itself.
        M15 = knife up, M14 = knife down.
        """
        ms = 'X{}Y{}*'
        s1 = ms.format(_mmtoci(self.x1), _mmtoci(self.y1))
        lines = ['M14*']
        lines += [ms.format(_mmtoci(x), _mmtoci(y)) 
                  for x,y in self.pnts[1:]]
        lines += ['M15*']
        s2 = ''.join(lines)
        return (s1, s2)

    def move(self, dx, dy):
        """Move the entity.
        
        :dx: movement in the x direction
        :dy: movement in the y direction
        """
        self.pnts = [(x+dx, y+dy) for x, y in self.pnts]
        Entity.move(self, dx, dy)

    def swap(self):
        self.pnts.reverse()
        Entity.swap(self)

    def length(self):
        """Returns the length of the entity."""
        pass


class Arc(Entity):
    """A class for an arc entity, centering in (cx, cy) with radius R from
    angle a1 to a2.

    Class properties: 

        :Arc.dev: Maximum deviation from the true arc.
        :Arc.as_segments: Whether an arc should be output as a list of
                          connected line segments. True by default.
    """
    dev = 1
    as_segments = True

    def __init__(self, cx, cy, R, a1, a2, index):
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
        self.a1 = float(a1)
        self.a2 = float(a2)
        self.segments = None
        x1 = cx+R*math.cos(math.radians(a1))
        y1 = cy+R*math.sin(math.radians(a1))
        x2 = cx+R*math.cos(math.radians(a2))
        y2 = cy+R*math.sin(math.radians(a2))
        Entity.__init__(self, x1, y1, x2, y2, index)
        # Refine bounding box
        A1 = int(a1)//90
        A2 = int(a2)//90
        for ang in range(A1, A2):
            (px, py) = (cx+R*math.cos(math.radians(90*ang)),
                        cy+R*math.sin(math.radians(90*ang)))
            if px > self.xmax:
                self.xmax = px
            elif px < self.xmin:
                self.xmin = px
            if py > self.ymax:
                self.ymax = py
            elif py < self.ymin:
                self.ymin = py

    def gensegments(self):
        """Subdivide the arc into a list of line segments which deviate
        maximally Arc.dev fromt the true arc. 
        """
        da = self.a2-self.a1
        step = math.degrees(2*math.acos(1-Arc.dev/float(self.R)))
        cnt = da//step + 1
        step = da/cnt
        sa = self.a1
        if self.sw:
            sa = self.a2
            step = -step
        angs = [sa+i*step for i in range(int(cnt)+1)]
        pnts = [(self.cx+self.R*math.cos(math.radians(a)), 
                 self.cy+self.R*math.sin(math.radians(a))) for a in angs]
        llist = []
        for j in range(1, len(pnts)):
            i = j-1
            llist.append(Line(pnts[i][0], pnts[i][1], 
                              pnts[j][0], pnts[j][1], None))
        self.segments = llist

    def __str__(self):
        s = "#ARC from ({:.3f},{:.3f}) to ({:.3f},{:.3f}), radius {:.3f}"
        s += ", index {}"
        s =  s.format(self.x1, self.y1, self.x2, self.y2, self.R, self.index)
        if self.sw:
            s += " (swapped)"
        return s

    def move(self, dx, dy):
        Entity.move(self, dx, dy)
        self.cx += dx
        self.cy += dy
        if self.segments:
            for s in self.segments:
                s.move(dx, dy)

    def dxfdata(self):
        if Arc.as_segments == False:
            lines = ['  0', 'ARC', '  8', 'snijlijnen', ' 10', str(self.cx),
                     ' 20', str(self.cy), ' 30', '0.0', ' 40', str(self.R),
                     ' 50', str(self.a1), ' 51', str(self.a2), '']
            # empty string for adding a last newline with the join.
            return '\n'.join(lines)
        if self.segments == None:
            self.gensegments()
        lines = []
        for sg in self.segments:
            lines.append(sg.dxfdata())
        return ''.join(lines)

    def pdfdata(self):
        """Returns a tuple containing the data to draw an arc.
        (as used by cairo.Context.arc)
        """
        a1 = math.radians(self.a1)
        a2 = math.radians(self.a2)
        return (self.cx, self.cy, self.R, a1, a2)

    def ncdata(self):
        if self.segments == None:
            self.gensegments()
        s1 = 'X{}Y{}*'.format(_mmtoci(self.segments[0].x1),
                              _mmtoci(self.segments[0].y1))
        ls2 = ['M14*'] # start cutting
        for sg in self.segments:
            ls2.append('X{}Y{}*'.format(_mmtoci(sg.x2), _mmtoci(sg.y2)))
        ls2.append('M15*') # stop cutting
        return (s1, ''.join(ls2))

    def length(self):
        """Returns the length of an arc."""
        angle = math.radians(self.a2-self.a1)
        return self.R*angle


class Contour(Entity):
    """A class for a list of connected Entities"""

    def __init__(self, ent):
        """Creates a contour from an initial entity."""
        assert isinstance(ent, Entity), Entity._anoent
        Entity.__init__(self, ent.x1, ent.y1, ent.x2, ent.y2)
        self.ent = [ent]
        self.nument = 1

    def append(self, ent): 
        """Tries to append an entity to the contour, if one of the ends of
        entity matches the end of the last entity.  otherwise False.

        :ent: entity to try and connect
        :returns: True if ent connects, otherwise False.
        """
        assert isinstance(ent, Entity), Entity._anoent
        last = self.ent[-1]
        newfree = last.fits(2, ent)
        if newfree == 0:
            return False
        self.ent.append(ent)
        self.nument += 1
        (self.xmin, self.ymin, 
         self.xmax, self.ymax) = merge_bb(self.getbb(), ent.getbb())
        if newfree == 1:
            ent.swap()
        self.x2 = ent.x2
        self.y2 = ent.y2
        return True

    def prepend(self, ent):
        """Tries to prepent an entity to the contour, if one of the ends of
        entity matches the beginning of the first entity.  otherwise False.

        :ent: entity to try and connect
        :returns: True if ent connects, otherwise False.
        """
        assert isinstance(ent, Entity), Entity._anoent
        first = self.ent[0]
        newfree = first.fits(1, ent)
        if newfree == 0:
            return False
        self.ent.insert(0, ent)
        self.nument += 1
        (self.xmin, self.ymin, 
         self.xmax, self.ymax) = merge_bb(self.getbb(), ent.getbb())
        if newfree == 2:
            ent.swap()
        self.x1 = ent.x1
        self.y1 = ent.y1
        return True

    def __str__(self):
        outstr = "#Contour [boundingbox: {:.3f}, {:.3f}, {:.3f}, {:.3f}]\n"
        outstr = outstr.format(self.xmin, self.ymin, self.xmax, self.ymax)
        for e in self.ent:
            outstr += "#" + str(e) + "\n"
        return outstr[0:-1]

    def dxfdata(self):
        lines = []
        for e in self.ent:
            lines.append(e.dxfdata())
        return ''.join(lines)

    def pdfdata(self):
        rl = [self.ent[0].x1, self.ent[0].y1]
        for e in self.ent:
            rl.append(e.x2, e.y2)
        return rl

    def ncdata(self):
        (s1, s2) = self.ent[0].ncdata()
        es = [e.ncdata()[1] for e in self.ent[1:]]
        s2 += ''.join(es)
        # Remove superfluous knife up/down movements
        sc, ec = 'M14*', 'M15*' # knife down, knife up
        s2 = sc + s2.replace(sc, '').replace(ec, '') + ec
        return (s1, s2)

    def length(self):
        """Returns the length of a contour."""
        il = [e.length() for e in self.ent]
        return sum(il)


# Function definitions.
def _mmtoci(d):
    """Converts dimensions in mm to 1/100 inches."""
    return int(round(float(d)*3.937007874015748))


def merge_bb(a, b):
    """Calculate and return a box that contains a and b.

    :a,b: 4-tuples (xmin, ymin, xmax, ymax)
    :returns: a 4-tuple that envelopes a and b
    """
    xmin = min(a[0], b[0])
    ymin = min(a[1], b[1])
    xmax = max(a[2], b[2])
    ymax = max(a[3], b[3])
    return (xmin, ymin, xmax, ymax)


def _read_entities(name):
    """Reads a DXF file, and return a list of entities as strings.

    :name: name of the DXF file.
    :returns: a list of strings
    """
    dxffile = open(name)
    sdata = [s.strip() for s in dxffile.readlines()]
    dxffile.close()
    soe = sdata.index('ENTITIES')+1
    eoe = sdata.index('ENDSEC', soe)
    entities = sdata[soe:eoe]
    return entities


def _find_entities(ename, el):
    """Searches the list for a named entity. Returns a list of indices for
    that name.

    :ename: name of the entity to search for, e.g. LINE or ARC.
    :el: list of strings froma DXF file.
    :returns: a list of indices where these elements can be found in el
    """
    cnt = el.count(ename)
    if cnt > 0:
        return [x for x in range(len(el)) if el[x] == ename]
    return []


def _line_from_elist(elist, num):
    """Create a Line element from a list of strings from a DXF file.

    :elist: list of strings from a DXF file.
    :num: index where to start looking
    :returns: a Line object
    """
    num = elist.index("10", num) + 1
    x1 = float(elist[num])
    num = elist.index("20", num) + 1
    y1 = float(elist[num])
    num = elist.index("11", num) + 1
    x2 = float(elist[num])
    num = elist.index("21", num) + 1
    y2 = float(elist[num])
    return Line(x1, y1, x2, y2, num)


def _arc_from_elist(elist, num):
    """Create an Arc element from a list of strings from a DXF file.

    :elist: list of strings from a DXF file.
    :num: index where to start looking
    :returns: an Arc object
    """
    num = elist.index("10", num) + 1
    cx = float(elist[num])
    num = elist.index("20", num) + 1
    cy = float(elist[num])
    num = elist.index("40", num) + 1
    R = float(elist[num])
    num = elist.index("50", num) + 1
    a1 = float(elist[num])
    num = elist.index("51", num) + 1
    a2 = float(elist[num])
    if a2 < a1:
        a2 += 360.0
    return Arc(cx, cy, R, a1, a2, num)


def _polyline_from_elist(elist, num):
    """Create a Polyline object from a list of strings from a DXF file.

    :elist: list of strings from a DXF file.
    :num: index where to start looking
    :returns: a Polyline object
    """
    start = num
    end = elist.index('SEQEND', num)
    points = []
    v = 'VERTEX'
    num = elist.index(v, num)
    while num < end:
        try:
            num = elist.index("10", num) + 1
            x = float(elist[num])
            num = elist.index("20", num) + 1
            y = float(elist[num])
            points.append((x, y))
            num = elist.index(v, num)
        except ValueError: # item not in list
            break
    return Polyline(points, start)


def fromfile(fname):
    """Extracts LINE and ARC entities from a DXF file

    :fname: name of the file to read
    :returns: a list of Entities
    """
    ent = _read_entities(fname)
    lo = _find_entities("LINE", ent)
    lines = []
    if len(lo) > 0:
        lines = [_line_from_elist(ent, n) for n in lo]
    ao = _find_entities("ARC", ent)
    arcs = []
    if len(ao) > 0:
        arcs = [_arc_from_elist(ent, m) for m in ao]
    polys = []
    po = _find_entities("POLYLINE", ent)
    if len(po) > 0:
        polys = [_polyline_from_elist(ent, m) for m in po]
    entities = lines + arcs + polys
    entities.sort(key=lambda x: x.index)
    return entities


def find_contours(elements):
    """Find polylines in the list of lines and list of arcs. 

    :elements: list of Entities
    :returns: a list of Contours and a list of remaining Entities as a tuple.
    """
    rement = []
    loc = []
    while len(elements) > 0:
        first = elements.pop(0)
        cn = Contour(first)
        oldlen = cn.nument
        while True:
            n = 0
            while n < len(elements):
                if cn.append(elements[n]) or cn.prepend(elements[n]):
                    del elements[n]
                else:
                    n += 1
            if cn.nument == oldlen:
                break
            oldlen = cn.nument
        if cn.nument > 1:
            loc.append(cn)
        else:
            rement.append(first)
    return (loc, rement)
