# dxf2pdf - main program
# vim:fileencoding=utf-8

"""Reads DXF files and renders them as PDF files."""

import argparse
import datetime
import logging
import os
import sys
import time
import cairo
from nctools import dxfreader, lines, utils

__version__ = '2.0.0-beta'

_lic = """dxf2pdf {}
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-v', '--version', action='version',
                       version=__version__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-a', '--all', action="store_true",
                        help='process all layers (default: numbered layers)')
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
        logging.info('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='.pdf', addenum='_dxf')
            data = dxfreader.parse(f)
            entities = dxfreader.entities(data)
        except ValueError as ex:
            logging.info(str(ex))
            fns = "Cannot construct output filename. Skipping file '{}'."
            logging.error(fns.format(f))
            continue
        except IOError as ex:
            logging.info(str(ex))
            logging.error("Cannot open the file '{}'. Skipping it.".format(f))
            continue
        if not args.all:
            numbered = dxfreader.numberedlayers(entities)
            entities = [e for e in entities if e[8] in numbered]
        # Output
        num = len(entities)
        if num == 0:
            logging.warning('No entities found!')
            continue
        if num > 1:
            logging.info('Found {} entities'.format(num))

        else:
            logging.info('Found 1 entity')
        segments = dxfreader.mksegments(entities)
        bboxes = [lines.bbox(s) for s in segments]
        minx, miny, maxx, maxy = lines.merge_bbox(bboxes)
        out, ctx = cairosetup(ofn, minx, miny, maxx, maxy)
        plotgrid(ctx, minx, miny, maxx, maxy)
        logging.info('Plotting the entities')
        plotlines(ctx, segments)
        plottitle(ctx, ofn, maxy)
        # Finish the page.
        out.show_page()
        out.finish()
        logging.info('File "{}" done.'.format(f))


def cairosetup(ofn, minx, miny, maxx, maxy, offset=40):
    """
    Set up the Cairo surface and drawing context.

    Arguments:
        ofn: Name of the file to store the drawing in.
        minx: Left side of the drawing.
        miny: Bottom of the drawing.
        maxx: Right side of the drawing.
        maxy: Top of the drawing.
        offset: Border around the drawing.

    Returns:
        (output surface, drawing context)
    """
    w = (maxx - minx) + 2*offset
    h = (maxy - miny) + 2*offset
    xf = cairo.Matrix(xx=1.0, yy=-1.0, x0=offset-minx, y0=maxy+offset)
    out = cairo.PDFSurface(ofn, w, h)
    ctx = cairo.Context(out)
    ctx.set_matrix(xf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.5)
    return out, ctx


def plotgrid(context, minx, miny, maxx, maxy, spacing=100):
    """
    Plot a 100x100 grid

    Arguments:
        context: Drawing context.
        minx: Left side of the drawing.
        miny: Bottom of the drawing.
        maxx: Right side of the drawing.
        maxy: Top of the drawing.
        spacing: Spacing between grid lines, defaults to 100.
    """
    context.save()
    context.new_path()
    for x in range(int(minx), int(maxx), spacing):
        context.move_to(x, miny)
        context.line_to(x, maxy)
    for y in range(int(miny), int(maxy), spacing):
        context.move_to(minx, y)
        context.line_to(maxx, y)
    context.close_path()
    context.set_line_width(0.1)
    context.set_source_rgb(0.5, 0.5, 0.5)
    context.set_dash([20.0, 20.0])
    context.stroke()
    context.restore()


def plotlines(context, lines, lw=0.5):
    """
    Plot a list of lines. Each line is a list of 2-tuples (x, y).

    Arguments:
        context: Drawing context.
        lines: Iterator of lines.
        lw: Line width to draw. Defaults to 0.5.
    """
    context.save()
    context.set_line_width(lw)
    context.new_path()
    for ln in lines:
        context.move_to(*ln[0])
        for pt in ln[1:]:
            context.line_to(*pt)
    context.stroke()
    context.restore()


def plottitle(context, ofn, maxy, offset=40):
    """
    Write the title on the plot.

    Arguments:
        context: Drawing context.
        ofn: Name of the output file.
        maxy: top of the drawing area
    """
    context.save()
    context.set_matrix(cairo.Matrix(xx=1.0, yy=1.0))
    context.select_font_face('Sans')
    fh = 10
    context.set_source_rgb(0.0, 0.0, 0.0)
    context.set_font_size(fh)
    context.move_to(5, fh+5)
    txt = ' '.join(['Produced by: dxf2pdf', __version__, 'on',
                    str(datetime.datetime.now())[:-10]])
    context.show_text(txt)
    context.stroke()
    context.move_to(5, maxy+2*offset-(fh))
    txt = 'File: "{}", last modified: {}'
    context.show_text(txt.format(ofn, time.ctime(os.path.getmtime(ofn))))
    context.stroke()
    context.restore()


if __name__ == '__main__':
    main(sys.argv[1:])
