# nc2pdf - main program
# vim:fileencoding=utf-8
# $Date$

"""Plot cuts from a Gerber cloth cutter NC file to a PDF."""

from __future__ import print_function, division

__version__ = '$Revision$'[11:-2]

_lic = """nc2pdf {}
Copyright © 2013, 2014 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
import datetime
import os.path
import time
import sys
import cairo
from nctools import gerbernc, plot, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def getcuts(rd):
    """Make a list of cuts

    :rd: nctools.gerbernc.Reader object
    :returns: list of (x,y) tuples representing the cuts.
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


def main(argv):
    """Main program for the nc2pdf utility.

    :argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
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
    offset = 40
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for fn in utils.xpand(pv.files):
        msg.say('Starting file "{}"'.format(fn))
        try:
            ofn = utils.outname(fn, extension='.pdf', addenum='_nc')
            rd = gerbernc.Reader(fn)
        except ValueError as e:
            msg.say(str(e))
            fns = "Cannot construct output filename. Skipping file '{}'."
            msg.say(fns.format(fn))
            continue
        except IOError as e:
            msg.say("Cannot read file: {}".format(e))
            msg.say("Skipping file '{}'".format(fn))
            continue
        cuts, xvals, yvals = getcuts(rd)
        cnt = len(cuts)
        msg.say('Got {} cuts'.format(cnt))
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = '{} range from {:.1f} mm to {:.1f} mm'
        msg.say(bs.format('X', minx, maxx))
        msg.say(bs.format('Y', miny, maxy))
        w = maxx - minx + offset
        h = maxy - miny + offset
        msg.say('Plotting the cuts')
        # Produce PDF output. Scale factor is 1 mm real =
        # 1 PostScript point in the PDF file
        xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
        out = cairo.PDFSurface(ofn, w, h)
        ctx = cairo.Context(out)
        ctx.set_matrix(xf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(0.5)
        # Plot a grid in red
        plot.plotgrid(ctx, w, h)
        # Plot the cutlines
        colors = plot.crange(380, 650, cnt)
        # Plot in colors
        ctx.save()
        ctx.translate(offset/2-minx, offset/2-miny)
        for section, (r, g, b) in zip(cuts, colors):
            x1, y1 = section.pop(0)
            ctx.move_to(x1, y1)
            ctx.set_source_rgb(r/255.0, g/255.0, b/255.0)
            for x2, y2 in section:
                ctx.line_to(x2, y2)
            ctx.stroke()
        ctx.restore()
        # plot the color bar
        plot.plotcolorbar(ctx, w, cnt, colors)
        # Plot the filename
        ctx.save()
        ctx.set_matrix(cairo.Matrix(xx=1.0, yy=1.0))
        ctx.select_font_face('Sans')
        fh = min(10, h/40)
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.set_font_size(fh)
        ctx.move_to(5, fh+5)
        txt = ' '.join(['Produced by: nc2pdf', __version__, 'on',
                        str(datetime.datetime.now())[:-10]])
        ctx.show_text(txt)
        ctx.stroke()
        fh = min(30, h/20)
        ctx.move_to(5, h-15)
        txt = 'File: "{}", last modified: {}'
        ctx.show_text(txt.format(fn, time.ctime(os.path.getmtime(fn))))
        ctx.stroke()
        ctx.restore()
        # Finish the page.
        out.show_page()
        msg.say('Writing output file "{}"'.format(ofn))
        out.finish()
        msg.say('File "{}" done.'.format(fn))


if __name__ == '__main__':
    main(sys.argv[1:])
