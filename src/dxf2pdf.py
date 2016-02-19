# dxf2pdf - main program
# vim:fileencoding=utf-8

"""Reads DXF files and renders them as PDF files."""

__version__ = '1.12-beta'

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

import argparse
import sys
import os
import datetime
import time
import cairo
from nctools import bbox, dxf, plot, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def main(argv):
    """Main program for the readdxf utility.

    :param argv: command line arguments
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
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    offset = 40
    for f in utils.xpand(pv.files):
        msg.say('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='.pdf', addenum='_dxf')
            entities = dxf.reader(f)
        except ValueError as ex:
            msg.say(str(ex))
            fns = "Cannot construct output filename. Skipping file '{}'."
            msg.say(fns.format(f))
            continue
        except IOError as ex:
            msg.say(str(ex))
            msg.say("Cannot open the file '{}'. Skipping it.".format(f))
            continue
        # Output
        num = len(entities)
        if num == 0:
            msg.say('No entities found!')
            continue
        if num > 1:
            msg.say('Contains {} entities'.format(num))
            bbx = [e.bbox for e in entities]
            bb = bbox.merge(bbx)
        else:
            msg.say('Contains: 1 entity')
            bb = entities[0].bbox
        w = bb.width + offset
        h = bb.height + offset
        xf = cairo.Matrix(xx=1.0, yy=-1.0, y0=h)
        out = cairo.PDFSurface(ofn, w, h)
        ctx = cairo.Context(out)
        ctx.set_matrix(xf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_width(0.5)
        plot.plotgrid(ctx, w, h)
        colors = plot.crange(380, 650, len(entities))
        msg.say('Plotting the entities')
        plot.plotentities(ctx, (offset/2-bb.minx, offset/2-bb.miny),
                          entities, colors)
        # plot the color bar
        plot.plotcolorbar(ctx, w, len(entities), colors)
        # Plot the filename
        ctx.save()
        ctx.set_matrix(cairo.Matrix(xx=1.0, yy=1.0))
        ctx.select_font_face('Sans')
        fh = min(10, h/40)
        ctx.set_source_rgb(0.0, 0.0, 0.0)
        ctx.set_font_size(fh)
        ctx.move_to(5, fh+5)
        txt = ' '.join(['Produced by: dxf2pdf', __version__, 'on',
                        str(datetime.datetime.now())[:-10]])
        ctx.show_text(txt)
        ctx.stroke()
        fh = min(30, h/20)
        ctx.move_to(5, h-15)
        txt = 'File: "{}", last modified: {}'
        ctx.show_text(txt.format(f, time.ctime(os.path.getmtime(f))))
        ctx.stroke()
        ctx.restore()
        # Finish the page.
        out.show_page()
        out.finish()
        msg.say('File "{}" done.'.format(f))


if __name__ == '__main__':
    main(sys.argv[1:])
