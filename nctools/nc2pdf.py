# file: nc2pdf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
# nc2pdf - main program
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-19 22:34:29 +0100
# Last modified: 2024-12-24T11:08:58+0100
"""Plot cuts from a Gerber cloth cutter NC file to a PDF."""

import argparse
import logging
import sys
from nctools import gerbernc, plot, utils
from nctools import __VERSION__, __LICENSE__

_CP = f"""nc2pdf {__VERSION__}
Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
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
    Entry point for nc2pdf.py.
    """
    args = process_arguments()
    for fn in utils.xpand(args.files):
        logging.info('starting file "{}"'.format(fn))
        try:
            ofn = utils.outname(fn, extension=".pdf", addenum="_nc")
            cuts = list(gerbernc.segments(fn))
        except ValueError as e:
            logging.info(str(e))
            fns = "cannot construct output filename. Skipping file '{}'."
            logging.error(fns.format(fn))
            continue
        except IOError as e:
            logging.info("cannot read file: {}".format(e))
            logging.error("i/o error, skipping file '{}'".format(fn))
            continue
        cnt = len(cuts)
        logging.info("got {} cuts".format(cnt))
        xvals = [pnt[0] for s in cuts for pnt in s]
        yvals = [pnt[1] for s in cuts for pnt in s]
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)
        bs = "{} range from {:.1f} mm to {:.1f} mm"
        logging.info(bs.format("X", minx, maxx))
        logging.info(bs.format("Y", miny, maxy))
        logging.info("plotting the cuts")
        out, ctx = plot.setup(ofn, minx, miny, maxx, maxy)
        plot.grid(ctx, minx, miny, maxx, maxy)
        plot.lines(ctx, cuts)
        plot.title(ctx, "nc2pdf", ofn, maxy - miny)
        out.show_page()
        logging.info('writing output file "{}"'.format(ofn))
        out.finish()
        logging.info('file "{}" done.'.format(fn))


if __name__ == "__main__":
    main()
