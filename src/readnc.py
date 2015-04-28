# readnc - main program
# vim:fileencoding=utf-8

"""Reads a Gerber cloth cutter NC file and print the contents in
human-readable form."""

__version__ = '1.11-beta'

_lic = """readnc {}
Copyright © 2012-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.

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
from nctools import gerbernc, utils


class LicenseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(_lic)
        sys.exit()


def main(argv):
    """Main program for the readnc utility.

    :param argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-L', '--license', action=LicenseAction, nargs=0,
                       help="print the license")
    group.add_argument('-V', '--version', action='version',
                       version=__version__)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for fn in utils.xpand(pv.files):
        try:
            rd = gerbernc.Reader(fn)
        except IOError as e:
            utils.skip(e, fn)
            continue
        except ValueError as e:
            utils.skip(e, fn)
            continue
        # print the file
        for cmd, _ in rd:
            print(cmd)


if __name__ == '__main__':
    main(sys.argv[1:])
