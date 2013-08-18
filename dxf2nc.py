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

_proginfo = ('dxf2nc [ver. ' + 
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
    wr.newpiece()


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
            elif isinstance(e, ent.Arc):
                _cutarc(e, w)
            elif isinstance(e, ent.Line):
                _cutline(e, w)
            else:
                raise ValueError('unknown entity')


def splitents(ents, nb, blen):
    """Divide entities in sub-lists for each bite.

    :ents: list of entities, bound at x=0 and y=0
    :nb: number of bites
    :blen: length of a bite
    :returns: modified list of entities
    """
    ec = ents[:]
    borders = [i*blen for i in range(1, nb+1)]
    for b in borders:
        tosplit = [e for e in ec if e.bbox.maxx > b and e.bbox.minx < b]
        for e in tosplit:
            ec.remove(e)
            r = e.hsplit(b)
            for j in r:
                ec.insert(0, j)
    return ec


def main(argv):
    """Main program for the dxf2nc utility.

    :argv: command line arguments
    """
    msg = utils.Msg()
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when 
    searching for contours (defaults to 0.5 mm)"""
    argtxt2 = u"""minimum rotation angle in degrees where the knife needs 
    to be lifted to prevent breaking (defaults to 60°)"""
    argtxt3 = """length of the cutting table that can be cut before the 
    conveyor has to move (defaults to 1000 mm)"""
    parser.add_argument('-l', '--limit', help=argtxt, dest='limit',
                       metavar='F', type=float, default=0.5)
    parser.add_argument('-a', '--angle', help=argtxt2, dest='ang',
                       metavar='F', type=float, default=60)
    parser.add_argument('-b', '--bite', help=argtxt3, dest='bite',
                       metavar='N', type=int, default=1300)
    parser.add_argument('-v', '--version', action='version', 
                        version=_proginfo)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    lim = pv.limit**2
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        msg.say('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='')
            entities = dxf.Reader(f)
        except Exception as e: #pylint: disable=W0703
            utils.skip(e, f)
            continue
        num = len(entities)
        if num == 0:
            msg.say('No entities found!')
            continue
        if num > 1:
            msg.say('Contains {} entities'.format(num))
            bbe = [e.bbox for e in entities]
            bb = bbox.merge(bbe)
            es = 'Original extents: {:.1f} ≤ x ≤ {:.1f} mm,' \
                ' {:.1f} ≤ y ≤ {:.1f} mm'
            msg.say(es.format(bb.minx, bb.maxx, bb.miny, bb.maxy))
            # move entities so that the bounding box begins at 0,0
            if bb.minx != 0 or bb.miny != 0:
                ms = 'Moving all entities by ({:.1f}, {:.1f}) mm'
                msg.say(ms.format(-bb.minx, -bb.miny))
                for e in entities:
                    e.move(-bb.minx, -bb.miny)
            # chop entities in bites
            nbites = int(bb.width//pv.bite + 1)
            bitelen = bb.width/float(nbites)
            if nbites > 1:
                m = 'Cut length divided into {} bites of {} mm'
                msg.say(m.format(nbites, bitelen))
                msg.say('Splitting entities in bites')
                se = splitents(entities, nbites, bitelen)
                msg.say('{} entities after splitting'.format(len(se)))
                entities = []
                ncon = ' '.join(['Bite {}:', 'found {} contours,'
                                '{} remaining entities.'])
                for b in range(1, (nbites+1)):
                    be = [e for e in se if 
                          (b-1)*bitelen < e.bbox.minx < b*bitelen]
                    msg.say('Bite {}, {} entities'.format(b, len(be)))
                    contours, rement = ent.findcontours(be, lim)
                    be = contours + rement
                    msg.say(ncon.format(b, len(contours), len(rement)))
                    #msg.say('Bite {}: sorting entities'.format(b))
                    be.sort(key=lambda e: (e.bbox.minx, e.bbox.miny))
                    entities += se
            else:
                msg.say('Gathering connected entities into contours')
                contours, rement = ent.findcontours(entities, lim)
                ncon = 'Found {} contours, {} remaining single entities'
                msg.say(ncon.format(len(contours), len(rement)))
                entities = contours + rement
                msg.say('Sorting entities')
                entities.sort(key=lambda e: (e.bbox.minx, e.bbox.miny))
        else:
            msg.say('Contains: 1 entity')
            bb = entities[0].bbox
        length = sum(e.length for e in entities)
        msg.say('Total length of entities: {:.0f} mm'.format(length))
        msg.say('Writing output to "{}"'.format(ofn))
        write_entities(ofn, entities, pv.ang)
        msg.say('File "{}" done.'.format(f))

if __name__ == '__main__':
    main(sys.argv[1:])
