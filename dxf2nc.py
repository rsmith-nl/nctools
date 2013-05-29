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
import os.path
import dxfgeom


__proginfo__ = ('dxf2nc [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def nc_header(progname, bbox):
    """Returns the start of the NC file.
    
    :progname: name of the program
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


def newname(oldpath):
    """Create the output filename from the input filename.
    
    :oldpath: path of the input file
    :returns: name of the output file
    """
    oldbase = os.path.splitext(os.path.basename(oldpath))[0]
    if oldbase.startswith('.') or oldbase.isspace():
        raise ValueError("Invalid file name!")
    rv = oldbase + '.nc'
    return rv

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
            outname = newname(f)
            # Find entities
            (lines, arcs) = dxfgeom.fromfile(f)
        except ValueError:
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(f)
            print "A valid filename _must_ have a '.dxf' extension."
            print "And it must be more than just the extension."
            continue
        except IOError:
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        if len(lines) == 0 and len(arcs) == 0:
            print "No lines or arcs found. Skipping file '{}'".format(f)
            continue
        print 'Found {} lines, {} arcs.'.format(len(lines), len(arcs))
        # Move bounding box of entities to 0,0.
        bbs = [ln.getbb() for ln in lines]
        bbs += [a.getbb() for a in arcs]
        bb = bbs[0]
        for add in bbs[1:]:
            bb = dxfgeom.merge_bb(bb, add)
        dispx = -bb[0]
        dispy = -bb[1]
        for ln in lines:
            ln.move(dispx, dispy)
        for a in arcs:
            a.move(dispx, dispy)
        # Find contours
        print 'Looking for contours...'
        (contours, remlines, remarcs) = dxfgeom.find_contours(lines, arcs)
        print 'Found {} contours.'.format(len(contours))
        print '{} unconnected lines and {} arcs remain'.format(len(remlines),
                len(remarcs))
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


if __name__ == '__main__':
    main(sys.argv)
