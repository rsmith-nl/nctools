#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# outputs G-codes for the Gerber cutter..
#
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2012-04-16 22:59:14 rsmith>
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
import os.path

# Local module.
import dxfgeom

ver = "dxf2nc [revision VERSION] (DATE)"

def nc_header(progname, bbox):
    '''Returns the start of the NC file.'''
    Li = (bbox[2]-bbox[0])/25.4
    Wi = (bbox[3]-bbox[1])/25.4
    s = "H1*M20*{}/L={:5.3f}/W={:5.3f}*N1*".format(progname, Li, Wi)
    return s

def nc_footer():
    '''Returns the ending of the NC file.'''
    return 'M0*'

def newname(oldpath):
    '''Write the header of the NC file.'''
    oldname = os.path.basename(oldpath)
    if not oldname.endswith(('.dxf', '.DXF')):
        raise ValueError('not a DXF file!')
    oldbase = oldname[:-4]
    if len(oldbase) == 0:
        raise ValueError("zero-length file name!")
    rv = oldbase + '.nc'
    return rv

# Main program starts here.
if len(sys.argv) == 1:
    print ver
    print "Usage: {} [file.dxf ...]".format(sys.argv[0])
    exit(1)
del sys.argv[0]
for f in sys.argv:
    try:
        outname = newname(f)
        ent = dxfgeom.read_entities(f)
    except ValueError:
        print "Cannot construct output filename. Skipping file '{}'.".format(f)
        print "A valid filename _must_ have a '.dxf' extension."
        print "And it must be more than just the extension."
        continue
    except IOError:
        print "Cannot open the file '{}'. Skipping it.".format(f)
        continue
    # Find entities
    lo = dxfgeom.find_entities("LINE", ent)
    lines = []
    if len(lo) > 0:
        lines = [dxfgeom.line_from_elist(ent, nn) for nn in lo]
    ao = dxfgeom.find_entities("ARC", ent)
    arcs = []
    if len(ao) > 0:
        arcs = [dxfgeom.arc_from_elist(ent, m) for m in ao]
    # TODO: Find bounding box.
    bbs = [ln.getbb() for ln in lines]
    bbs += [a.getbb() for a in arcs]
    bb = bbs[0]
    for add in bbs[1:]:
        bb = dxfgeom.merge_bb(bb, add)
    # TODO: Translate all elements so that bounding box starts at 0,0.
    dispx = -bb[0]
    dispy = -bb[1]
    for ln in lines:
        ln.move(dispx, dispy)
    for a in arcs:
        a.move(dispx, dispy)
    # Find contours
    (contours, remlines, remarcs) = dxfgeom.find_contours(lines, arcs)
    # Sort in y1, then in x1.
    contours.sort()
    remlines.sort()
    remarcs.sort()
    # Output
    outf = open(outname, 'w')
    outf.write(nc_header(outname[:-3], bb))
    for cn in contours:
        s1, s2 = cn.ncdata()
        outf.write(s1+s2)
    for l in remlines:
        s1, s2 = l.ncdata()
        outf.write(s1+s2)
    for a in remarcs:
        s1, s2 = a.ncdata()
        outf.write(s1+s2)
    outf.write(nc_footer())
    outf.close()
