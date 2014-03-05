#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Reads DXF files and re-orders the entities so that entities that fit
together are stored as a chain in the output DXF file."""

import argparse
import sys
from nctools import bbox, dxf, ent, utils

_proginfo = ('dxfgerber [ver. ' +
             '$Revision$'[11:-2] + '] (' +
             '$Date$'[7:-2]+')')


def main(argv):
    """Main program for the dxfgerber utility.

    :argv: command line arguments
    """
    msg = utils.Msg()
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = """maximum distance between two points considered equal when
    searching for contours (defaults to 0.5 mm)"""
    parser.add_argument('-l', '--limit', nargs=1, help=argtxt, dest='limit',
                        metavar='F', type=float, default=0.5)
    parser.add_argument('-v', '--version', action='version',
                        version=_proginfo)
    parser.add_argument('files', nargs='*', help='one or more file names',
                        metavar='file')
    pv = parser.parse_args(argv)
    lim = pv.limit**2
    if not pv.files:
        parser.print_help()
        sys.exit(0)
    for f in utils.xpand(pv.files):
        msg.say('Starting file "{}"'.format(f))
        try:
            ofn = utils.outname(f, extension='.dxf', addenum='_mod')
            entities = dxf.reader(f)
        except Exception as e:  # pylint: disable=W0703
            utils.skip(e, f)
            continue
        num = len(entities)
        if num == 0:
            msg.say('No entities found!')
            continue
        if num > 1:
            msg.say('Contains {} entities'.format(num))
            bbe = [e.bbox for e in entities]
            bb = bbox.merge(bbe)
            msg.say('Gathering connected entities into contours')
            contours, rement = ent.findcontours(entities, lim)
            ncon = 'Found {} contours, {} remaining single entities'
            msg.say(ncon.format(len(contours), len(rement)))
            entities = contours + rement
            msg.say('Sorting entities')
            entities.sort(key=lambda e: (e.bbox.minx, e.bbox.miny))
        else:
            msg.say('Contains: 1 entity')
            bb = entities[0].bbox
        es = 'Original extents: {:.1f} ≤ x ≤ {:.1f} mm,' \
             ' {:.1f} ≤ y ≤ {:.1f} mm'
        msg.say(es.format(bb.minx, bb.maxx, bb.miny, bb.maxy))
        # move entities so that the bounding box begins at 0,0
        if bb.minx != 0 or bb.miny != 0:
            ms = 'Moving all entities by ({:.1f}, {:.1f}) mm'
            msg.say(ms.format(-bb.minx, -bb.miny))
            for e in entities:
                e.move(-bb.minx, -bb.miny)
        length = sum(e.length for e in entities)
        msg.say('Total length of entities: {:.0f} mm'.format(length))
        msg.say('Writing output to "{}"'.format(ofn))
        dxf.writer(ofn, 'dxfgerber', entities)
        msg.say('File "{}" done.'.format(f))


if __name__ == '__main__':
    main(sys.argv[1:])
