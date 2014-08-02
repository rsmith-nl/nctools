# vim:fileencoding=utf-8
# Copyright © 2013,2014 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Classes for reading and writing Gerber NC files for a cloth cutter.
The language and file format for PCB machines is different!
"""
from __future__ import division, print_function
import math
import os.path as op
import bbox


class Reader(object):
    """Reads a subset of Gerber NC files. It defaults to coordinates in
    centi-inches format.
    """

    cmds = {'M0': '# end of file', 'M00': '# program stop',
            'M01': '# optional stop', 'M14': 'down()', 'M15': 'up()'}

    def _newpiece(self, c):
        """Parse the N instruction.

        :c: text to parse
        :returns: text, (number of piece)
        """
        num = int(c[1:])
        return 'newpiece() # {}'.format(c[1:]), (num)

    def _moveto(self, c):
        """Parse a lineair instruction.

        :c: text to parse
        :pnt: current (x,y) point
        :returns: text, (startpoint, endpoint)
        """
        oldpos = self.pos
        x, y = [int(t) for t in c[1:].split('Y')]
        p, q = cin2mm([x, y])
        self.pos = (p, q)
        s = 'moveto({:.1f}, {:.1f})'
        return s.format(p, q), (oldpos, self.pos)

    def _arc(self, c):
        """Parse an arc movement instruction.

        :c: text to parse
        :pnt: current (x,y) point
        :returns: text, (startpoint, endpoint, center of arc)
        """
        oldpos = self.pos
        if c[2] == '2':
            direction = 'arc_cw'
        elif c[2] == '3':
            direction = 'arc_ccw'
        ct = c[4:].replace('Y', ' ').replace('I', ' ').replace('J', ' ')
        x, y, i, j = [int(n) for n in ct.split()]
        p, q, r, s = cin2mm([x, y, i, j])
        self.pos = (p, q)
        fs = '{}({:.1f}, {:.1f}, {:.1f}, {:.1f})'
        return fs.format(direction, p, q, r, s), (oldpos, self.pos, (i, j))

    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            c = f.read().split('*')
        if c[0] != 'H1' and c[1] != 'M20':
            raise ValueError('{} is not a valid NC file.'.format(path))
        ident = c[2].split('/')
        del c[0:3]
        self.name = ident[0]
        self.length = float(ident[1][2:]) * 25.4  # mm
        self.width = float(ident[2][2:]) * 25.4  # mm
        self.commands = c
        self.pos = None

    def __iter__(self):
        """Iterate over the NC commands.

        :yields: text, (other results)
        """
        yield '# Path: {}'. format(self.path), (self.path)
        yield '# Name of part: {}'.format(self.name), (self.name)
        fs = '# Length: {:.1f} mm, width {:.1f} mm'
        yield fs.format(self.length, self.width), (self.length, self.width)
        for c in self.commands:
            if c in Reader.cmds.keys():
                yield Reader.cmds[c], ()
                if c == 'M0':
                    raise StopIteration
            elif c[0] == 'N':
                yield self._newpiece(c)
            elif c[0] == 'X':
                yield self._moveto(c)
            elif c[:3] in ['G02', 'G03']:
                yield self._arc(c)
            else:
                yield 'unknown command: "{}"'.format(c), ()


class Writer(object):
    """Writes Gerber NC files."""

    def __init__(self, path, name=None, anglim=60):
        """Initialize the writer.

        :path: the output file
        :name: name of the program. If not given, the basename without any
        extension will be used.
        """
        self.path = path
        self.name = name
        if not self.name:
            self.name = op.splitext(op.basename(path))[0]
        self.cut = False
        self.pos = None
        self.ang = None
        self.bbox = None
        self.f = None
        self.anglim = float(anglim)
        self.piece = 1
        # commands[2] is an empty placeholder. The name, length and width of
        # the program need to be put there before writing.
        self.commands = ['H1', 'M20', '', 'N1', 'M15']

    def __str__(self):
        return '*'.join(self.commands)

    def newpiece(self):
        self.piece += 1
        self.commands += ['N{}'.format(self.piece)]

    def up(self):
        """Stop cutting.
        """
        self.cut = False
        self.ang = None
        self.commands += ['M15']

    def down(self):
        """Start cutting.
        """
        if not self.pos:
            raise ValueError('start cutting at unknown position')
        self.cut = True
        if self.bbox is None:
            self.bbox = bbox.BBox(self.pos)
        else:
            self.bbox.update(self.pos)
        self.commands += ['M14']

    def moveto(self, x, y):
        """Move the cutting head from the current position to the indicated
        position in a straight line.

        :x: x coordinate in mm
        :y: y coordinate in mm
        """
        x, y = mm2cin([x, y])
        if self.cut:  # We're cutting
            self.bbox.update((x, y))
            dx, dy = x - self.pos[0], y - self.pos[1]
            newang = math.degrees(math.atan2(dy, dx))
            if newang < 0.0:
                newang += 360.0
            if self.ang is not None:
                angdif = math.fabs(newang-self.ang)
                if angdif > 180:
                    angdif = 360 - angdif
                if angdif > self.anglim:
                    self.commands += ['M15', 'M14']
            self.ang = newang
        self.commands += ['X{:.0f}Y{:.0f}'.format(x, y)]
        self.pos = (x, y)

    def write(self):
        """Write the NC file.
        """
        self.__enter__()
        self.__exit__(None, None, None)

    def __enter__(self):
        """Start context manager."""
        self.f = open(self.path, 'wb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop context manager."""
        li = self.bbox.width/100.0
        wi = self.bbox.height/100.0
        self.commands[2] = '{}/L={:.3f}/W={:.3f}'.format(self.name, li, wi)
        if self.commands[-1].startswith('N'):
            del self.commands[-1]  # Remove unnecessary newpiece()
        if not self.commands[-1] == 'M15':
            self.commands.append('M15')
        self.commands.append('M0')
        self.f.write('*'.join(self.commands))
        self.f.write('*')
        self.f.close()


def mm2cin(arg):
    """Convert millimeters to 1/100 in

    :arg: number or sequence of numbers
    :returns: converted number or sequence
    """
    if not type(arg) in [list, tuple]:
        return float(arg) * 100.0 / 25.4
    return [float(j) * 100.0 / 25.4 for j in arg]


def cin2mm(arg):
    """Convert 1/100 in to millimeters

    :arg: number or sequence of numbers
    :returns: converted number or sequence
    """
    if not type(arg) in [list, tuple]:
        return float(arg) * 0.254
    return [float(j) * 0.254 for j in arg]


if __name__ == '__main__':
    from os import remove
    nm = '/tmp/foo.nc'
    # Write a sample file
    with Writer(nm) as w:
        w.moveto(0, 0)
        w.down()
        w.moveto(100, 0)
        w.moveto(100, 100)
        w.moveto(0, 100)
        w.moveto(0, 0)
        print('NC code:', w)
    # Read it back
    rd = Reader(nm)
    for cmd, _ in rd:
        print(cmd)
    remove(nm)
