# readdxf - main program
# vim:fileencoding=utf-8
# $Date$

"""Reads DXF files and prints the entities in human-readable form."""

from __future__ import print_function, division

__version__ = '$Revision$'[11:-2]

_lic = """readdxf {}
Copyright © 2011-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
from nctools import bbox, dxf, ent, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def main(argv):
    """Main program for the readdxf utility.

    :param argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when
    searching for contours (defaults to 0.5 mm)"""
    parser.add_argument('-l', '--limit', nargs='?', help=argtxt, dest='limit',
                        type=float, default=0.5)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('files', metavar='file', nargs='*',
                        help='one or more file names')
    pv = parser.parse_args(argv)
    msg = utils.Msg()
    lim = pv.limit**2
    parts = []
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        try:
            entities = dxf.reader(f)
        except Exception as ex:
            utils.skip(ex, f)
            continue
        num = len(entities)
        msg.say('Filename: {}'.format(f))
        if num == 0:
            msg.say('No entities found!')
            sys.exit(1)
        if num > 1:
            msg.say('Contains: {} entities'.format(num))
            bbe = [e.bbox for e in entities]
            bb = bbox.merge(bbe)
            layers = {e.layer for e in entities}
            for layer in layers:
                msg.say('Layer: "{}"'.format(layer))
                le = [e for e in entities if e.layer == layer]
                contours, rement = ent.findcontours(le, lim)
                for c in contours:
                    c.layer = layer
                ncon = 'Found {} contours, {} remaining single entities'
                msg.say(ncon.format(len(contours), len(rement)))
                le = contours + rement
                le.sort(key=lambda x: x.bbox.minx)
                parts.append(le)
        else:
            msg.say('Contains: 1 entity')
            msg.say('Layer: "{}"'.format(entities[0].layer))
            bb = entities[0].bbox
            parts.append(entities)
        es = 'Extents: {:.1f} ≤ x ≤ {:.1f}, {:.1f} ≤ y ≤ {:.1f}'
        msg.say(es.format(bb.minx, bb.maxx, bb.miny, bb.maxy))
        length = sum(e.length for e in entities)
        msg.say('Total length of entities: {:.0f} mm'.format(length))
        for p in parts:
            msg.say('Layer: "{}"'.format(p[0].layer))
            for e in p:
                msg.say(e)
                if isinstance(e, ent.Contour):
                    for c in e.entities:
                        msg.say('..', c)


if __name__ == '__main__':
    main(sys.argv[1:])
