# file: dxfgerber.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
# dxfgerber - main program
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-19 22:34:29 +0100
# Last modified: 2018-01-23 21:24:33 +0100
"""
Reorganizes entities in a DXF file.

For each numbered layer (except layer 0) in numbered order it groups connected
lines together in polylines and writes them and any remaining loose lines in
sorted order.
"""

import argparse
import logging
import sys
from nctools import dxfreader as dx
from nctools import lines, utils
from nctools import __version__

_lic = """dxfgerber {}
Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
SUCH DAMAGE.""".format(
    __version__
)

dxfheader = "  0\r\nSECTION\r\n  2\r\nENTITIES\r\n"
dxffooter = "  0\r\nENDSEC\n  0\r\nEOF\r\n"
linefmt = (
    "0\r\nLINE\r\n  8\r\n{layer}\r\n 10\r\n{x1:.3f}\r\n 20\r\n{y1:.3f}"
    " 30\r\n0\r\n 11\r\n{x2:.3f}\r\n 21\r\n{y2:.3f}\r\n 31\r\n0\r\n"
)
# The flag in plheader should be 8 for an open polyline or 9 for a closed one.
# I'm assuming that in a closed segment the last point (equal to first) can be
# left out.
plheader = (
    "0\r\nPOLYLINE\r\n100\r\nAcDb3dPolyline\r\n 66\r\n   1\r\n"
    "  8\r\n{layer}\r\n 10\r\n0\r\n 20\r\n0\r\n"
    " 30\r\n0\r\n 70\r\n{flag:3d}\r\n"
)
vertex = (
    "0\r\nVERTEX\r\n100\r\nAcDbVertex\r\n100\r\nAcDb3dPolylineVertex\r\n"
    "  8\r\n{layer}\r\n"
    " 10\r\n{x}\r\n 20\r\n{y}\r\n 30\r\n0\r\n 70\r\n32\r\n"
)
plfooter = "0\r\nSEQEND\r\n  8\r\n{layer}\r\n"


class LicenseAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def write_segment(s, out, layer):
    """Write a segment to a file."""
    if len(s) == 2:
        out.write(
            linefmt.format(layer=layer, x1=s[0][0], y1=s[0][1], x2=s[1][0], y2=s[1][1])
        )
    elif len(s) > 2:
        if lines.closed(s):
            flag = 9
            pnts = s[:-1]
        else:
            flag = 8
            pnts = s
        out.write(plheader.format(layer=layer, flag=flag))
        for a, b in pnts:
            out.write(vertex.format(layer=layer, x=a, y=b))
        out.write(plfooter.format(layer=layer))


def write_allseg(seg, out, layer, keyfunc):
    """Assemble segments into contours before writing them."""
    closedseg, openseg = lines.combine_segments(seg)
    fs = '{} {} segments in layer "{}"'
    for a, b in (("closed", closedseg), ("open", openseg)):
        logging.info(fs.format(len(b), a, layer))
    openseg.sort(key=keyfunc)
    for s in openseg:
        write_segment(s, out, layer)
    closedseg.sort(key=keyfunc)
    for s in closedseg:
        write_segment(s, out, layer)


def process_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-d",
        "--dist",
        help="maximum distance between points considered equal "
        "(defaults to 0.25 mm)",
        metavar="mm",
        type=float,
        default=0.25,
    )
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument(
        "-s",
        "--sort",
        default="xy",
        choices=["xy", "yx", "dist"],
        help="sorting algorithm to use (defaults to 'xy')",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-L", "--license", action=LicenseAction, nargs=0, help="print the license"
    )
    group.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "files", nargs="*", help="one or more file names", metavar="file"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug("command line arguments = {}".format(sys.argv))
    logging.debug("parsed arguments = {}".format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    return args


def main():
    """
    Entry point for dxfgerber.py.
    """
    args = process_arguments()
    sorters = {"xy": utils.bbxykey, "yx": utils.bbyxkey, "dist": utils.distkey}
    sortkey = sorters[args.sort]
    lines.epsilon = args.dist
    for f in utils.xpand(args.files):
        logging.info('starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension=".dxf", addenum="_mod")
            data = dx.parse(f)
            entities = dx.entities(data)
        except ValueError as ex:
            logging.info(str(ex))
            fns = "error during processing. Skipping file '{}'."
            logging.error(fns.format(f))
            continue
        except IOError as ex:
            logging.info(str(ex))
            logging.error("i/o error in file '{}'. Skipping it.".format(f))
            continue
        layers = dx.numberedlayers(entities)
        entities = [e for e in entities if dx.bycode(e, 8) in layers]
        num = len(entities)
        if num == 0:
            logging.info("no entities found! Skipping file '{}'.".format(f))
            continue
        logging.info("{} entities found.".format(num))
        with open(ofn, "w") as out:
            out.write(dxfheader)
            for layername in layers:
                thislayer = dx.fromlayer(entities, layername)
                ls = '{} entities found in layer "{}".'
                logging.info(ls.format(num, layername))
                segments = lines.mksegments(thislayer)
                fs = '{} segments in layer "{}"'
                logging.info(fs.format(len(segments), layername))
                write_allseg(segments, out, layername, sortkey)
            out.write(dxffooter)


if __name__ == "__main__":
    main()
