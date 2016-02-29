# readdxf - main program
# vim:fileencoding=utf-8

"""Reads DXF files and prints the entities in human-readable form."""

import argparse
import logging
import math
import pprint
import sys
from nctools import dxfreader as dx
from nctools import utils as ut

__version__ = '2.0.0-beta'
_lic = """readdxf {}
Copyright © 2011-2016 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def main(argv):
    """Main program for the readdxf utility.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtext1 = 'show details of unknown entities'
    parser.add_argument('-v', '--verbose', help=argtext1, action="store_true")
    parser.add_argument('-a', '--all', action="store_true",
                        help='process all layers (default: numbered layers)')
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('files', metavar='file', nargs='*',
                        help='one or more file names')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('Command line arguments = {}'.format(argv))
    logging.debug('Parsed arguments = {}'.format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    for f in ut.xpand(args.files):
        print('Filename: {}'.format(f))
        try:
            data = dx.parse(f)
            if args.verbose:
                for d in data:
                    pprint.pprint(d)
            entities = dx.entities(data)
        except Exception as ex:
            ut.skip(ex, f)
            continue
        if not args.all:
            numbered = dx.numberedlayers(entities)
            bylayer = {nm: dx.fromlayer(entities, nm)
                       for nm in numbered}
            entities = []
            for layerent in bylayer.values():
                entities += layerent
        num = len(entities)
        if num == 0:
            logging.warning('no entities found!')
            continue
        else:
            print('Contains: {} entities'.format(num))
            if args.verbose:
                for e in entities:
                    pprint.pprint(e)
            layers = dx.layernames(entities)
            for layer in layers:
                print('Layer: "{}"'.format(layer))
                for e in dx.fromlayer(entities, layer):
                    printent(e, args.verbose)


def printent(e, v):
    """Print a DXF entity"""
    def line():
        xs, ys = float(dx.bycode(e, 10)), float(dx.bycode(e, 20))
        xe, ye = float(dx.bycode(e, 11)), float(dx.bycode(e, 21))
        outs = '  LINE from ({:.2f}, {:.2f}) to ({:.2f}, {:.2f})'
        print(outs.format(xs, ys, xe, ye))

    def arc():
        xc, yc, R = (float(dx.bycode(e, 10)), float(dx.bycode(e, 20)),
                     float(dx.bycode(e, 40)))
        sa, ea = float(dx.bycode(e, 50)), float(dx.bycode(e, 51))
        sar, ear = math.radians(sa), math.radians(ea)
        xs, ys = xc + R*math.cos(sar), yc + R*math.sin(sar)
        xe, ye = xc + R*math.cos(ear), yc + R*math.sin(ear)
        outs = '  ARC from ({:.2f}, {:.2f}) to ({:.2f}, {:.2f})'
        print(outs.format(xs, ys, xe, ye))
        outs = '      centered at ({:.2f}, {:.2f}), ' \
               'radius {:.2f}, from {:.1f}° to {:.1f}°'
        print(outs.format(xc, yc, R, sa, ea))

    def polyline():
        print('  POLYLINE')

    def vertex():
        x, y = float(dx.bycode(e, 10)), float(dx.bycode(e, 20))
        outs = '    VERTEX at ({:.2f}, {:.2f})'.format(x, y)
        if 42 in e:
            v = math.degrees(math.atan(float(dx.bycode(e, 42)))*4)
            outs += ', curve angle {:.1f}°'.format(v)
        print(outs)

    def endseq():
        print('  ENDSEQ')

    printdict = {'LINE': line, 'ARC': arc,
                 'POLYLINE': polyline, 'VERTEX': vertex,
                 'SEQEND': endseq}
    k = dx.bycode(e, 0)
    try:
        printdict[k]()
    except KeyError:
        if v:
            print('  {} entity: {}'.format(k, e))
        else:
            print('  {} entity'.format(k))


if __name__ == '__main__':
    main(sys.argv[1:])
