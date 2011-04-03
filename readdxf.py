#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and prints them.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-04-03 17:23:59 rsmith>
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
    '''Searches the ent list for the entity named in the ename string.'''
    cnt = ent.count(ename)
    if cnt > 0:
        return [x for x in range(len(ent)) if ent[x] == ename]

# Class definitions

class DxfLine:
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
    def __str__(self):
        return "LINE from ({},{}) to ({},{})".format(self.x1, self.y1, 
                                                    self.x2, self.y2)

class DxfArc:
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
    def __str__(self):
        s = "ARC center ({},{}), radius {} from {} to {} degrees"
        return s.format(self.cx, self.cy, self.R, self.a1, self.a2)

# Main program starts here.

if len(sys.argv) > 1:
    del sys.argv[0]
    for f in sys.argv:
        ent = opendxf(f)
        lo = findent("LINE", ent)
        lines = [DxfLine(ent,n) for n in lo] 
        ao = findent("ARC", ent)
        arcs = [DxfArc(ent,m) for m in ao]
        for l in lines:
            print l
        for a in arcs:
            print a
else:
    print "Usage {} dxf-file(s)".format(sys.argv[0])
