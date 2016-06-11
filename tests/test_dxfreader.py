# file: test-dxfreader.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-03-28 01:44:10 +0200
# Last modified: 2016-06-11 13:37:10 +0200

"""Tests for the dxfreader module."""

import sys

sys.path.insert(1, 'src')

from nctools import dxfreader as dxf  # noqa

data = []
ents = []
names = []


def test_parse():
    global data
    data = dxf.parse('testfiles/demo.dxf')
    assert len(data) == 4768
    assert data[0] == (0, 'SECTION')
    assert data[-1] == (0, 'EOF')


def test_entities():
    global ents
    ents = dxf.entities(data)
    start = ((0, 'LINE'), (5, '359'), (330, '475'), (100, 'AcDbEntity'),
             (8, 'deel 1'), (100, 'AcDbLine'), (10, '999.9999999999984'),
             (20, '100.0'), (30, '0.0'), (11, '1100.0'), (21, '100.0'),
             (31, '0.0'))
    end = ((0, 'LINE'), (5, '37A'), (330, '475'), (100, 'AcDbEntity'),
           (8, 'deel 1'), (100, 'AcDbLine'), (10, '999.9999999999982'),
           (20, '575.0'), (30, '0.0'), (11, '999.9999999999982'),
           (21, '600.0'), (31, '0.0'))
    assert len(ents) == 16
    assert ents[0] == start
    assert ents[-1] == end


def test_layernames():
    global names
    names = dxf.layernames(ents)
    assert names == ['deel 1']


def test_numberedlayers():
    numnames = dxf.numberedlayers(ents)
    assert numnames == ['deel 1']
