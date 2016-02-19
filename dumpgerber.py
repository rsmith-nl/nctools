#!/usr/bin/env python3
# file: dumpgerber.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-15 16:45:18 +0200

"""Dump the contents of a NC file for a Gerber cutter in a readable form."""

import sys
import os.path

__version__ = '1.12-beta'

eof = 'end of file'
kd, ku = 'knife down', 'knife up'
sd, ns = 'slow down', 'resume normal speed'
md, ad = 'main drill', 'auxilliary drill'
simple = {'M0': eof, 'M00': eof,
          'M01': 'optional stop', 'M14': kd, 'M15': ku, 'B': kd, 'A': ku,
          'M17': 'maximum advance (zero heel cut)',
          'M18': 'inhibit next overcut', 'M19': 'no overcut, no advance',
          'M20': 'message', 'M25': sd, 'M26': ns,
          'M31': 'labeler data follows',
          'M40': 'allow auto-sharpen', 'M41': 'inhibit auto-sharpen',
          'M42': 'sharpen', 'M43': md, 'M44': ad, 'R': md,
          'M46': 'lift and plunge corner', 'M47': 'knife intelligence off',
          'M48': 'knife intelligence on',
          'M51': 'zero knife intelligence transducers',
          'M60': 'reduce velocity by 5%', 'M61': 'reduce velocity by 10%',
          'M62': 'reduce velocity by 15%', 'M63': 'reduce velocity by 20%',
          'M64': 'reduce velocity by 25%', 'M65': 'reduce velocity by 30%',
          'M66': 'reduce velocity by 35%', 'M67': 'reduce velocity by 40%',
          'M69': 'move conveyor',
          'M70': 'set current position as origin'}
withargs = {'H': 'file #{}', 'N': 'piece #{}', 'F': 'feed rate {} in/min'}


def main(argv):
    """Entry point for this script.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    del argv[0]  # delete the name of the script.
    # Real work starts here.
    for fn in argv:
        with open(fn) as df:
            data = df.read()
        print("/Reading file '{}'./".format(fn))
        items = data.split('*')
        if len(items[-1]) == 0:
            del items[-1]
        print("/This file contains {} blocks./".format(len(items)))
        for cmd in items:
            if cmd in simple:
                print('{:20s} /{}/'.format(cmd, simple[cmd]))
            elif cmd[0] in withargs:
                arg = withargs[cmd[0]].format(cmd[1:])
                print('{:20s} /{}/'.format(cmd, arg))
            elif cmd.startswith('X'):
                x, y = cmd[1:].split('Y')
                x, y = float(x)*25.4/100, float(y)*25.4/100
                fs = '{:20s} /move to x = {:.0f} mm, y = {:.0f} mm/'
                print(fs.format(cmd, x, y))
            else:
                print(cmd)


if __name__ == '__main__':
    main(sys.argv)
