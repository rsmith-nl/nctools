#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# outputs G-codes for the Gerber cutter..
#
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

import sys
import nctools.dxfgeom as dxfgeom
from nctools.fileutils import outname

__proginfo__ = ('dxf2nc [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def nc_header(progname, bbox):
    """Returns the start of the NC file.
    
    :progname: name of the file
    :bbox: 4-tuple (xmin, ymin, xmax, ymax) in mm
    :returns: a string containing the header for the nc file. 
    """
    Li = (bbox[2]-bbox[0])/25.4
    Wi = (bbox[3]-bbox[1])/25.4
    s = "H1*M20*{}/L={:5.3f}/W={:5.3f}*N1*M15*".format(progname, Li, Wi)
    return s


def nc_footer():
    """Returns the ending of the NC file."""
    return 'M0*'


def main(argv): #pylint: disable=R0912
    """Main program for the dxf2nc utility.

    :argv: command line arguments
    """    
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} [file.dxf ...]".format(argv[0])
        exit(1)
    del argv[0]
    for f in argv:
        try:
            ofn = outname(f, extension='.nc')
            # Find entities
            entities = dxfgeom.fromfile(f)
        except ValueError:
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(f)
            print "A valid filename _must_ have a '.dxf' extension."
            print "And it must be more than just the extension."
            continue
        except IOError:
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        if len(entities) == 0:
            print "No lines or arcs found. Skipping file '{}'".format(f)
            continue
        print 'Found {} entities.'.format(len(entities))
        # Move bounding box of entities to 0,0.
        bbs = [e.getbb() for e in entities]
        bb = bbs[0]
        for add in bbs[1:]:
            bb = dxfgeom.merge_bb(bb, add)
        dispx = -bb[0]
        dispy = -bb[1]
        for e in entities:
            e.move(dispx, dispy)
        # Find contours
        print 'Looking for contours...'
        (contours, rement) = dxfgeom.find_contours(entities)
        print 'Found {} contours.'.format(len(contours))
        print '{} entities remain'.format(len(rement))
        entities = contours + rement
        entities.sort()
        # Output
        outf = open(ofn, 'w')
        outf.write(nc_header(ofn[:-3], bb))
        for e in entities:
            s1, s2 = e.ncdata()
            outf.write(s1+s2)
        outf.write(nc_footer())
        outf.close()


if __name__ == '__main__':
    main(sys.argv)
