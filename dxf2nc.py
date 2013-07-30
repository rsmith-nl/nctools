#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Converts a DXF file to a cutting program for a Gerber cloth cutter."""

import argparse
import sys 
from nctools import bbox, dxf, ent, gerbernc, utils

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


def write_entities(fn, ents, alim):
    """@todo: Docstring for write_entities

    :fn: output file name
    :ents: list of entities
    :alim: minimum turning angle where the knife needs to be lifted
    :returns: @todo

    """
    with gerbernc.Writer(fn, anglim=alim) as w:
        for e in ents:
            if isinstance(e, ent.Contour):
                _cutcontour(e, w)
            elif isinstance(e, ent.Polyline):
                _cutpoly(e, w)
            elif isinstance(e, ent.Arc):
                _cutarc(e, w)
            elif isinstance(e, ent.Line):
                _cutline(e, w)


def main(argv):
    """Main program for the dxf2nc utility.
    
    :argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when 
    searching for contours (defaults to 0.5 mm)"""
    argtxt2 = u"""minimum rotation angle in degrees where the knife needs 
    to be lifted to prevent breaking (defaults to 60°)"""
    parser.add_argument('-l', '--limit', help=argtxt, dest='limit',
                       metavar='F', type=float, default=0.5)
    parser.add_argument('-a', '--angle', help=argtxt2, dest='ang',
                       metavar='F', type=float, default=60)
    parser.add_argument('-v', '--version', action='version', 
                        version=__proginfo__)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    lim = pv.limit**2
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        try:
            ofn = utils.outname(f, extension='')
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
            contours, rement = ent.findcontours(entities, lim)
            ncon = 'Found {} contours, {} remaining single entities'
            print ncon.format(len(contours), len(rement))
            entities = contours + rement
            entities.sort(key=lambda x: x.bbox.minx)
        else:
            print 'Contains: 1 entity'
            bb = entities[0].bbox
        es = 'Original extents: {:.1f} ≤ x ≤ {:.1f} mm,' \
             ' {:.1f} ≤ y ≤ {:.1f} mm'
        print es.format(bb.minx, bb.maxx, bb.miny, bb.maxy)
        # move entities so that the bounding box begins at 0,0
        if bb.minx != 0 or bb.miny != 0:
            ms = 'Moving all entities by ({:.1f}, {:.1f}) mm'
            print ms.format(-bb.minx, -bb.miny)
            for e in entities:
                e.move(-bb.minx, -bb.miny)
        length = sum(e.length for e in entities)
        print 'Total length of entities: {:.0f} mm'.format(length)
        write_entities(ofn, entities, pv.ang)

if __name__ == '__main__':
    main(sys.argv[1:])
