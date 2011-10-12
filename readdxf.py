#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and prints them.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-10-12 23:06:20 rsmith>
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
import dxfgeom

# Main program starts here.
if len(sys.argv) == 1:
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
    print "#File: {}".format(f)
    for c in contours:
        print c
    for l in remlines:
        print l
    for a in remarcs:
        print a
