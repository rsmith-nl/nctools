========
DXFtools
========

Introduction
============
These programs were created because the existing software to generate NC code
for our gerber cutter was somewhat clunky and unsophisticated.

All programs use the `dxfgeom` module. This module can extract only LINE and
ARC entities from a DXF file. Note that it does *not* handle other entities
like BLOCK or POLYLINE. The module _assumes_ that the units in the file are
millimeters.

The programs
============

dxf2nc
------
This program reads a DXF file and generates NC code for a Gerber cutter. It
was written for an older model that does not know how to cut in an arc. So
arcs are approximated as line segments. It assembles connected lines/arcs into
contours that are cut in one go without lifting the knife.

dxf2pdf
-------
This program reads a DXF file and generates a PDF file from it. This comes in
handy to view a PDF file. The lines and arcs from the DXF file are shown on
top of a 100x100 mm grid.

dxfgerber
---------
This was the original program to optimize DXF files for use with the Gerber
software. It assembles connected lines/arcs into contours so that the cutter
won't jump all over the part.

nc2pdf
------
This program reads a Gerber NC file and plots the cuts as a PDF. It assumes
units of 1/100 inch and only reads like knife up/down and movements.

ncfmt
-----
This program reads a Gerber NC file outputs it in a more human-readable
manner.

readdxf
-------
Reads a DXF file and outputs the entities that it finds.

