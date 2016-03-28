# file: test-lines.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-03-28 12:45:47 +0200
# Last modified: 2016-03-28 13:22:21 +0200

"""Tests for the lines module.

Run from the tests directory with: nosetests-3.5 -v test-lines.py"""

import pathmagic
from nctools import lines


def test_mksegments_line():
    entities = [((0, 'LINE'), (5, '359'), (330, '475'), (100, 'AcDbEntity'),
                (8, 'deel 1'), (100, 'AcDbLine'), (10, '999.9999999999984'),
                (20, '100.0'), (30, '0.0'), (11, '1100.0'), (21, '100.0'),
                (31, '0.0')),
                ((0, 'LINE'), (5, '35A'), (330, '475'), (100, 'AcDbEntity'),
                (8, 'deel 1'), (100, 'AcDbLine'), (10, '1100.0'),
                (20, '100.0'), (30, '0.0'), (11, '1100.0'), (21, '600.0'),
                (31, '0.0')),
                ((0, 'LINE'), (5, '35B'), (330, '475'), (100, 'AcDbEntity'),
                (8, 'deel 1'), (100, 'AcDbLine'), (10, '1100.0'),
                (20, '600.0'), (30, '0.0'), (11, '1000.0000001'),
                (21, '600.0'), (31, '0.0'))]
    segments = lines.mksegments(entities)
    assert segments == [[(1000, 100), (1100, 100)], [(1100, 100), (1100, 600)],
                        [(1100, 600), (1000, 600)]]


def test_mksegments_arc():
    arc = [((0, 'ARC'), (5, '35F'), (330, '475'), (100, 'AcDbEntity'),
           (8, 'deel 1'), (100, 'AcDbCircle'), (10, '900.0'),
           (20, '349.9999999999998'), (30, '0.0'), (40, '800.0'),
           (100, 'AcDbArc'), (50, '169.1930771251396'),
           (51, '190.8069228748603'))]
    rv = lines.mksegments(arc)
    ev = [[(114.19, 500), (103.55, 425.33), (100, 350), (103.55, 274.67),
           (114.19, 200)]]
    assert rv[0] == ev[0]


def test_combine_segments():
    segments = [[(0, 0), (100, 0)], [(0, 50), (50, 0)], [(100, 0), (100, 100)],
                [(100, 100), (0, 100)], [(0, 100), (0, 0)]]
    rv = lines.combine_segments(segments)
    ev = ([[(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]],
          [[(0, 50), (50, 0)]])
    assert rv[0][0] == ev[0][0]
    assert rv[1][0] == ev[1][0]


def test_closed():
    segment = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
    assert lines.closed(segment) is True


def test_length():
    openseg = [(0, 0), (100, 0), (100, 100)]
    closedseg = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
    assert lines.length(openseg) == 200
    assert lines.length(closedseg) == 400


def test_setstart():
    closedseg = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
    lines.setstart(closedseg, (100, 100))
    ev = [(100, 100), (0, 100), (0, 0), (100, 0), (100, 100)]
    assert closedseg == ev
