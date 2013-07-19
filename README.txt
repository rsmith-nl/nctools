========
NCtools
========


Introduction
============
These programs and modules were created because the existing software to 
generate NC code for our gerber cloth cutter has some deficiencies.

Note that this software does _not_ deal with Gerber PCB milling machines!

All programs use the `nctools` modules. The dxf submodule can extract LINE,
ARC and POLYLINE entities from a DXF file. Note that it does *not* handle
other entities like BLOCK. The module _assumes_ that the units in the file are
millimeters. It also only writes nc code in centi-inches. All of these
programs require the Python 2.7 interpreter. They might work with Python 3.x
after conversion with 2to3 but that has not been tested.


The programs
============
All these programs can read files in other directories. They will however only
write files in the current working directory. The output filename will be
generated from the input filename by removing any directories and the
extension. Where necessary, new extensions are added. So an input file
'..\foo\bar.dxf' will generally result in an output file named 'bar' with the
appropriate extension.


dxf2nc
------
The cutworks software that comes with a gerber cutter doesn't
automatically optimize the cutting paths it reads from dxf files. It
essentially cuts lines in the order it finds them in the dxf file.

This program reads a dxf file. The name of the file must end in .dxf or .DXF
otherwise the program will report an error and quit. It extracts all the LINE,
ARC and POLYLINE entities from it It then searches through all these entities
and assembles connected entities into lists called contours. If necessary, the
direction of entities in a contour is changed so that all entities can be cut
in one continuous movement.

These contours and any remaining lines and arcs are then sorted in ascending
order from the left-bottom corner of their bounding box.

It also converts arcs into line segments. By default the length of these
segments is such that the deviation from the curve is not more than 1 mm. It
ignores the $MEASUREMENT variable in the dxf file because that is often not
set correctly and assumes that the units in the dxf file are millimeters.

Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. The ncfmt utility can be used to
display the file in a more human-readable format.

Usage: dxf2nc.py [file.dxf ...]


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


readnc 
------ 
Gerber numeric code files are basically text files but do not contain line
breaks, which makes them hard to read. This utility can be used to display the
file in a more human-readable format.

Usage: ncfmt.py [file ...]

Example output:

# Path: test/gerber-busgang-csm.nc
# Name of part: Bus-CSM2
# Length: 1600.0 mm, width 960.0 mm
newpiece() # 1
up()
moveto(0.0, 0.0)
down()
moveto(800.1, 0.0)
up()
down()
moveto(1599.9, 0.0)
up()
down()
moveto(1599.9, 960.1)
up()
down()
moveto(800.1, 960.1)
up()
...


readdxf
-------
Reads a DXF file and outputs the entities that it finds. This is more a
debugging tool than a really useful program.

Usage: ./readdxf.py [file.dxf ...]

Example output:

Filename: test/snijden-CSM1.dxf
Contains 103 entities
Extents: 784.4 ≤ x ≤ 10880.3, 3360.1 ≤ y ≤ 4610.1
<line from (784.440222017,3360.90245434) to (1983.19502279,3360.90245434), layer CSM450>
<line from (1746.80876285,3672.16739857) to (2007.21029717,3672.16739857), layer CSM450>
<line from (1983.19502279,3360.90245434) to (1959.98199674,3672.16739857), layer CSM450>
<line from (1383.8176224,4610.09630948) to (2007.21029717,4610.09630948), layer CSM450>
<line from (1383.8176224,4610.09630948) to (1002.20840991,4610.09630948), layer CSM450>
<line from (2007.21029717,4610.09630948) to (2007.21029717,3672.16739857), layer CSM450>
<line from (844.009099688,4610.09630948) to (784.440222017,3360.90245434), layer CSM450>
...

