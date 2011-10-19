========
DXFtools
========

Introduction
============
The purpose of the 'dxfgerber' program is to generate optimized DXF files for
processing on a Gerber cutting machine. The software for this cutter is
apparently not very intelligent and doesn't seem able to sort line and arc
entities in a DXF file in a relevant order.

This software does two things;
  * Look for lines and arcs that fit end-to-end (contours) and write them out 
    in the correct order.
  * Sort contours, remaining lines and arc in ascending x-order of theeir
    bounding box.

