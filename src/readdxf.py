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
from nctools import dxfentities, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def printent(e, v):
    def line():
        xs, ys = float(e[10]), float(e[20])
        xe, ye = float(e[11]), float(e[21])
        outs = '  LINE from ({:.2f}, {:.2f}) to ({:.2f}, {:.2f})'
        print(outs.format(xs, ys, xe, ye))

    def arc():
        xc, yc = float(e[10]), float(e[20])
        outs = '  ARC centered at ({:.2f}, {:.2f})'
        print(outs.format(xc, yc))

    def polyline():
        print('  POLYLINE')

    def vertex():
        x, y = float(e[10]), float(e[20])
        outs = '    VERTEX at ({:.2f}, {:.2f})'
        print(outs.format(x, y))

    def endseq():
        print('  ENDSEQ')

    printdict = {'LINE': line, 'ARC': arc,
                 'POLYLINE': polyline, 'VERTEX': vertex,
                 'SEQEND': endseq}
    try:
        printdict[e[0]]()
    except KeyError:
        if v:
            print('  {} entity: {}'.format(e[0], e))
        else:
            print('  {} entity'.format(e[0]))


def main(argv):
    """Main program for the readdxf utility.

    :param argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when
    searching for contours (defaults to 0.5 mm)"""
    parser.add_argument('-l', '--limit', nargs='?', help=argtxt, dest='limit',
                        type=float, default=0.5)
    argtext1 = 'show details of unknown entities'
    parser.add_argument('-v', '--verbose', help=argtext1, action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('files', metavar='file', nargs='*',
                        help='one or more file names')
    pv = parser.parse_args(argv)
    lim = pv.limit**2
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        try:
            entities = dxfentities.read_entities(f)
        except Exception as ex:
            utils.skip(ex, f)
            continue
        num = len(entities)
        print('Filename: {}'.format(f))
        if num == 0:
            print('No entities found!')
            continue
        else:
            print('Contains: {} entities'.format(num))
            layers = {e[8] for e in entities}
            for layer in layers:
                print('Layer: "{}"'.format(layer))
                le = [e for e in entities if e[8] == layer]
                for e in le:
                    printent(e, pv.verbose)


if __name__ == '__main__':
    main(sys.argv[1:])
