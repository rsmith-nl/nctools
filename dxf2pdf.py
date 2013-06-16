#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converts lines and arcs from a DXF file and prints them.
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

import sys 
import cairo
import nctools.dxfgeom as dxfgeom
import nctools.plot as plot
from nctools.utils import outname


__proginfo__ = ('dxf2pdf [ver. ' + '$Revision$'[11:-2] +
                '] ('+'$Date$'[7:-2]+')')

def main(argv): # pylint: disable=R0912
    """Main program for the readdxf utility.
    
    :argv: command line arguments
    """
    offset = 40
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} dxf-file(s)".format(sys.argv[0])
        exit(1)
    del argv[0]
    for f in argv:
        try:
            ofn = outname(f, extension='.pdf', addenum='_dxf')
            entities = dxfgeom.fromfile(f)
        except ValueError as e:
            print e
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(f)
            continue
        except IOError as e:
            print e
            print "Cannot open the file '{}'. Skipping it.".format(f)
            continue
        # Output
        bb = entities[0].getbb()
        for e in entities:
            bb = dxfgeom.merge_bb(bb, e.getbb())
        # bb = xmin, ymin, xmax, ymax
        w = bb[2] - bb[0] + offset
        h = bb[3] - bb[1] + offset
        xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
        out = cairo.PDFSurface(ofn, w, h)
        ctx = cairo.Context(out)
        ctx.set_matrix(xf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(0.5)
        plot.plotgrid(ctx, w, h)
        colors = plot.crange(380, 650, len(entities))
        # Plot in colors
        plot.plotentities(ctx, (offset/2-bb[0], offset/2-bb[1]), 
                          entities, colors)
        # plot the color bar
        plot.plotcolorbar(ctx, w, len(entities), colors)
        out.show_page()
        out.finish()


if __name__ == '__main__':
    main(sys.argv)

