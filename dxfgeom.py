# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and organizes them into contours.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-09-27 22:16:19 rsmith>
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

import math

# Constants
DxfDelta=0.01

# Class definitions
class DxfEntity:
    '''A base class for a DXF entities; lines and arcs.'''
    def __init__(self):
        # Start- and enpoint
        self.x1 = self.x2 = 0.0
        self.y1 = self.y2 = 0.0
        # Bounding box
        self.xmin = self.xmax = 0.0
        self.xmax = self.xmax = 0.0
        self.sw = False
    def fits(self, index, other):
        if not isinstance(other, DxfEntity):
            print "{} is not a DxfEntity!".format(other)
            return 0
        if index == 1:
            if (math.fabs(self.x1-other.x1)<DxfDelta and 
                math.fabs(self.y1-other.y1)<DxfDelta):
                # return free end of other
                return 2
            elif (math.fabs(self.x1-other.x2)<DxfDelta and 
                  math.fabs(self.y1-other.y2)<DxfDelta):
                return 1
        elif index == 2:
            if (math.fabs(self.x2-other.x1)<DxfDelta and 
                math.fabs(self.y2-other.y1)<DxfDelta):
                return 2
            elif (math.fabs(self.x2-other.x2)<DxfDelta and 
                  math.fabs(self.y2-other.y2)<DxfDelta):
                return 1
        return 0 # doesn't fit!
    def getbb(self):
        return (self.xmin, self.ymin, self.xmax, self.ymax)
    def swap(self):
        '''Swap (x1,y1) and (x2,y2)'''
        (self.x1, self.x2) = (self.x2, self.x1)
        (self.y1, self.y2) = (self.y2, self.y1)
        self.sw = not self.sw
    def __lt__(self, other):
        '''The (xmin,ymin) corner of the bounding box will be used for sorting.'''
        if self.xmin == other.xmin:
            if self.ymin < other.ymin:
                return True
        else:
            return self.xmin < other.xmin
    def __gt__(self, other):
        if self.xmin == other.xmin:
            if self.ymin > other.ymin:
                return True
        else:
            return self.xmin > other.xmin
    def __eq__(self, other):
        return self.xmin == other.xmin and self.ymin == other.ymin

class DxfLine(DxfEntity):
    '''A class for a line entity, from point (x1,y1) to (x2,y2)'''
    def __init__(self, elist, num):
        '''Creates a DxfLine by searching the elist entities list starting
        from the number num.'''
        num = elist.index("10", num) + 1
        self.x1 = float(elist[num])
        num = elist.index("20", num) + 1
        self.y1 = float(elist[num])
        num = elist.index("11", num) + 1
        self.x2 = float(elist[num])
        num = elist.index("21", num) + 1
        self.y2 = float(elist[num])
        self.sw = False
        # Set bounding box
        if self.x2 > self.x1:
            self.xmin = self.x1
            self.xmax = self.x2
        else:
            self.xmin = self.x2
            self.xmax = self.x1
        if self.y2 > self.y1:
            self.ymin = self.y1
            self.ymax = self.y2
        else:
            self.ymin = self.y2
            self.ymax = self.y1
    def __str__(self):
        fs = "LINE from ({:.3f},{:.3f}) to ({:.3f},{:.3f})"
        fs =  fs.format(self.x1, self.y1, self.x2, self.y2)
        if self.sw == True:
            fs += " (swapped)"
        return fs

class DxfArc(DxfEntity):
    '''A class for an arc entity, centering in (cx,cy) with radius R from
    angle a1 to a2'''
    def __init__(self, elist, num):
        '''Creates a DxfArc by searching the elist entities list starting from
        the number num.'''
        num = elist.index("10", num) + 1
        self.cx = float(elist[num])
        num = elist.index("20", num) + 1
        self.cy = float(elist[num])
        num = elist.index("40", num) + 1
        self.R = float(elist[num])
        num = elist.index("50", num) + 1
        self.a1 = float(elist[num])
        num = elist.index("51", num) + 1
        self.a2 = float(elist[num])
        if self.a2 < self.a1:
            self.a2 += 360.0
        # Start and endpoint 
        self.x1 = self.xmin = self.cx+self.R*math.cos(math.radians(self.a1))
        self.y1 = self.ymin = self.cy+self.R*math.sin(math.radians(self.a1))
        self.x2 = self.xmax = self.cx+self.R*math.cos(math.radians(self.a2))
        self.y2 = self.ymax = self.cy+self.R*math.sin(math.radians(self.a2))
        self.sw = False
        # Refine bounding box
        if self.xmin > self.xmax:
            (self.xmin,self.xmax) = (self.xmax,self.xmin)
        if self.ymin > self.ymax:
            (self.ymin,self.ymax) = (self.ymax,self.ymin)
        A1 = int(self.a1)/90
        A2 = int(self.a2)/90
        for ang in range(A1,A2):
            (px,py) = (self.cx+self.R*math.cos(math.radians(90*ang)),
                       self.cy+self.R*math.sin(math.radians(90*ang)))
            if px > self.xmax:
                self.xmax = px
            elif px < self.xmin:
                self.xmin = px
            if py > self.ymax:
                self.ymax = py
            elif py < self.ymin:
                self.ymin = py
    def startpoint(self):
        return (self.x1,self.y1)
    def endpoint(self):
        return (self.x2,self.y2)
    def __str__(self):
        s = "ARC from ({:.3f},{:.3f}) to ({:.3f},{:.3f}), radius {:.3f}"
        s =  s.format(self.x1, self.y1, self.x2, self.y2, self.R)
        if self.sw == True:
            s += " (swapped)"
        return s

class DxfContour(DxfEntity):
    '''A class for a list of connected DxfEntities'''
    def __init__(self, ent):
        '''Creates a contour from an initial entity.'''
        self.ent = [ent]
        self.nument = 1
        (self.xmin, self.ymin, self.xmax, self.ymax) = ent.getbb()
        (self.x1, self.y1, self.x2, self.y2) = (ent.x1, ent.y1, ent.x2, ent.y2)
    def append(self, ent):
        '''Appends and entity to the contour, if one of the ends of entity
        matches the end of the last entity. Returns True if matched, otherwise
        False.'''
        last = self.ent[-1]
        newfree = last.fits(2, ent)
        if newfree == 0:
            return False
        self.ent.append(ent)
        self.nument += 1
        (self.xmin, self.ymin, 
         self.xmax, self.ymax) = DxfMergebb(self.getbb(), ent.getbb())
        if newfree == 1:
            ent.swap()
        self.x2 = ent.x2
        self.y2 = ent.y2
        return True
    def prepend(self, ent):
        '''Prepends and entity to the contour, if one of the ends of entity
        matches the end of the first entity. Returns True if matched,
        otherwise False.'''
        first = self.ent[0]
        newfree = first.fits(1, ent)
        if newfree == 0:
            return False
        self.ent.insert(0,ent)
        self.nument += 1
        (self.xmin, self.ymin, 
         self.xmax, self.ymax) = DxfMergebb(self.getbb(), ent.getbb())
        if newfree == 2:
            ent.swap()
        self.x1 = ent.x1
        self.y1 = ent.y1
        return True
    def __str__(self):
        outstr = "#Contour ({}, {}, {}, {})\n"
        outstr = outstr.format(self.xmin, self.ymin, self.xmax, self.ymax)
        for e in self.ent:
            outstr += "|" + str(e) + "\n"
        return outstr[0:-1]

# Function definitions.
def DxfMergebb(a, b):
    '''The bounding boxes a and b are tuples (xmin, ymin, xmax,
    ymax). Calculate and return a bounding box that contains a and b.'''
    xmin = min(a[0], b[0])
    ymin = min(a[1], b[1])
    xmax = max(a[2], b[2])
    ymax = max(a[3], b[3])
    return (xmin, ymin, xmax, ymax)

def DxfReadEntities(name):
    '''Opens the DXF file 'name', and return a list of entities'''
    dxffile = open(name)
    sdata = [str.strip() for str in dxffile.readlines()]
    dxffile.close()
    soe = sdata.index('ENTITIES')
    sdata = sdata[soe+1:]
    eoe = sdata.index('ENDSEC')
    entities = sdata[:eoe]
    del sdata
    return entities

def DxfFindentities(ename, el):
    '''Searches the ent list for the entity named in the ename string. Returns
    a list of indices.'''
    cnt = el.count(ename)
    if cnt > 0:
        return [x for x in range(len(el)) if el[x] == ename]
    return []

def DxfFindContours(lol, loa):
    '''Find polylines in the list of lines loe and list of arcs loa. Returns a
    list of contours and a list of remaining lines and a list of remaining
    arcs as a tuple.'''
    remlines = []
    remarcs = []
    elements = lol[:]+loa[:]
    loc = []
    while len(elements) > 0:
        first = elements.pop(0)
        cn = DxfContour(first)
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
            if isinstance(first, DxfLine):
                remlines.append(first)
            elif isinstance(first, DxfArc):
                remarcs.append(first)
    return (loc, remlines, remarcs)

