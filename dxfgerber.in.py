#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# output another DXF file.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-10-18 00:13:29 rsmith>
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

# System modules
import sys
import datetime

# Local module.
import dxfgeom

ver = "dxfgerber [revision VERSION] (DATE)"

def DxfHeader(progname, loc, lol, loa):
    '''Write comments at the beginning of a DXF file.'''
    s = "999\nDXF file generated by {}\n".format(progname)
    dt = datetime.datetime.now()
    s += "999\nThis conversion was started on " + dt.strftime("%A, %B %d %H:%M\n")
    c = "999\nThis file contains {} contours, {} loose lines and {} loose arcs.\n"
    s += c.format(len(loc), len(lol), len(loa))
    s += "999\nThe contours are:"
    for n,c in enumerate(contours):
        u = "\n999\n#{} bounding box ({:.3f}, {:.3f}, {:.3f}, {:.3f})"
        s += u.format(n+1, *c.getbb())
    return s

def StartEntities():
    '''Write the beginning of an entities section.'''
    return "  0\nSECTION\n  2\nENTITIES"

def EndEntities():
    '''Write the end of an entities section.'''
    s = "  0\nENDSEC\n  0\nEOF"
    return s

# Main program starts here.
if len(sys.argv) == 1:
    print ver
    print "Usage: {} dxf-file(s)".format(sys.argv[0])
    exit(1)
del sys.argv[0]
for f in sys.argv:
    # Find entities
    ent = dxfgeom.ReadEntities(f)
    lo = dxfgeom.Findentities("LINE", ent)
    lines = []
    if len(lo) > 0:
        lines = [dxfgeom.Linefromelist(ent, n) for n in lo]
    ao = dxfgeom.Findentities("ARC", ent)
    arcs = []
    if len(ao) > 0:
        arcs = [dxfgeom.Arcfromelist(ent, m) for m in ao]
    # Find contours
    (contours, remlines, remarcs) = dxfgeom.FindContours(lines, arcs)
    # Sort in x1, then in y1.
    contours.sort()
    remlines.sort()
    remarcs.sort()
    # Output
    print DxfHeader(ver, contours, remlines, remarcs)
    print StartEntities()
    for c in contours:
        print c.dxfdata(),
    for l in remlines:
        print l.dxfdata(),
    for a in remarcs:
        print a.dxfdata(),
    print EndEntities()
