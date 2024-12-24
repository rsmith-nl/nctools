# file: dumpgerber.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-15 16:45:18 +0200
# Last modified: 2018-01-23 21:36:22 +0100
"""Dump the contents of a NC file for a Gerber cutter in a readable form."""

import argparse
import sys
from nctools import __version__

eof = "end of file"
kd, ku = "knife down", "knife up"
sd, ns = "slow down", "resume normal speed"
md, ad = "main drill", "auxilliary drill"
simple = {
    "M0": eof,
    "M00": eof,
    "M01": "optional stop",
    "M14": kd,
    "M15": ku,
    "B": kd,
    "A": ku,
    "M17": "maximum advance (zero heel cut)",
    "M18": "inhibit next overcut",
    "M19": "no overcut, no advance",
    "M20": "message",
    "M25": sd,
    "M26": ns,
    "M31": "labeler data follows",
    "M40": "allow auto-sharpen",
    "M41": "inhibit auto-sharpen",
    "M42": "sharpen",
    "M43": md,
    "M44": ad,
    "R": md,
    "M46": "lift and plunge corner",
    "M47": "knife intelligence off",
    "M48": "knife intelligence on",
    "M51": "zero knife intelligence transducers",
    "M60": "reduce velocity by 5%",
    "M61": "reduce velocity by 10%",
    "M62": "reduce velocity by 15%",
    "M63": "reduce velocity by 20%",
    "M64": "reduce velocity by 25%",
    "M65": "reduce velocity by 30%",
    "M66": "reduce velocity by 35%",
    "M67": "reduce velocity by 40%",
    "M69": "move conveyor",
    "M70": "set current position as origin",
}
withargs = {"H": "file #{}", "N": "piece #{}", "F": "feed rate {} in/min"}

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
SUCH DAMAGE.""".format(
    __version__
)


class LicenseAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def process_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-L", "--license", action=LicenseAction, nargs=0, help="print the license"
    )
    group.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "files", nargs="*", help="one or more file names", metavar="file"
    )
    args = parser.parse_args(sys.argv[1:])
    if not args.files:
        parser.print_help()
        sys.exit(0)
    return args


def main():
    """
    Entry point for dumpgerber.py.
    """
    args = process_arguments()
    for fn in args.files:
        with open(fn) as df:
            data = df.read()
        print("/Reading file '{}'./".format(fn))
        items = data.split("*")
        if len(items[-1]) == 0:
            del items[-1]
        print("/This file contains {} blocks./".format(len(items)))
        for cmd in items:
            if cmd in simple:
                print("{:20s} /{}/".format(cmd, simple[cmd]))
            elif cmd[0] in withargs:
                arg = withargs[cmd[0]].format(cmd[1:])
                print("{:20s} /{}/".format(cmd, arg))
            elif cmd.startswith("X"):
                x, y = cmd[1:].split("Y")
                x, y = round(float(x) * 25.4 / 100, 0), round(float(y) * 25.4 / 100, 0)
                fs = "{:20s} /move to x = {:.0f} mm, y = {:.0f} mm/"
                print(fs.format(cmd, x, y))
            else:
                print(cmd)


if __name__ == "__main__":
    main()
