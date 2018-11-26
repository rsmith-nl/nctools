Specification for nctools
#########################

:date: 2015-11-11
:tags: 
:author: Roland Smith

.. Last modified: 2015-11-12 00:38:30 +0100


.. PELICAN_END_SUMMARY

Introduction
============

The main purpose of these programs is to read geometric data in DXF format and
generate NC code for a Gerber S-3000 cutter with a C-200MT.


NC format
=========

In short, the S-3000 cutter has a command for movements in the XY plane. It
also has commands for lowering or raising the nife. Movement with the knife
lowered is cutting.

The cuts can be grouped into pieces, identified by a number. Pieces are cut in
ascending order.

My original intent was to find closed loops and treat them as pieces. Sometimes
this is obvious; if a point only occurs in two lines, then it is a connection
between them. If you follow connections from a point and end up in the same
point, we have a closed loop. But if several lines meet in one point (or if
lines cross) there is ambiguity in the intent.

DXF format
==========

A DXF file contains drawing entities and other information. For our purpose we
are only interested in the drawing entities. Other information will be
discarded. This software will handle LINE, ARC, CIRCLE and POLYLINE entities.
Support for other entities may be added later.

Considerations
==============

My current notion is to use the layers in the DXF file as piece numbers in the
nc code. Layers that contain parts are indicated by names that have a positive
integer number (as in a string of digits) in them. Except for layer 0, that
will be ignored since it is a catch-all layer. So valid part layer names are:

* 'layer 1'
* 'part3'
* '42 head-end'

The following are *invalid*:

* 'part 3 of 7' (>1 separate number)
* 'piece four' (not a number)

Note that the layer names 'layer 6' and '6th part' *both* contain the same
number. These layers will both be considered as piece 6.

The layer numbers which are used as piece numbers are used as helpers for the
conversion.

Consider the case where we have four points forming a rectangle of four lines.
One of the points is also part of another string of lines. The rectangle and
the string of lines should be grouped into different numbered layers to make
clear which ones go together as a piece.

Within each numbered layer (i.e. piece), the programs look for strings of
connected entities. Each of these will be grouped into an object which is in
essence a list of points. Let's call this object a “LineList”.  Such a list
should have at least two points (a line segment) or more (a string of
connected line segments). Entities that are not connected will form a single
object. Lists with more than two points can have a "closed" attribute,
indicating that the first and last point are connected. The LineLists are used
to generate nc code. They will be processed layer by layer. To remove this amiguity
only one multi-segment linelist is allowed per layer.



