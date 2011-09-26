#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and prints them.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-09-26 17:49:15 rsmith>
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

import sys # for argv.
import math


# Class definitions

delta=0.01

class DxfEntity:
    '''A class for a line or arc entities'''
    def __init__(self):
        self.xmin = 0.0
        self.xmax = 0.0
        self.xmax = 0.0
        self.xmax = 0.0
    def boundingbox(self):
        return (xmin, ymin, xmax, ymax)

class DxfLine(DxfEntity):
    '''A class for a line entity, from point (x1,y1) to (x2,y2)'''
    def __init__(self, elist, num):
        '''Creates a DxfLine by searching the elist entities list starting from
 the number num.'''
        num = elist.index("10", num) + 1
        self.x1 = float(elist[num])
        num = elist.index("20", num) + 1
        self.y1 = float(elist[num])
        num = elist.index("11", num) + 1
        self.x2 = float(elist[num])
        num = elist.index("21", num) + 1
        self.y2 = float(elist[num])
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
    def swap(self):
        '''Swap (x1,y1) and (x2,y2)'''
        tx = self.x1
        ty = self.y1
        self.x1 = self.x2
        self.y1 = self.y2
        self.x2 = tx
        self.y2 = ty
    def __str__(self):
        return "LINE from ({},{}) to ({},{})".format(self.x1, self.y1, 
                                                    self.x2, self.y2)

class DxfArc(DxfEntity):
    '''A class for an arc entity, centering in (cx,cy) with radius R from angle
 a1 to a2'''
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
        self.x1 = self.cx+self.R*math.cos(math.radians(self.a1))
        self.y1 = self.cy+self.R*math.sin(math.radians(self.a1))
        self.x2 = self.cx+self.R*math.cos(math.radians(self.a2))
        self.y2 = self.cy+self.R*math.sin(math.radians(self.a2))
        # TODO: bounding-box calculation
    def startpoint(self):
        return (self.x1,self.y1)
    def endpoint(self):
        return (self.x2,self.y2)
    def __str__(self):
        s = "ARC center ({},{}), radius {} from {} to {} degrees"
        return s.format(self.cx, self.cy, self.R, self.a1, self.a2)

class DxfPolyLine(DxfEntity):
    '''A class for a poly line entity, from point (x1,y1) to (xn,yn)'''
    def __init__(self, line):
        '''Creates a polyline from an initial line segment.'''
        self.points = [(line.x1,line.y1), (line.x2, line.y2)]
        self.numpoints = 2
    def append(self, line):
        '''Appends line to the polyline, if one of the ends of line matches
        the end of the polyline. Returns True if matched, otherwise False.'''
        endpoint = self.points[-1]
        if math.fabs(endpoint[0]-line.x1)<delta and math.fabs(endpoint[1]-line.y1)<delta:
            self.points.append((line.x2,line.y2))
            self.numpoints+=1
            return True
        if math.fabs(endpoint[0]-line.x2)<delta and math.fabs(endpoint[1]-line.y2)<delta:
            self.points.append((line.x1,line.y1))
            self.numpoints+=1
            return True
        return False
    def prepend(self, line):
        '''Prepends line to the polyline, if one of the ends of line matches
        the start of the polyline. Returns True if matched, otherwise False.'''
        endpoint = self.points[0]
        if math.fabs(endpoint[0]-line.x1)<delta and math.fabs(endpoint[1]-line.y1)<delta:
            self.points.insert(0, (line.x2,line.y2))
            self.numpoints+=1
            return True
        if math.fabs(endpoint[0]-line.x2)<delta and math.fabs(endpoint[1]-line.y2)<delta:
            self.points.insert(0, (line.x1,line.y1))
            self.numpoints+=1
            return True
        return False
    def __str__(self):
        outstr = "#Polyline\n"
        for n in range(0,self.numpoints-1):
            outstr +=  "|LINE from ({},{}) to ({},{})\n".format(self.points[n][0], 
                                                                self.points[n][1], self.points[n+1][0], 
                                                                self.points[n+1][1])
        return outstr[0:-1]

# Function definitions.

def opendxf(name):
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

def findent(ename, ent):
    '''Searches the ent list for the entity named in the ename string. Returns a list of indices.'''
    cnt = ent.count(ename)
    if cnt > 0:
        return [x for x in range(len(ent)) if ent[x] == ename]
    return []

def findpolylines(lol):
    '''Find polylines in the list of lines lol. Returns a list of polylines
    and a list of remaining lines as a tuple.'''
    lines = lol[:]
    rl = []
    lop = []
    while len(lines) > 0:
        first = lines.pop(0)
        pl = DxfPolyLine(first)
        n = 0
        while n < len(lines):
            if pl.append(lines[n]) or pl.prepend(lines[n]):
                lines.pop(n)
            else:
                n += 1
        if pl.numpoints < 3:
            rl.append(first)
        else:
            lop.append(pl)
            #print "# Found polyline of {} points.".format(pl.numpoints)
    return (rl,lop)

# Main program starts here.
if len(sys.argv) == 1:
    print "Usage: {} dxf-file(s)".format(sys.argv[0])
    exit(1)

del sys.argv[0]
for f in sys.argv:
    # Find entities
    ent = opendxf(f)
    lo = findent("LINE", ent)
    lines = []
    if len(lo) > 0:
        lines = [DxfLine(ent,n) for n in lo] 
    ao = findent("ARC", ent)
    arcs = []
    if len(ao) > 0:
        arcs = [DxfArc(ent,m) for m in ao]
    # Find polylines
    (remlines,polylines) = findpolylines(lines)
    # Output
    for p in polylines:
        print p
    for l in remlines:
        print l
    for a in arcs:
        print a
