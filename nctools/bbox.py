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

"""A bounding box"""

__version__ = '$Revision$'[11:-2]


class BBox(object):

    def __init__(self):
        self._empty = True
        self.xmin, self.xmax = None, None
        self.ymin, self.ymax = None, None

    def __repr__(self):
        if self.empty:
            return '<BBox (empty)>'
        s = '<BBox xmin={}, xmax={}, ymin={}, ymax={}>'
        return s.format(self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def empty(self):
        return self._empty

    def addp(self, arg):
        """Add points to the bounding box

        :arg: a 2-tuple point, or a list of 2-tuples
        """
        if len(arg) == 2 and (isinstance(arg[0], int) or 
                              isinstance(arg[0], float)):
            arg = [arg]
        x = [i for i, _ in arg]
        y = [j for _, j in arg]
        if self._empty:
            self.xmin, self.xmax = x[0], x[0]
            self.ymin, self.ymax = y[0], y[0]
            self._empty = False
        self.xmin = min(x + [self.xmin])
        self.xmax = max(x + [self.xmax])
        self.ymin = min(y + [self.ymin])
        self.ymax = max(y + [self.ymax])

    def merge(self, other):
        """Merge other box(es) into this one.

        :other: BBox or list of BBox-es
        """
        if isinstance(other, BBox):
            other = [other]
        elif not type(other) in [list, tuple]:
            raise ValueError('Oither must be a BBox or a list/tuple of them')
        if self._empty:
            self.xmin, self.xmax = other[0].xmin, other[0].xmax
            self.ymin, self.ymax = other[0].ymin, other[0].ymax
            self._empty = False
        self.xmin = min([a.xmin for a in other] + [self.xmin])
        self.xmax = max([a.xmax for a in other] + [self.xmax])
        self.ymin = min([a.ymin for a in other] + [self.ymin])
        self.ymax = max([a.ymax for a in other] + [self.ymax])


# Built-in test.
if __name__ == '__main__':
    pass
