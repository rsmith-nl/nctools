# dxf2nc - main program
# vim:fileencoding=utf-8

"""Converts a DXF file to a cutting program for a Gerber cloth cutter."""

import argparse
import logging
import sys
from nctools import dxfreader, lines, gerbernc, utils

__version__ = '2.0.0-beta'

_lic = """dxf2nc {}
Copyright © 2012-2016 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
    """Main program for the dxf2nc utility.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt2 = """minimum rotation angle in degrees where the knife needs
    to be lifted to prevent breaking (defaults to 60°)"""
    argtxt4 = "assemble connected lines into contours (off by default)"
    parser.add_argument('-a', '--angle', help=argtxt2, dest='ang',
                        metavar='F', type=float, default=60)
    parser.add_argument('-c', '--contours', help=argtxt4, dest='contours',
                        action="store_true")
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('Command line arguments = {}'.format(argv))
    logging.debug('Parsed arguments = {}'.format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(args.files):
        # parts = []
        logging.info('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='')
            data = dxfreader.parse(f)
            entities = dxfreader.entities(data)
        except ValueError as ex:
            logging.info(str(ex))
            fns = "error during processing. Skipping file '{}'."
            logging.error(fns.format(f))
            continue
        except IOError as ex:
            logging.info(str(ex))
            logging.error("i/o error in file '{}'. Skipping it.".format(f))
            continue
        layers = dxfreader.numberedlayers(entities)
        entities = [e for e in entities if e[8] in layers]
        num = len(entities)
        if num == 0:
            logging.info("no entities found! Skipping file '{}'.".format(f))
            continue
        logging.info('{} entities found.'.format(num))
        out = gerbernc.Writer(ofn)
        for layername in layers:
            out.newpiece()
            thislayer = dxfreader.fromlayer(entities, layername)
            ls = '{} entities found in layer "{}".'
            logging.info(ls.format(num, layername))
            segments = lines.mksegments(thislayer)
            fs = '{} segments in layer "{}"'
            logging.info(fs.format(len(segments), layername))
            if args.contours:
                cut_contours(segments, out, layername)
            else:
                # TODO: sort segments
                cut_segments(segments, out)
        out.write()


def cut_contours(seg, w, layer):
    """Assemble contours into segments"""
    closedseg, openseg = lines.combine_segments(seg)
    fs = '{} {} segments in layer "{}"'
    for a, b in (('closed ', closedseg), ('open ', openseg)):
        logging.info(fs.format(len(b), a, layer))
    # TODO: Sort open segments
    cut_segments(openseg, w)
    # TODO: Sort closed segments
    cut_segments(closedseg, w)


def cut_segments(seg, w):
    """Generate cutting commands for a list of segments.

    Arguments:
        seg: List of line segments.
        w: gerbernc.Writer instance
    """
    for s in seg:
        w.moveto(*s[0])
        w.down()
        for p in s[1:]:
            w.moveto(*p)
        w.up()


if __name__ == '__main__':
    main(sys.argv[1:])
