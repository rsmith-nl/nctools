Principles of nctools
#####################

:date: 2015-11-14
:tags: 
:author: Roland Smith

.. Last modified: 2024-12-24T11:20:47+0100


.. PELICAN_END_SUMMARY

The main goal of these programs is to generate nc code for a Gerber S-3000
cutter with a GM200T controller. This is a very simple controller that can
basically only cut straight lines.
Modern Gerber machines still support this format.

DXF files contain a lot of information but only the geometric entities like
(poly)lines, circles and arcs are of interest. So other information will be
discarded. The information given is generally in the form of 3D coordinates,
with the lines et cetera implied between them.

Since the purpose of a cutter is to cut pieces out of a sheet of material we
are looking for sets of geometry that form closed contours. This can be done
algorithmically by tracing connected lines. Problems arise mainly when a point
if part of more than two entities. This happens e.g. when two contours share
a boundary to prevent extra cuts. In this case the program tracing a contour
doesn't know which next line to follow and it needs help from the drawing.
A design decision was to make each DXF layer which has a number in the layer
name correspond to a “piece” in the nc code. The rule is that while multiple
contours in a piece are allowed, they must be disjoint, i.e. not connected.


Piece numbers correspond to layer numbers, but are not identical. Suppose we
have the layers “layer 1”, “3 rd part”, “number 4”, “piece 7”, this gives the
number sequence 1, 3, 4, 7. This will be transformed to piece numbers 1, 2, 3,
4.

Pieces will be cut in ascending order. In a piece, contours will be drawn
sorted by their lower-left corner. The sorting is done first in x and then in
y. If there are multiple closed contours in a piece, the open contours and
lines that (partially) fall inside one of the closed contours are associated
with it.  The loose lines will be cut first, followed by the open contours and
last the closed contours.
