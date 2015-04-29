# file: test_dxfentities.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-16 12:31:50 +0200

"""Tests for dxfentities.py.

Run with the command: nosetests-3.4 -v test_dxfentities.py
"""

import os
import sys

bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
print('base path:', bp)
modpath = os.sep.join(bp + ['src', 'nctools'])
print('modpath:', modpath)
sys.path.append(modpath)

from dxfentities import read_entities

# De testen zijn in eerste instantie gegenereerd met de volgende code:
#
# import os
# dxf = [f for f in os.listdir() if f.endswith('.dxf')]
# for fn in dxf:
#     print('def test_{}():'.format(fn[:-4].replace('-', '_')))
#     print("    assert len(read_entities('{}')) > 0\n\n".format(fn))
#
# De hoeveelheid entiteiten is later aangepast aan de hand van de uitvoer van;
# ./readdxf test/*.dxf | & grep -E 'Filename:|Contains:'
# [0:00:00.02]: Filename: test/busgang-csm.dxf
# [0:00:00.02]: Contains: 387 entities
# [0:00:01.50]: Filename: test/busgang-mm.dxf
# [0:00:01.50]: Contains: 89 entities
# [0:00:01.55]: Filename: test/demo.dxf
# [0:00:01.55]: Contains: 16 entities
# [0:00:01.57]: Filename: test/doorsnede-proto11_2000.dxf
# [0:00:01.57]: Contains: 146 entities
# [0:00:01.68]: Filename: test/doorsnede-proto11_R14.dxf
# [0:00:01.68]: Contains: 146 entities
# [0:00:01.79]: Filename: test/drawingA.dxf
# [0:00:01.79]: Contains: 4 entities
# [0:00:01.82]: Filename: test/eindstuk_carrier.dxf
# [0:00:01.82]: Contains: 60 entities
# [0:00:01.92]: Filename: test/lapjes.dxf
# [0:00:01.92]: Contains: 870 entities
# [0:00:04.50]: Filename: test/opvulling.dxf
# [0:00:04.50]: Contains: 104 entities
# [0:00:04.56]: Filename: test/polyline.dxf
# [0:00:04.56]: Contains: 3 entities  ← houdt geen rekening met POLYLINE!
# [0:00:04.61]: Filename: test/revo_tt.dxf
# [0:00:04.61]: Contains: 8 entities
# [0:00:04.79]: Filename: test/snijbestand_carrier6_2.dxf
# [0:00:04.79]: Contains: 2074 entities
# [0:00:16.48]: Filename: test/snijtest-sirex.dxf
# [0:00:16.48]: Contains: 11 entities
# [0:00:16.60]: Filename: test/test1.dxf
# [0:00:16.60]: Contains: 22 entities
# [0:00:16.71]: Filename: test/vierkant100.dxf
# [0:00:16.71]: Contains: 4 entities ← houdt geen rekening met POLYLINE!
# [0:00:16.82]: Filename: test/vierkant100_afgerond.dxf
# [0:00:16.82]: Contains: 8 entities ← houdt geen rekening met POLYLINE!
# De rest van de bestanden gaf unicode fouten, en is dus met read_entities()
# in IPython getest.


def test_revo_tt():
    assert len(read_entities('revo_tt.dxf')) == 8


def test_drawingA():
    assert len(read_entities('drawingA.dxf')) == 4


def test_vierkant100():
    assert len(read_entities('vierkant100.dxf')) == 6


def test_doorsnede_proto11_2000():
    assert len(read_entities('doorsnede-proto11_2000.dxf')) == 146


def test_doorsnede_proto11_R14():
    assert len(read_entities('doorsnede-proto11_R14.dxf')) == 146


def test_test1():
    assert len(read_entities('test1.dxf')) == 22


def test_voorkant_hgz():
    assert len(read_entities('voorkant_hgz.dxf')) == 36


def test_busgang_csm():
    assert len(read_entities('busgang-csm.dxf')) == 387


def test_busgang_mm():
    assert len(read_entities('busgang-mm.dxf')) == 89


def test_snijtest_sirex():
    assert len(read_entities('snijtest-sirex.dxf')) == 11


def test_snijden_continuemat1():
    assert len(read_entities('snijden-continuemat1.dxf')) == 398


def test_snijden_multimat1():
    assert len(read_entities('snijden-multimat1.dxf')) == 73


def test_snijden_continuemat2():
    assert len(read_entities('snijden-continuemat2.dxf')) == 382


def test_snijden_multimat2():
    assert len(read_entities('snijden-multimat2.dxf')) == 93


def test_snijden_UNIE640():
    assert len(read_entities('snijden-UNIE640.dxf')) == 371


def test_snijden_CSM2():
    assert len(read_entities('snijden-CSM2.dxf')) == 412


def test_snijden_CSM1():
    assert len(read_entities('snijden-CSM1.dxf')) == 444


def test_vierkant100_afgerond():
    assert len(read_entities('vierkant100_afgerond.dxf')) == 10


def test_polyline():
    assert len(read_entities('polyline.dxf')) == 6


def test_eindstuk_carrier():
    assert len(read_entities('eindstuk_carrier.dxf')) == 60


def test_demo():
    assert len(read_entities('demo.dxf')) == 16


def test_lapjes():
    assert len(read_entities('lapjes.dxf')) == 870


def test_snijbestand_carrier6_2():
    assert len(read_entities('snijbestand_carrier6_2.dxf')) == 2074


def test_opvulling():
    assert len(read_entities('opvulling.dxf')) == 104
