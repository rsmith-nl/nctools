# file: dxf2pdf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
# dxf2pdf - main program
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-19 22:34:29 +0100
# Last modified: 2024-12-24T11:00:35+0100
"""Read DXF files and renders them as PDF files."""

import argparse
import logging
import sys
from nctools import dxfreader as dxf
from nctools import lines, utils, plot
from nctools import __VERSION__, __LICENSE__

_CP = f"""dxf2pdf {__VERSION__}
Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
"""


class LicenseAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        print(_CP)
        print(__LICENSE__)
        sys.exit()


def process_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-L", "--license", action=LicenseAction, nargs=0, help="print the license"
    )
    group.add_argument("-v", "--version", action="version", version=__VERSION__)
    argtxt4 = "assemble connected lines into contours (off by default)"
    parser.add_argument(
        "-c", "--contours", help=argtxt4, dest="contours", action="store_true"
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
    parser.add_argument(
        "-m",
        "--markers",
        action="store_true",
        help="add start (blue) and end (red) markers",
    )
    parser.add_argument(
        "-a",
        "--alllayers",
        action="store_true",
        help="process all layers (default: numbered layers)",
    )
    parser.add_argument(
        "files", nargs="*", help="one or more file names", metavar="file"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug("Command line arguments = {}".format(sys.argv))
    logging.debug("Parsed arguments = {}".format(args))
    if not args.files:
        parser.print_help()
        sys.exit(0)
    return args


def output(ifn, ofn, entities, args):
    opts = []
    if args.contours:
        opts = ["contours"]
    if args.markers:
        opts.append("markers")
    sorters = {"xy": utils.bbxykey, "yx": utils.bbyxkey, "dist": utils.distkey}
    sortkey = sorters[args.sort]
    if not args.alllayers:
        layers = dxf.numberedlayers(entities)
        logging.info(f"{len(layers)} numbered layers found")
        entities = [e for e in entities if dxf.bycode(e, 8) in layers]
    else:
        layers = dxf.layernames(entities)
    num = len(entities)
    if num == 0:
        logging.info("no entities found! Skipping file '{}'.".format(ifn))
        return
    logging.info("{} entities found".format(num))
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
        logging.info("plotting the entities")
        if args.contours:
            closedseg, openseg = lines.combine_segments(segments)
            fs = '{} {} segments in layer "{}"'
            for a, b in (("closed", closedseg), ("open", openseg)):
                logging.info(fs.format(len(b), a, layername))
            openseg.sort(key=sortkey)
            plot.lines(ctx, openseg, marks=args.markers)
            closedseg.sort(key=sortkey)
            plot.lines(ctx, closedseg, marks=args.markers)
        else:
            fs = '{} segments in layer "{}"'
            logging.info(fs.format(len(segments), layername))
            plot.lines(ctx, segments, marks=args.markers)
    plot.title(ctx, "dxf2pdf", ofn, maxy - miny, options=opts)
    out.show_page()
    logging.info('writing output file "{}"'.format(ofn))
    out.finish()
    logging.info('file "{}" done.'.format(ifn))


def main():
    """
    Entry point for dxf2pdf.py.
    """
    args = process_arguments()
    for f in utils.xpand(args.files):
        logging.info('starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension=".pdf", addenum="_dxf")
            data = dxf.parse(f)
            entities = dxf.entities(data)
        except ValueError as ex:
            logging.info(str(ex))
            fns = "cannot construct output filename. Skipping file '{}'."
            logging.error(fns.format(f))
            continue
        except IOError as ex:
            logging.info(str(ex))
            logging.error("cannot open the file '{}'. Skipping it.".format(f))
            continue
        output(f, ofn, entities, args)


if __name__ == "__main__":
    main()
