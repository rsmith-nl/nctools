#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Optimizes lines and arcs from a DXF file for cutting on a Gerber cutter,
# outputs another DXF file.
#
# Copyright © 2011-2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

import sys 
from nctools import bbox, dxf, ent, utils

__proginfo__ = ('dxfgerber [ver. ' + 
                '$Revision$'[11:-2] + '] (' + 
                '$Date$'[7:-2]+')')


def main(argv):
    """Main program for the dxfgerber utility.
    
    :argv: command line arguments
    """
    if len(argv) == 1:
        print __proginfo__
        print "Usage: {} [dxf-file ...]".format(argv[0])
        sys.exit(1)
    del argv[0]
    for f in argv:
        try:
            ofn = utils.outname(f, extension='.dxf', addenum='_mod')
            entities = dxf.Reader(f)
        except Exception as e: #pylint: disable=W0703
            utils.skip(e, f)
            continue
        num = len(entities)
        print 'Filename:', f
        if num == 0:
            print 'No entities found!'
            sys.exit(1)
        if num > 1:
            print 'Contains: {} entities'.format(num)
            bbe = [e.bbox for e in entities]
            bb = bbox.merge(bbe)
            contours, rement = ent.findcontours(entities)
            ncon = 'Found {} contours, {} remaining single entities'
            print ncon.format(len(contours), len(rement))
            entities = contours + rement
            entities.sort(key=lambda x: x.bbox.minx)
        else:
            print 'Contains: 1 entity'
            bb = entities[0].bbox
        es = 'Extents: {:.1f} ≤ x ≤ {:.1f}, {:.1f} ≤ y ≤ {:.1f}'
        print es.format(bb.minx, bb.maxx, bb.miny, bb.maxy)
        dxf.Writer(ofn, entities)


if __name__ == '__main__':
    main(utils.xpand(sys.argv))
