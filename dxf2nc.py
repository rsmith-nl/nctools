#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# outputs G-codes for the Gerber cutter.
#
# Copyright © 2012,2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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
import nctools.dxf as dxf
import nctools.ent as ent
import nctools.bbox as bbox
import nctools.utils as utils
import nctools.gerbernc as gerbernc

__proginfo__ = ('dxf2nc [ver. ' + 
                '$Revision$'[11:-2] + '] (' + 
                '$Date$'[7:-2]+')')


def _cutline(e, wr):
    """Cut a ent.Line

    :ent: nctools.ent.Line
    :wr: nctoos.gerbernc.Writer
    """
    wr.moveto(e.x[0], e.y[0])
    wr.down()
    wr.moveto(e.x[1], e.y[1])
    wr.up()


def _cutarc(e, wr):
    """Cut an ent.Arc

    :ent: nctools.ent.Arc
    :wr: nctoos.gerbernc.Writer
    """
    pnts = e.segments()
    x, y = pnts.pop(0)
    wr.moveto(x, y)
    wr.down()
    for x, y in pnts:
        wr.moveto(x, y)
    wr.up()


def _cutpoly(e, wr):
    """Cut a ent.Polyline

    :ent: nctools.ent.Polyline
    :wr: nctoos.gerbernc.Writer
    """
    d = e.segments()
    (xs, ys), _, _ = d[0]
    wr.moveto(xs, ys)
    wr.down()
    for sp, (xe, ye), ang in d:
        if ang == 0.0:
            wr.moveto(xe, ye)
        else:
            (xc, yc), R, a0, a1 = ent.arcdata(sp, (xe, ye), ang)
            if ang > 0:
                ccw = True
            else:
                ccw = False
            a = ent.Arc(xc, yc, R, a0, a1, ccw=ccw)
            pnts = a.segments()
            pnts.pop(0)
            for x, y in pnts:
                wr.moveto(x, y)
    wr.up()


def _cutcontour(e, wr):
    """Cut a ent.Contour

    :ent: nctools.ent.Contour
    :wr: nctoos.gerbernc.Writer
    """
    wr.moveto(e.entities[0].x[0], e.entities[0].y[0])
    wr.down()
    for ce in e.entities:
        if isinstance(ce, ent.Arc):
            pnts = ce.segments()
            pnts.pop(0)
            for x, y in pnts:
                wr.moveto(x, y)
        elif isinstance(ce, ent.Line):
            wr.moveto(ce.x[1], ce.y[1])
    wr.up()


def main(argv):
    """Main program for the dxf2nc utility.
    
    :argv: command line arguments
    """
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} [dxf-file ...]".format(argv[0])
        sys.exit(1)
    del argv[0]
    for f in argv:
        try:
            ofn = utils.outname(f, extension='.nc')
            entities = dxf.Reader(f)
        except Exception as e: #pylint: disable=W0703
            utils.skip(e, f)
            continue
        num = len(entities)
        print 'Filename:', f
        if num == 0:
            print 'No entities found!'
            sys.exit(1)
        if num > 1:
            print 'Contains: {} entities'.format(num)
            bbe = [e.bbox for e in entities]
            bb = bbox.merge(bbe)
            contours, rement = ent.findcontours(entities)
            ncon = 'Found {} contours, {} remaining single entities'
            print ncon.format(len(contours), len(rement))
            entities = contours + rement
        else:
            print 'Contains: 1 entity'
            bb = entities[0].bbox
        es = 'Extents: {:.1f} ≤ x ≤ {:.1f}, {:.1f} ≤ y ≤ {:.1f}'
        print es.format(bb.minx, bb.maxx, bb.miny, bb.maxy)
        length = sum(e.length for e in entities)
        print 'Total length of entities: {:.0f} mm'.format(length)
        with gerbernc.Writer(ofn) as w:
            for e in entities:
                if isinstance(e, ent.Contour):
                    _cutcontour(e, w)
                elif isinstance(e, ent.Polyline):
                    _cutpoly(e, w)
                elif isinstance(e, ent.Arc):
                    _cutarc(e, w)
                elif isinstance(e, ent.Line):
                    _cutline(e, w)

if __name__ == '__main__':
    main(utils.xpand(sys.argv))
