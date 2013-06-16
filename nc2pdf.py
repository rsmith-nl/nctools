#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Plot cut lines to a PDF file. 
#
# Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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
import nctools.plot as plot
from nctools.utils import outname


__proginfo__ = ('nc2pdf [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def parsexy(m):
    """Parse a movement string, return the coordinates in mm.

    :m: movement string
    :returns: A tuple (x,y) of the coordinates in mm
    """
    x, y = m[1:].split('Y')
    # Units are 1/100 inch. Convert to mm. 
    x, y = float(x)*0.254, float(y)*0.254
    return x, y


def getcuts(glist):
    """Make a list of cuts.

    :glist: list of g-code strings
    :returns: nested list of (x,y) tuples representing the cuts 
    """
    cuts = []
    x = []
    y = []
    section = None
    cutting = False
    pos = None
    for g in glist:
        if g == 'M14':
            cutting = True
            if not pos:
                raise ValueError('Start of cutting without pos')
            section = [pos]
        elif g == 'M15':
            cutting = False
            if section:
                cuts.append(section)
            section = []
        elif g.startswith('X'):
            newpos = parsexy(g)
            if cutting:
                section.append(newpos)
            xv, yv = newpos
            x.append(xv)
            y.append(yv)
            pos = newpos
    return cuts, x, y


def main(argv):
    """Main program for the nc2pdf utility.

    :argv: command line arguments
    """
    offset = 40
    if len(argv) == 1:
        print __proginfo__
        print "Usage: nc2pdf.py [file ...]"
        print
        sys.exit(0)
    del argv[0]
    for fn in argv:
        try:
            ofn = outname(fn, extension='.pdf', addenum='_nc')
            with open(fn, 'r') as inf:
                rd = inf.read()
        except ValueError as e:
            print e
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(fn)
            continue
        except IOError as e:
            print "Cannot read file: {}".format(e)
            print "Skipping file '{}'".format(fn)
            continue
        cmds = rd.split('*')
        if len(cmds[-1]) == 0:
            del cmds[-1]
        cuts, xvals, yvals = getcuts(cmds)
        cnt = len(cuts)
        print 'Got {} cuts'.format(cnt)
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = '{} range from {:.1f} mm to {:.1f} mm'
        print bs.format('X', minx, maxx)
        print bs.format('Y', miny, maxy)
        w = maxx - minx + offset
        h = maxy - miny + offset
        # Produce PDF output. Scale factor is 1 mm real = 
        # 1 PostScript point in the PDF file
        xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
        out = cairo.PDFSurface(ofn, w, h)
        ctx = cairo.Context(out)
        ctx.set_matrix(xf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(0.5)
        # Plot a grid in red
        plot.plotgrid(ctx, w, h)
        # Plot the cutlines
        colors = plot.crange(380, 650, cnt)
        # Plot in colors
        ctx.save()
        ctx.translate(offset/2-minx, offset/2-miny)
        for section, (r, g, b) in zip(cuts, colors):
            x1, y1 = section.pop(0)
            ctx.move_to(x1, y1)
            ctx.set_source_rgb(r/255.0, g/255.0, b/255.0)
            for x2, y2 in section:
                ctx.line_to(x2, y2)
            ctx.stroke()
        ctx.restore()
        # plot the color bar
        plot.plotcolorbar(ctx, w, cnt, colors)
        out.show_page()
        out.finish()


if __name__ == '__main__':
    main(sys.argv)
