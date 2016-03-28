# file: plot.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-05-03 20:18:19 +0200
# Last modified: 2016-03-28 16:18:37 +0200
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
# NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Utilities for plotting."""

import datetime
import math
import os
import time
import cairo

__version__ = '2.0.0-beta'


def setup(ofn, minx, miny, maxx, maxy, offset=40):
    """
    Set up the Cairo surface and drawing context.

    Arguments:
        ofn: Name of the file to store the drawing in.
        minx: Left side of the drawing.
        miny: Bottom of the drawing.
        maxx: Right side of the drawing.
        maxy: Top of the drawing.
        offset: Border around the drawing.

    Returns:
        (output surface, drawing context)
    """
    w = (maxx - minx) + 2*offset
    h = (maxy - miny) + 2*offset
    xf = cairo.Matrix(xx=1.0, yy=-1.0, x0=offset-minx, y0=maxy+offset)
    out = cairo.PDFSurface(ofn, w, h)
    ctx = cairo.Context(out)
    ctx.set_matrix(xf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.5)
    return out, ctx


def grid(context, minx, miny, maxx, maxy, spacing=100):
    """
    Plot a 100x100 grid

    Arguments:
        context: Drawing context.
        minx: Left side of the drawing.
        miny: Bottom of the drawing.
        maxx: Right side of the drawing.
        maxy: Top of the drawing.
        spacing: Spacing between grid lines, defaults to 100.
    """
    context.save()
    context.new_path()
    for x in range(int(minx), int(maxx), spacing):
        context.move_to(x, miny)
        context.line_to(x, maxy)
    for y in range(int(miny), int(maxy), spacing):
        context.move_to(minx, y)
        context.line_to(maxx, y)
    context.close_path()
    context.set_line_width(0.1)
    context.set_source_rgb(0.5, 0.5, 0.5)
    context.set_dash([20.0, 20.0])
    context.stroke()
    context.restore()


def lines(context, lines, lw=2, marks=True):
    """
    Plot a list of lines. Each line is a list of 2-tuples (x, y).

    Arguments:
        context: Drawing context.
        lines: Iterator of lines.
        lw: Line width to draw. Defaults to 2.
        marks: Draw start markings. Defaults to True.
    """
    context.save()
    context.set_line_width(lw)
    context.new_path()
    for ln in lines:
        context.move_to(*ln[0])
        for pt in ln[1:]:
            context.line_to(*pt)
    context.stroke()
    context.restore()
    if marks:
        context.save()
        context.set_line_width(lw)
        for ln in lines:
            # Print start mark
            fp, sp = ln[0], ln[1]
            dx, dy = sp[0] - fp[0], sp[1] - fp[1]
            a = math.pi/2 - math.atan2(dx, dy)
            context.save()
            context.set_line_width(1)
            context.translate(*fp)
            context.rotate(a)
            context.new_path()
            context.move_to(-5, 2)
            context.set_source_rgb(0.0, 0.0, 1.0)
            context.line_to(0, 0)
            context.line_to(-5, -2)
            context.move_to(0, 2)
            context.line_to(5, 0)
            context.line_to(0, -2)
            context.stroke()
            context.restore()
            # Print end mark
            fp, sp = ln[-2], ln[-1]
            dx, dy = sp[0] - fp[0], sp[1] - fp[1]
            a = math.pi/2 - math.atan2(dx, dy)
            context.save()
            context.set_line_width(1)
            context.translate(*sp)
            context.rotate(a)
            context.new_path()
            context.move_to(-5, 2)
            context.set_source_rgb(1.0, 0.0, 0.0)
            context.line_to(0, 0)
            context.line_to(-5, -2)
            context.stroke()
            context.restore()
        context.restore()


def title(context, prog, ofn, h, offset=40):
    """
    Write the title on the plot.

    Arguments:
        context: Drawing context.
        prog: Name of the program.
        ofn: Name of the output file.
        h: top of the drawing area
        offset: Border around the drawing.
    """
    context.save()
    context.set_matrix(cairo.Matrix(xx=1.0, yy=1.0))
    context.select_font_face('Sans')
    fh = 10
    context.set_source_rgb(0.0, 0.0, 0.0)
    context.set_font_size(fh)
    context.move_to(5, fh+5)
    txt = ' '.join(['Produced by:', prog, __version__, 'on',
                    str(datetime.datetime.now())[:-10]])
    context.show_text(txt)
    context.stroke()
    context.move_to(5, h+2*offset-(fh))
    txt = 'File: "{}", last modified: {}'
    context.show_text(txt.format(ofn, time.ctime(os.path.getmtime(ofn))))
    context.stroke()
    context.restore()
