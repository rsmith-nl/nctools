# nc2pdf - main program
# vim:fileencoding=utf-8

"""Plot cuts from a Gerber cloth cutter NC file to a PDF."""

import argparse
import os.path
import logging
import sys
import cairo
from nctools import gerbernc, plot, utils

__version__ = '2.0.0-beta'

_lic = """nc2pdf {}
Copyright © 2013, 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
    """
    Main program for the nc2pdf utility.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-v', '--version', action='version',
                       version=__version__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    for fn in utils.xpand(args.files):
        logging.info('starting file "{}"'.format(fn))
        try:
            ofn = utils.outname(fn, extension='.pdf', addenum='_nc')
            rd = gerbernc.Reader(fn)
        except ValueError as e:
            logging.info(str(e))
            fns = "cannot construct output filename. Skipping file '{}'."
            logging.error(fns.format(fn))
            continue
        except IOError as e:
            logging.info("Cannot read file: {}".format(e))
            logging.error("i/o error, skipping file '{}'".format(fn))
            continue
        cuts, xvals, yvals = getcuts(rd)
        cnt = len(cuts)
        logging.info('cot {} cuts'.format(cnt))
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = '{} range from {:.1f} mm to {:.1f} mm'
        logging.info(bs.format('X', minx, maxx))
        logging.info(bs.format('Y', miny, maxy))
        logging.info('plotting the cuts')
        out, ctx = plot.setup(ofn, minx, miny, maxx, maxy)
        plot.grid(ctx, minx, miny, maxx, maxy)
        plot.lines(ctx, cuts)
        plot.title(ctx, 'nc2pdf', ofn, maxy-miny)
        out.show_page()
        logging.info('Writing output file "{}"'.format(ofn))
        out.finish()
        logging.info('File "{}" done.'.format(fn))


def getcuts(rd):
    """
    Make a list of cuts

    Arguments:
        rd: nctools.gerbernc.Reader object

    Returns: A list of lists of (x,y) tuples representing the cuts.
    """
    cuts = []
    x = []
    y = []
    section = None
    cutting = False
    pos = None
    for c, args in rd:
        if c.startswith('down'):
            cutting = True
            if not pos:
                raise ValueError('Start of cutting without pos')
            section = [pos]
        elif c.startswith('up'):
            cutting = False
            if section:
                cuts.append(section)
            section = None
        elif c.startswith('moveto'):
            _, newpos = args
            if cutting:
                section.append(newpos)
            xv, yv = newpos
            x.append(xv)
            y.append(yv)
            pos = newpos
    return cuts, x, y


if __name__ == '__main__':
    main(sys.argv[1:])
