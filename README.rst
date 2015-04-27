NCtools
#######

:date: 2015-04-27
:author: Roland Smith


Introduction
============
These programs and modules were created because the existing software to
generate NC code for our gerber cloth cutter has some deficiencies.

Note that this software was _not_ written fot Gerber PCB milling machines! The
generated code was tested on a Gerber Garment Technology S-3000 cutter, with
the C-200MT controller software.

All programs use the `nctools` modules. The dxf submodule can extract LINE,
ARC, CIRCLE and POLYLINE entities from a DXF file. Note that it does *not*
handle other entities like BLOCK. The module _assumes_ that the units in the
file are millimeters. It also only writes nc code in centi-inches. All of
these programs require the Python interpreter. Currently both the ‘master’ and
‘develop’ branches use Python 3.

At this time these programs are going through a rewrite, done on the ‘develop’
branch.


General remarks about the programs
==================================
All these programs can read files in other directories. They will however only
write files in the current working directory. The output filename will be
generated from the input filename by removing any directories and the
extension. Where necessary, new extensions and/or modifiers are added. So an
input file '..\foo\bar.dxf' will generally result in an output file named
'bar' with the appropriate extension.

Those programs that produce output files in general all perform the following
actions:

* Read entities.
* Assemble connected entities into contours.
* Sort entities in by the minimum x value of their bounding box in ascending
  order.
* Move all entities so that the lower left corner for the bounding box
  for all entities is at (0,0).


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

These contours and any remaining lines and arcs are then sorted in ascending
order from the left edge of their bounding box.

The machine that these programs were originally written for is an older
machine, whose controllen doesn't even understand arcs, only straight lines.
So it also converts arcs into line segments. By default the length of these
segments is such that the deviation from the curve is not more than 1 mm. It
ignores the $MEASUREMENT variable in the dxf file because that is often not
set correctly and assumes that the units in the dxf file are millimeters.

Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. The readnc utility can be used to
display the file in a more human-readable format.

Usage: dxf2nc.py [file.dxf ...]

The software for our machine doesn't use extensions for nc files, so this
program just strips the dxf extension from the filename.


dxf2pdf
-------
This program reads a DXF file and generates a PDF file from it. This comes in
handy to view a PDF file. The lines, arcs and polylines from the DXF file are
shown on top of a 100x100 mm grid. The drawn elements are color coded to show
their sequence in the file.

Usage: dxf2pdf.py [file.dxf ...]

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

Usage: dxfgerber.py [file.dxf ...]

Since the output of this command is also a DXF file, the output filename has
'_mod' appended. So the input file 'baz.dxf' has the associated output file
'baz_mod.dxf'.


nc2pdf
------
This program reads a Gerber NC file and plots the cuts as a PDF. It assumes
units of 1/100 inch and only reads knife up/down and movements. It colors the
cuts to indicate their sequence in the nc file.

Usage: nc2pdf.py [file ...]

In this case, the output filename for the input file 'foo.nc' will be
'foo_nc.pdf'


dumpgerber.py
-------------
Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. This utility can be used to display the
file in a more human-readable format.

Usage: dumpgerber.py [file ...]

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

Usage: ./readdxf.py [file.dxf ...]

Example output::

    Filename: test/snijden-CSM1.dxf
    Contains: 444 entities
    Layer: "0"
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    INSERT entity
    Layer: "DIM"
    DIMENSION entity
    DIMENSION entity
    DIMENSION entity
    DIMENSION entity
    Layer: "CSM450"
    LINE from (784.44, 3360.90) to (1983.20, 3360.90)
    LINE from (1746.81, 3672.17) to (2007.21, 3672.17)
    LINE from (1983.20, 3360.90) to (1959.98, 3672.17)
    LINE from (1383.82, 4610.10) to (2007.21, 4610.10)
    LINE from (1383.82, 4610.10) to (1002.21, 4610.10)
    LINE from (2007.21, 4610.10) to (2007.21, 3672.17)
    LINE from (844.01, 4610.10) to (784.44, 3360.90)
    LINE from (1002.21, 4610.10) to (844.01, 4610.10)
    LINE from (1265.13, 4167.08) to (1507.00, 4167.08)
    LINE from (1472.62, 4378.83) to (1246.55, 4379.29)
    LINE from (1246.55, 4379.29) to (1265.13, 4167.08)
    LINE from (1497.34, 4351.15) to (1507.00, 4167.08)
    ...
