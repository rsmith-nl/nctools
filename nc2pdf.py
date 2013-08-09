#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Plot cuts from a Gerber cloth cutter NC file to a PDF."""

import argparse
import sys
import cairo
from nctools import gerbernc, plot, utils

__proginfo__ = ('nc2pdf [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def getcuts(rd):
    """Make a list of cuts

    :rd: nctools.gerbernc.Reader object
    :returns: list of (x,y) tuples representing the cuts.
    """
    cuts = []
    x = []
    y = []
    section = None
    cutting = False
    pos = None
    for c, args in rd:
        if c.startswith('down'):
            cutting = True
            if not pos:
                raise ValueError('Start of cutting without pos')
            section = [pos]
        elif c.startswith('up'):
            cutting = False
            if section:
                cuts.append(section)
            section = None
        elif c.startswith('moveto'):
            _, newpos = args
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', 
                        version=__proginfo__)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    offset = 40
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for fn in utils.xpand(pv.files):
        try:
            ofn = utils.outname(fn, extension='.pdf', addenum='_nc')
            rd = gerbernc.Reader(fn)
        except ValueError as e:
            print e
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(fn)
            continue
        except IOError as e:
            print "Cannot read file: {}".format(e)
            print "Skipping file '{}'".format(fn)
            continue
        cuts, xvals, yvals = getcuts(rd)
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
    main(sys.argv[1:])
