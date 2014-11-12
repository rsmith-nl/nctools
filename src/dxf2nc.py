# dxf2nc - main program
# vim:fileencoding=utf-8
# $Date$

"""Converts a DXF file to a cutting program for a Gerber cloth cutter."""

from __future__ import print_function, division

__version__ = '$Revision$'[11:-2]

_lic = """dxf2nc {}
Copyright © 2012-2014 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.""".format(__version__)

import argparse
import sys
from nctools import bbox, dxf, ent, gerbernc, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


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


def write_entities(fn, ents, blen, alim):
    """@todo: Docstring for write_entities

    :fn: output file name
    :ents: list of entities
    :blen: length of bites
    :alim: minimum turning angle where the knife needs to be lifted
    :returns: @todo

    """
    with gerbernc.Writer(fn, bitelen=blen, anglim=alim) as w:
        for e in ents:
            if isinstance(e, ent.Contour):
                _cutcontour(e, w)
            elif isinstance(e, ent.Arc):
                _cutarc(e, w)
            elif isinstance(e, ent.Line):
                _cutline(e, w)
            else:
                raise ValueError('unknown entity')


def mkbites(ents, nb, blen):
    """Yield the bite number and the elements in that bite.

    :ents: a list of all entities (this list will be modified).
    :nb: number of bites.
    :blen: length of a bite in mm.
    """
    for b in range(1, nb):
        border = b*blen
        inbite = [e for e in ents if e.bbox.maxx < border]
        crossing = [e for e in ents if e.bbox.minx < border < e.bbox.maxx]
        for e in inbite + crossing:
            ents.remove(e)
        for e in crossing:
            left, right = e.hsplit(border)
            inbite += left
            ents += right
        yield b, inbite
    yield nb, ents


def main(argv):
    """Main program for the dxf2nc utility.

    :argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when
    searching for contours (defaults to 0.5 mm)"""
    argtxt2 = u"""minimum rotation angle in degrees where the knife needs
    to be lifted to prevent breaking (defaults to 60°)"""
    argtxt3 = """length of the cutting table that can be cut before the
    conveyor has to move (defaults to 1300 mm)"""
    argtxt4 = "assemble connected lines into contours (off by default)"
    parser.add_argument('-l', '--limit', help=argtxt, dest='limit',
                        metavar='F', type=float, default=0.5)
    parser.add_argument('-a', '--angle', help=argtxt2, dest='ang',
                        metavar='F', type=float, default=60)
    parser.add_argument('-b', '--bitelength', help=argtxt3, dest='bitelen',
                        metavar='N', type=int, default=1300)
    parser.add_argument('-c', '--contours', help=argtxt4, dest='contours',
                        action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true")
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    msg = utils.Msg(pv.verbose)
    lim = pv.limit**2
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        msg.say('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='')
            entities = dxf.reader(f)
        except Exception as ex:  # pylint: disable=W0703
            utils.skip(ex, f)
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
            nbites = int(bb.width//pv.bitelen + 1)
            bitelen = bb.width/float(nbites)
            ncon = ' '.join(['Bite {}:', 'found {} contours,',
                             '{} remaining entities.'])
            newentlist = []
            if nbites > 1:
                m = 'Cut length divided into {} bites of {} mm'
                msg.say(m.format(nbites, bitelen))
                for bn, inbite in mkbites(entities, nbites, bitelen):
                    if pv.contours:
                        contours, rement = ent.findcontours(inbite, lim)
                        be = contours + rement
                        msg.say(ncon.format(bn, len(contours), len(rement)))
                    else:
                        be = inbite
                    msg.say('Sorting entities in bite', bn)
                    be.sort(key=lambda e: (e.bbox.minx, e.bbox.miny))
                    newentlist += be
                entities = newentlist
            else:
                if pv.contours:
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
        write_entities(ofn, entities, pv.bitelen, pv.ang)
        msg.say('File "{}" done.'.format(f))

if __name__ == '__main__':
    main(sys.argv[1:])
