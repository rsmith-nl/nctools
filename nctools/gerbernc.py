#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

"""Classes for reading and writing Gerber NC files"""

import bbox
import os.path as op

__version__ = '$Revision$'[11:-2]


class Reader(object):
    """Reads a subset of Gerber NC files. It assumes coordinates in
    centi-inches format.
    """

    cmds = {'M0': 'end of file', 'M00': 'program stop', 
            'M01': 'optional stop', 'M14': 'knife down', 'M15': 'knife up'} 

    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            c = f.read().split('*')
        if c[0] != 'H1' and c[1] != 'M20':
            raise ValueError('{} is not a valid NC file.'.format(path))
        ident = c[2].split('/')
        del c[0:3]
        self.name = ident[0]
        self.length = float(ident[1][2:])/25.4
        self.width = float(ident[2][2:])/25.4
        self.commands = c
        self.pos = None

    def __iter__(self):
        for c in self.commands:
            if c in Reader.cmds.keys():
                yield Reader.cmds[c]
                if c == 'M0':
                    raise StopIteration
            elif c.startswith('N'):
                idx = int(c[1:])
                yield 'piece #{}'.format(idx)
            elif c.startswith('X'):
                coords = c[1:].split('Y')
                x, y = [float(c) * 25.4 / 100.0 for c in coords]

                yield 'move to {:.1f}, {:.1f}'.format(x, y)
            else:
                yield 'unknown command: "{}"'.format(c)


class Writer(object):
    """Writes Gerber NC files.
    """

    def __init__(self, path, name=None):
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
        self.currpos = None
        self.bbox = bbox.BBox()
        self.f = None
        # commands[2] is an empty placeholder. The name, length and width of
        # the program need to be put there before writing.
        self.commands = ['H1', 'M20', '', 'N1', 'M15']

    def __str__(self):
        return '*'.join(self.commands)

    def up(self):
        """Stop cutting.
        """
        self.cut = False
        self.commands += ['M15']

    def down(self):
        """Start cutting.
        """
        if not self.currpos:
            raise ValueError('start cutting at unknown position')
        self.cut = True
        self.bbox.addp(self.currpos)
        self.commands += ['M14']

    def moveto(self, x, y):
        """Move the cutting head to the indicated position.

        :x: x coordinate in mm
        :y: y coordinate in mm
        """
        x = float(x) * 100.0 / 25.4
        y = float(y) * 100.0 / 25.4
        if self.cut: # We're cutting
            self.bbox.addp((x, y))
        self.commands += ['X{:.0f}Y{:.0f}'.format(x, y)]
        self.currpos = (x, y)
#        print 'currpos:', self.currpos

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
        li = (self.bbox.xmax - self.bbox.xmin)/100.0
        wi = (self.bbox.ymax - self.bbox.ymin)/100.0
        self.commands[2] = '{}/L={:.3f}/W={:.3f}'.format(self.name, li, wi)
        if not self.commands[-1] == 'M15':
            self.commands.append('M15')
        self.commands.append('M0')
        self.f.write('*'.join(self.commands))
        self.f.close()


# Built-in test.
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
        print w

    rd = Reader(nm)
    for cmd in rd:
        print cmd

    remove(nm)

