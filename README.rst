README for NCtools
##################

:modified: 2018-11-26
:date: 2018-01-23
:author: Roland Smith

.. note:: As of November 2018, the Gerber cloth cutter for which I wrote these
   programs is being retired. As a consequence, I will not spend a lot of time
   improving the programs anymore, and the github repo will be archived.


Introduction
============
These programs and modules were created because the existing software to
generate NC code for our gerber cloth cutter has some deficiencies.

Note that this software was _not_ written for Gerber PCB milling machines! The
generated code was tested on a Gerber Garment Technology S-3000 cutter, with
the C-200MT controller software.

Most programs use the ``nctools`` modules. The dxfreader submodule can extract LINE,
ARC, CIRCLE and POLYLINE entities from a DXF file. Note that it does *not*
handle other entities like BLOCK. The module _assumes_ that the units in the
file are millimeters. It also only writes nc code in centi-inches.

At this time these programs are going through a rewrite, done on the ‘develop’
branch.


Requirements
============
* Python 3. (Developed with Python 3.4 and 3.5)
* the ``cairo`` library and its python bindings for ``dxf2pdf`` and ``nx2pdf``


Installation
============

Run ``./setup.py install``.


General remarks about the programs
==================================
These programs are command-line utilities. There are no GUI front-ends planned
at the moment.

All these programs can read files in other directories. They will however only
write files in the current working directory. The output filename will be
generated from the input filename by removing any directories and the
extension. Where necessary, new extensions and/or modifiers are added. So an
input file '..\foo\bar.dxf' will generally result in an output file named
'bar' with the appropriate extension.

To try the programs without installing them, run::

    python3 -m nctools.<program> <arguments>

from the root directory of the repository. Every program supports the ``-h``
or ``--help`` options for an overiew of the arguments and usage.

dxf2nc
------
The cutworks software that comes with a gerber cutter doesn't
automatically optimize the cutting paths it reads from dxf files. It
essentially cuts lines in the order it finds them in the dxf file.

This program reads a dxf file. The name of the file must end in .dxf or .DXF
otherwise the program will report an error and quit. It extracts all the LINE,
ARC and POLYLINE entities from it. It then searches through all these entities
and assembles connected entities into lists called contours. If necessary, the
direction of entities in a contour is changed so that all entities can be cut
in one continuous movement.

These contours and any remaining lines and arcs are then sorted as given by
the options. The default is to sort first in ascending x and then in ascending
y.

The machine that these programs were originally written for is an older
machine, whose controllen doesn't even understand arcs, only straight lines.
So it also converts arcs into line segments. By default the length of these
segments is such that the deviation from the curve is not more than 0.5 mm. It
ignores the $MEASUREMENT variable in the dxf file because that is often not
set correctly and assumes that the units in the dxf file are millimeters.

Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. The ``readnc`` utility can be used to
display the file in a more human-readable format.

The software for our machine doesn't use extensions for nc files, so this
program just strips the dxf extension from the filename.


dxf2pdf
-------
This program reads a DXF file and generates a PDF file from it. This comes in
handy to view a PDF file. The lines, arcs and polylines from the DXF file are
shown on top of a 100x100 mm grid. Optionally the beginning and ending of
lines are marked.

In this case, the output filename for the input file 'foo.dxf' will be
'foo_dxf.pdf'


dxfgerber
---------
The cutworks software that comes with a gerber cutter doesn't
automatically optimize the cutting paths it reads from dxf files. It
essentially cuts lines in the order it finds them in the dxf file. This was
the original program to optimize DXF files for use with the Gerber software.
It assembles connected lines/arcs into contours so that the cutter won't jump
all over the part. The dxf2nc program is intended as its replacement.

Since the output of this command is also a DXF file, the output filename has
'_mod' appended. So the input file 'baz.dxf' has the associated output file
'baz_mod.dxf'.


nc2pdf
------
This program reads a Gerber NC file and plots the cuts as a PDF. It assumes
units of 1/100 inch and only reads knife up/down and movements. It colors the
cuts to indicate their sequence in the nc file.

In this case, the output filename for the input file 'foo.nc' will be
'foo_nc.pdf'


dumpgerber.py
-------------
Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. This utility can be used to display the
file in a more human-readable format.

Example output::

    /Reading file 'test/gerber-busgang-csm.nc'./
    /This file contains 1549 blocks./
    H1                   /file #1/
    M20                  /message/
    Bus-CSM2/L=62.992/W=37.795
    N1                   /piece #1/
    M15                  /knife up/
    X0Y0                 /move to x = 0 mm, y = 0 mm/
    M14                  /knife down/
    X3150Y0              /move to x = 800 mm, y = 0 mm/
    M15                  /knife up/
    M14                  /knife down/
    X6299Y0              /move to x = 1600 mm, y = 0 mm/
    M15                  /knife up/
    M14                  /knife down/
    X6299Y3780           /move to x = 1600 mm, y = 960 mm/
    M15                  /knife up/
    ...


readdxf
-------
Reads a DXF file and outputs the entities that it finds. This is more of a
debugging tool for the nctools module than a really useful program. It
gathers entities into contours for testing purposes of that functionality. A
visual alternative would be to use dxf2pdf.

Example output::

    Filename: testfiles/snijden-CSM1.dxf
    Contains: 425 entities
    Layer: "deel 1"
    LINE from (0.00, 0.00) to (1198.75, 0.00)
    LINE from (962.37, 311.26) to (1222.77, 311.26)
    LINE from (1198.75, 0.00) to (1175.54, 311.26)
    LINE from (599.38, 1249.19) to (1222.77, 1249.19)
    LINE from (599.38, 1249.19) to (217.77, 1249.19)
    LINE from (1222.77, 1249.19) to (1222.77, 311.26)
    LINE from (59.57, 1249.19) to (0.00, 0.00)
    LINE from (217.77, 1249.19) to (59.57, 1249.19)
    LINE from (480.69, 806.18) to (722.56, 806.18)
    LINE from (688.18, 1017.93) to (462.11, 1018.39)
    LINE from (462.11, 1018.39) to (480.69, 806.18)
    LINE from (712.90, 990.25) to (722.56, 806.18)
    POLYLINE
        VERTEX at (712.90, 990.25)
        VERTEX at (712.89, 990.49)
        VERTEX at (712.87, 990.74)
        VERTEX at (712.85, 990.99)
        ...
        VERTEX at (688.42, 1017.89)
        VERTEX at (688.18, 1017.93)
    ENDSEQ
    LINE from (811.74, 1141.23) to (387.01, 1141.23)
    LINE from (387.01, 641.28) to (811.74, 641.28)
    LINE from (256.88, 1011.10) to (256.88, 771.40)
    LINE from (941.88, 771.40) to (941.88, 1011.10)
    ARC from (387.01, 1141.22) to (256.88, 1011.10)
        centered at (387.01, 1011.09), radius 130.13, from 90.0° to 180.0°
    ARC from (256.88, 771.40) to (387.01, 641.28)
        centered at (387.01, 771.41), radius 130.13, from 180.0° to 270.0°
    ...


Developers
==========

You will need py.test_ to run the provided tests. Code checks are done using
pylama_. Both should be invoked from the root directory of the repository.

.. _py.test: https://docs.pytest.org/
.. _pylama: http://pylama.readthedocs.io/en/latest/
