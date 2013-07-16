#! /usr/bin/env python
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS AS IS'' AND
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

"""Test for segmenting arcs"""

import cairo
import nctools.plot as plot
import nctools.ent as ent

__proginfo__ = ('test/segments.py [ver. ' + '$Revision$'[11:-2] +
                '] ('+'$Date$'[7:-2]+')')


def main():
    """Entry point for this script.
    """
    rad = 150
    entities = [ent.Arc(0, 0, rad, 0, 90), ent.Arc(0, 0, rad-1, 0, 90)]
    w = rad
    h = rad
    xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
    out = cairo.PDFSurface('test-segments.pdf', w, h)
    ctx = cairo.Context(out)
    ctx.set_matrix(xf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.5)
    # Draw entities
    plot.plotentities(ctx, (0, 0), entities, (255, 0, 0))
    # Draw segments
    pnts = entities[0].segments()
    x, y = pnts.pop(0)
    ctx.new_path()
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.move_to(x, y)
    for x, y in pnts:
        ctx.line_to(x, y)
    ctx.stroke()


    out.show_page()


if __name__ == '__main__':
    main()


