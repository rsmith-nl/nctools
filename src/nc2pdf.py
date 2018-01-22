#!/usr/bin/env python3
# file: nc2pdf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
# nc2pdf - main program
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-19 22:34:29 +0100
# Last modified: 2018-01-22 23:58:52 +0100
"""Plot cuts from a Gerber cloth cutter NC file to a PDF."""

import argparse
import logging
import sys
from nctools import gerbernc, plot, utils
from nctools import __version__

_lic = """nc2pdf {}
Copyright © 2013, 2016, 2018 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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


def main():
    """
    Entry point for nc2pdf.py.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-L', '--license', action=LicenseAction, nargs=0, help="print the license")
    group.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        'files', nargs='*', help='one or more file names', metavar='file')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(sys.argv))
    logging.debug('parsed arguments = {}'.format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    for fn in utils.xpand(args.files):
        logging.info('starting file "{}"'.format(fn))
        try:
            ofn = utils.outname(fn, extension='.pdf', addenum='_nc')
            cuts = list(gerbernc.segments(fn))
        except ValueError as e:
            logging.info(str(e))
            fns = "cannot construct output filename. Skipping file '{}'."
            logging.error(fns.format(fn))
            continue
        except IOError as e:
            logging.info("Cannot read file: {}".format(e))
            logging.error("i/o error, skipping file '{}'".format(fn))
            continue
        cnt = len(cuts)
        logging.info('got {} cuts'.format(cnt))
        xvals = [pnt[0] for s in cuts for pnt in s]
        yvals = [pnt[1] for s in cuts for pnt in s]
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = '{} range from {:.1f} mm to {:.1f} mm'
        logging.info(bs.format('X', minx, maxx))
        logging.info(bs.format('Y', miny, maxy))
        logging.info('plotting the cuts')
        out, ctx = plot.setup(ofn, minx, miny, maxx, maxy)
        plot.grid(ctx, minx, miny, maxx, maxy)
        plot.lines(ctx, cuts)
        plot.title(ctx, 'nc2pdf', ofn, maxy - miny)
        out.show_page()
        logging.info('Writing output file "{}"'.format(ofn))
        out.finish()
        logging.info('File "{}" done.'.format(fn))


if __name__ == '__main__':
    main()
