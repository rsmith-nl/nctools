# vim:fileencoding=utf-8
# Copyright © 2013-2016 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Last modified: 2017-06-04 16:08:22 +0200
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
"""
Classes for reading and writing Gerber NC files for a cloth cutter.

The language and file format for PCB machines is different!
"""

import math
import os.path as op


class Writer(object):
    """Write Gerber NC files."""

    def __init__(self, path, name=None, anglim=60):
        """
        Initialize the writer.

        Arguments:
            path: the output file
            name: name of the program. If not given, the basename without
                  any extension will be used.
            anglim: limit of angle between continuou cuts.
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
        self.piece = 0
        # commands[2] is an empty placeholder. The name, length and width of
        # the program need to be put there before writing.
        self.commands = ['H1', 'M20', '', 'M15']

    def __str__(self):
        """Convert to string."""
        return '*'.join(self.commands)

    def newpiece(self):
        """Start a new piece."""
        self.piece += 1
        self.commands += ['N{}'.format(self.piece)]

    def up(self):
        """Stop cutting (raise the knife)."""
        self.cut = False
        self.ang = None
        self.commands += ['M15']

    def _bbupdate(self, pnt):
        """Update bounding box."""
        if self.bbox is None:
            self.bbox = (pnt[0], pnt[1], pnt[0], pnt[1])
        else:
            a, b, c, d = self.bbox
            if pnt[0] < a:
                a = pnt[0]
            elif pnt[0] > c:
                c = pnt[0]
            if pnt[1] < b:
                a = pnt[1]
            elif pnt[1] > d:
                d = pnt[1]
            self.bbox = (a, b, c, d)

    def down(self):
        """Start cutting (lower the knife)."""
        if not self.pos:
            raise ValueError('start cutting at unknown position')
        self.cut = True
        self._bbupdate(self.pos)
        self.commands += ['M14']

    def moveto(self, x, y):
        """
        Move the cutting head.

        The move is done from the current position to the indicated
        position in a straight line.

        Arguments:
            x: x coordinate in mm
            y: y coordinate in mm
        """
        x, y = mm2cin([x, y])
        if self.cut:  # We're cutting
            self._bbupdate((x, y))
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
        """Write the NC file."""
        self.__enter__()
        self.__exit__(None, None, None)

    def __enter__(self):
        """Start context manager."""
        self.f = open(self.path, 'wb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop context manager."""
        a, b, c, d = self.bbox
        li = abs(a-c)/100.0
        wi = abs(b-d)/100.0
        self.commands[2] = '{}/L={:.3f}/W={:.3f}'.format(self.name, li, wi)
        if self.commands[-1].startswith('N'):
            del self.commands[-1]  # Remove unnecessary newpiece()
        if not self.commands[-1] == 'M15':
            self.commands.append('M15')
        self.commands.append('M0')
        self.f.write('*'.join(self.commands).encode('utf-8'))
        self.f.write(b'*')
        self.f.close()


def mm2cin(arg):
    """
    Convert millimeters to 1/100 in.

    Arguments:
        arg: Number or sequence of numbers.

    Returns:
        Converted number or sequence.
    """
    if not type(arg) in [list, tuple]:
        return float(arg) * 100.0 / 25.4
    return [float(j) * 100.0 / 25.4 for j in arg]


def cin2mm(arg):
    """
    Convert 1/100 in to millimeters.

    Arguments:
        arg: Number or sequence of numbers.

    Returns:
        Converted number or sequence.
    """
    if not type(arg) in [list, tuple]:
        return float(arg) * 0.254
    return [float(j) * 0.254 for j in arg]


def segments(path):
    """
    Read a Gerber cloth cutter file and yield the line segments that it cuts.

    Arguments:
        path: The input file

    Yields:
        Lists of (x, y) tuples
    """
    downcmd = ('M14', 'B')
    upcmd = ('M15', 'A')
    stopcmd = ('M0', 'M00')
    with open(path) as df:
        data = df.read()
    items = data.split('*')
    if len(items[-1]) == 0:
        del items[-1]
    pos = (0, 0)
    segment = []
    down = False
    for cmd in items:
        if cmd in downcmd:
            down = True
            if not segment:
                segment = [pos]
            elif segment[-1] != pos and len(segment) > 1:
                yield segment
                segment = [pos]
        elif cmd in upcmd:
            down = False
        elif cmd in stopcmd:
            if segment and len(segment) > 1:
                yield segment
            return
        elif cmd.startswith('X'):
            x, y = cmd[1:].split('Y')
            x = round(float(x)*25.4/100, 0)
            y = round(float(y)*25.4/100, 0)
            pos = (x, y)
            if down:
                segment.append(pos)
