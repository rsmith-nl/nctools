# dxf2pdf - main program
# vim:fileencoding=utf-8
"""Read DXF files and renders them as PDF files."""

import argparse
import logging
import sys
from nctools import dxfreader as dxf
from nctools import lines, utils, plot

__version__ = '2.0.0-beta'

_lic = """dxf2pdf {}
Copyright © 2011-2017 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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


parser = argparse.ArgumentParser(description=__doc__)
group = parser.add_mutually_exclusive_group()
group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                   help="print the license")
group.add_argument('-v', '--version', action='version',
                   version=__version__)
argtxt4 = "assemble connected lines into contours (off by default)"
parser.add_argument('-c', '--contours', help=argtxt4, dest='contours',
                    action="store_true")
parser.add_argument('--log', default='warning',
                    choices=['debug', 'info', 'warning', 'error'],
                    help="logging level (defaults to 'warning')")
parser.add_argument('-s', '--sort', default='xy',
                    choices=['xy', 'yx', 'dist'],
                    help="sorting algorithm to use (defaults to 'xy')")
parser.add_argument('-m', '--markers', action="store_true",
                    help='add start (blue) and end (red) markers')
parser.add_argument('files', nargs='*', help='one or more file names',
                    metavar='file')
args = parser.parse_args(sys.argv[1:])
logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                    format='%(levelname)s: %(message)s')
logging.debug('Command line arguments = {}'.format(sys.argv))
logging.debug('Parsed arguments = {}'.format(args))
sorters = {'xy': utils.bbxykey, 'yx': utils.bbyxkey, 'dist': utils.distkey}
sortkey = sorters[args.sort]
opts = []
if args.contours:
    opts = ['contours']
if args.markers:
    opts.append('markers')
if not args.files:
    parser.print_help()
    sys.exit(0)
for f in utils.xpand(args.files):
    logging.info('Starting file "{}"'.format(f))
    try:
        ofn = utils.outname(f, extension='.pdf', addenum='_dxf')
        data = dxf.parse(f)
        entities = dxf.entities(data)
    except ValueError as ex:
        logging.info(str(ex))
        fns = "Cannot construct output filename. Skipping file '{}'."
        logging.error(fns.format(f))
        continue
    except IOError as ex:
        logging.info(str(ex))
        logging.error("Cannot open the file '{}'. Skipping it.".format(f))
        continue
    layers = dxf.numberedlayers(entities)
    entities = [e for e in entities if dxf.bycode(e, 8) in layers]
    # Output
    num = len(entities)
    if num == 0:
        logging.info("No entities found! Skipping file '{}'.".format(f))
        continue
    logging.info('{} entities found'.format(num))
    allsegments = lines.mksegments(entities)
    bboxes = [lines.bbox(s) for s in allsegments]
    minx, miny, maxx, maxy = lines.merge_bbox(bboxes)
    out, ctx = plot.setup(ofn, minx, miny, maxx, maxy)
    plot.grid(ctx, minx, miny, maxx, maxy)
    for layername in layers:
        thislayer = dxf.fromlayer(entities, layername)
        segments = lines.mksegments(thislayer)
        ls = '{} entities found in layer "{}".'
        logging.info(ls.format(len(thislayer), layername))
        logging.info('Plotting the entities')
        if args.contours:
            closedseg, openseg = lines.combine_segments(segments)
            fs = '{} {} segments in layer "{}"'
            for a, b in (('closed', closedseg), ('open', openseg)):
                logging.info(fs.format(len(b), a, layername))
            openseg.sort(key=sortkey)
            plot.lines(ctx, openseg, marks=args.markers)
            closedseg.sort(key=sortkey)
            plot.lines(ctx, closedseg, marks=args.markers)
        else:
            fs = '{} segments in layer "{}"'
            logging.info(fs.format(len(segments), layername))
            plot.lines(ctx, segments, marks=args.markers)
    plot.title(ctx, 'dxf2pdf', ofn, maxy-miny, options=opts)
    out.show_page()
    logging.info('Writing output file "{}"'.format(ofn))
    out.finish()
    logging.info('File "{}" done.'.format(f))
