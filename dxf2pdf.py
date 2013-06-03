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
import os.path
import cairo
import dxfgeom
from wavelentorgb import crange


__proginfo__ = ('dxf2pdf [ver. ' + '$Revision$'[11:-2] +
                '] ('+'$Date$'[7:-2]+')')

def outname(inname):
    """Creates the name of the output filename based on the input filename.

    :inname: name + path of the input file
    :returns: output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if rv.startswith('.') or rv.isspace():
        raise ValueError("Invalid file name!")
    return rv + '_dxf.pdf'


def plotgrid(context, width, height, size=100):
    """@todo: Docstring for plotgrid

    :context: PDF drawing context
    :width: width of the context
    :height: height of the context
    :size: grid cell size
    :returns: @todo

    """
    context.save()
    context.new_path()
    for x in xrange(100, int(width), size):
        context.move_to(x, 0)
        context.line_to(x, height)
    for y in xrange(int(height)-size, 0, -size):
        context.move_to(0, y)
        context.line_to(width, y)
    context.close_path()
    context.set_line_width(0.25)
    context.set_source_rgb(1, 0, 0)
    context.stroke()
    context.restore()

def plotentities(context, offset, entities, colors, lw=0.5):
    """Draw the entities

    :context: PDF drawing context
    :offset: tuple for translating the coordinate system
    :entities: list of entities
    :colors: list of (r,g,b) tuples or one (r,g,b) tuple
    :lw: line width
    :returns: nothing
    """
#    print isinstance(colors, tuple), len(colors)
    if isinstance(colors, tuple) and len(colors) == 3:
        colors = [colors]*len(entities)
    elif len(colors) != len(entities):
        print len(colors), len(entities)
        raise ValueError('the amount of colors should be equal to entities')
    context.save()
    context.set_line_width(lw)
    context.translate(offset[0], offset[1])
    for e, (r, g, b) in zip(entities, colors):
        context.new_path()
        context.set_source_rgb(r/255.0, g/255.0, b/255.0)
        if isinstance(e, dxfgeom.Line): 
            s, x = e.pdfdata()
            context.move_to(*s)
            context.line_to(*x)
        elif isinstance(e, dxfgeom.Arc):
            p = e.pdfdata()
            context.new_sub_path()
            context.arc(*p)
        elif isinstance(e, dxfgeom.Polyline):
            rest = e.pdfdata()
            first = rest.pop(0)
            context.move_to(*first)
            for r in rest:
                context.line_to(*r)
        context.stroke()        
    context.restore()


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
            ofn = outname(f)
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
        plotgrid(ctx, w, h)
        colors = crange(380, 650, len(entities))
        # Plot in colors
        plotentities(ctx, (offset/2-bb[0], offset/2-bb[1]), entities, colors)
        # plot the color bar
        sw = w/float(2*len(entities))
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.set_line_width(sw)
        xs = 5
        for r, g, b in colors:
            ctx.set_source_rgb(r/255.0, g/255.0, b/255.0)
            ctx.move_to(xs, 5)
            ctx.rel_line_to(0, 5)
            ctx.stroke()
            xs += sw
        out.show_page()
        out.finish()


if __name__ == '__main__':
    main(sys.argv)

