# dxf2nc - main program
# vim:fileencoding=utf-8
# $Date$

"""Converts a DXF file to a cutting program for a Gerber cloth cutter."""

from __future__ import print_function, division

__version__ = '$Revision$'[11:-2]

_lic = """dxf2nc {}
Copyright © 2012-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
import re
import sys
from nctools import bbox, dxf, ent, gerbernc, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def _cutline(e, wr):
    """Cut a ent.Line

    :param ent: nctools.ent.Line
    :param wr: nctoos.gerbernc.Writer
    """
    wr.moveto(e.x[0], e.y[0])
    wr.down()
    wr.moveto(e.x[1], e.y[1])
    wr.up()


def _cutarc(e, wr):
    """Cut an ent.Arc

    :param ent: nctools.ent.Arc
    :param wr: nctoos.gerbernc.Writer
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

    :param ent: nctools.ent.Contour
    :param wr: nctoos.gerbernc.Writer
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


def write_entities(fn, parts, alim):
    """Write all parts to a NC file.

    :param fn: output file name
    :param parts: list of list of entities
    :param alim: minimum turning angle where the knife needs to be lifted
    """
    with gerbernc.Writer(fn, anglim=alim) as w:
        for p in parts:
            w.newpiece()
            for e in p:
                if isinstance(e, ent.Contour):
                    _cutcontour(e, w)
                elif isinstance(e, ent.Arc):
                    _cutarc(e, w)
                elif isinstance(e, ent.Line):
                    _cutline(e, w)
                else:
                    raise ValueError('unknown entity')


def main(argv):
    """Main program for the dxf2nc utility.

    :param argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when
    searching for contours (defaults to 0.5 mm)"""
    argtxt2 = u"""minimum rotation angle in degrees where the knife needs
    to be lifted to prevent breaking (defaults to 60°)"""
    argtxt4 = "assemble connected lines into contours (off by default)"
    parser.add_argument('-l', '--limit', help=argtxt, dest='limit',
                        metavar='F', type=float, default=0.5)
    parser.add_argument('-a', '--angle', help=argtxt2, dest='ang',
                        metavar='F', type=float, default=60)
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
        parts = []
        msg.say('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='')
            entities = dxf.reader(f)
        except Exception as ex:  # pylint: disable=W0703
            utils.skip(ex, f)
            continue
        # separate entities into parts according to their layers
        layers = {e.layer for e in entities}
        # Delete layer names that are not numbers
        layers = [la for la in layers if re.search('^[0-9]+', la)]
        layers.sort(key=lambda x: int(x))  # sort by integer value!
        # remove entities from unused layers.
        entities = [e for e in entities if e.layer in layers]
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
            for layer in layers:
                msg.say('Found layer: "{}"'.format(layer))
                le = [e for e in entities if e.layer == layer]
                if pv.contours:
                    msg.say('Gathering connected entities into contours')
                    contours, rement = ent.findcontours(le, lim)
                    for c in contours:
                        c.layer = layer
                    ncon = 'Found {} contours, {} remaining single entities'
                    msg.say(ncon.format(len(contours), len(rement)))
                    le = contours + rement
                msg.say('Sorting entities')
                le.sort(key=lambda e: (e.bbox.minx, e.bbox.miny))
                parts.append(le)
            msg.say('Sorting pieces')
            parts.sort(key=lambda p: bbox.merge([e.bbox for e in p]).minx)
        length = sum(e.length for e in entities)
        msg.say('Total length of entities: {:.0f} mm'.format(length))
        msg.say('Writing output to "{}"'.format(ofn))
        write_entities(ofn, parts, pv.ang)
        msg.say('File "{}" done.'.format(f))

if __name__ == '__main__':
    main(sys.argv[1:])
