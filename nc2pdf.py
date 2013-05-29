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
import os.path
import cairo

__proginfo__ = ('nc2pdf [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def outname(inname):
    """Creates the name of the output filename based on the input filename.

    :inname: name + path of the input file
    :returns: output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if len(rv) == 0:
        raise ValueError("zero-length file name!")
    return rv + '.pdf'

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
    :returns: list of nested ((x,y),(x,y)) tuples representing the cuts 
    """
    cuts = []
    cutting = False
    pos = None
    for g in glist:
        if g == 'M14':
            cutting = True
            if not pos:
                raise ValueError('Start of cutting without pos')
        elif g == 'M15':
            cutting = False
        elif g.startswith('X'):
            newpos = parsexy(g)
            if cutting:
                cuts.append((pos, newpos))
            pos = newpos
    return cuts


def main(argv):
    """Main program for the nc2pdf utility.

    :argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print __proginfo__
        print "Usage: {} [file ...]".format(binary)
        print
        sys.exit(0)
    del argv[0]
    for fn in argv:
        try:
            ofn = outname(fn)
            with open(fn, 'r') as inf:
                rd = inf.read()
        except ValueError:
            fns = "Cannot construct output filename. Skipping file '{}'."
            print fns.format(fn)
            continue
        except IOError:
            print "Cannot open the file '{}'. Skipping it.".format(fn)
            continue
        cmds = rd.split('*')
        if len(cmds[-1]) == 0:
            del cmds[-1]
        cuts = getcuts(cmds)
        print 'Got {} cuts'.format(len(cuts))
        xvals = [i for c in cuts for i in (c[0][0], c[1][0])]
        yvals = [i for c in cuts for i in (c[0][1], c[1][1])]
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = '{} range from {:.1f} mm to {:.1f} mm'
        print bs.format('X', minx, maxx)
        print bs.format('Y', miny, maxy)
        w = maxx - minx + 20
        h = maxy - miny + 20
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
        ctx.save()
        ctx.new_path()
        for x in xrange(100, int(w), 100):
            ctx.move_to(x, 0)
            ctx.line_to(x, h)
        for y in xrange(int(h)-100, 0, -100):
            ctx.move_to(0, y)
            ctx.line_to(w, y)
        ctx.close_path()
        ctx.set_line_width(0.25)
        ctx.set_source_rgb(1, 0, 0)
        ctx.stroke()
        ctx.restore()
        # Plot the cutlines in black
        ctx.translate(10-minx, 10-miny)
        ctx.new_path()
        for ((x1, y1), (x2, y2)) in cuts:
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
        ctx.close_path()
        ctx.stroke()
        out.show_page()
        out.finish()



if __name__ == '__main__':
    main(sys.argv)
