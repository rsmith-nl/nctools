# vim:fileencoding=utf-8
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Utilities for plotting."""

import nctools.ent as ent
import cairo

gamma = 0.8
maxc = 255


def wavelen2rgb(nm):  # pylint: disable=R0912
    """Convert a wavelength to an RGB tuple

    :param nm: wavelength in nanometers
    :returns: an RBG tuple
    """
    def adjust(color, factor):
        if color < 0.01:
            return 0
        rv = int(round(maxc * (color*factor)**gamma))
        if rv < 0:
            rv = 0
        elif rv > maxc:
            rv = maxc
        return rv
    # Clamp the wavelength
    if nm < 380:
        nm = 380
    elif nm > 780:
        nm = 780
    # Calculate intensities in the different wavelength bands.
    red, green, blue = 0.0, 0.0, 0.0
    if nm < 440:
        red = -(nm - 440.0) / (440.0 - 380.0)
        blue = 1.0
    elif nm < 490:
        green = (nm - 440.0) / (490.0 - 440.0)
        blue = 1.0
    elif nm < 510:
        green = 1.0
        blue = -(nm - 510.0) / (510.0 - 490.0)
    elif nm < 580:
        red = (nm - 510.0) / (580.0 - 510.0)
        green = 1.0
    elif nm < 645:
        red = 1.0
        green = -(nm - 645.0) / (645.0 - 580.0)
    else:
        red = 1.0
    # Let the intensity fall off near the vision limits.
    if nm < 420:
        factor = 0.3 + 0.7*(nm - 380.0) / (420.0 - 380.0)
    elif nm < 701:
        factor = 1.0
    else:
        factor = 0.3 + 0.7*(780.0 - nm) / (780.0 - 700.0)
    # Return the adjusted values
    return (adjust(red, factor), adjust(green, factor),
            adjust(blue, factor))


def crange(start, stop, count):
    """Create a list of colors

    :param start: starting wavelength
    :param stop: final wavelength
    :param count: length of the returned list
    :returns: a list of (R,G,B) tuples
    """
    if count == 1:
        return [wavelen2rgb(start)]
    step = (stop-start)/float(count-1)

    return [wavelen2rgb(start + j*step) for j in xrange(1, count+1)]


def plotgrid(context, width, height, size=100):
    """Plot a grid in black with a dotted line.

    :param context: Cairo context
    :param width: width of the context
    :param height: height of the context
    :param size: grid cell size
    """
    context.save()
    context.new_path()
    for x in xrange(100, int(width), size):
        context.move_to(x, 0)
        context.line_to(x, height)
    for y in xrange(int(height)-size, 0, -size):
        context.move_to(0, y)
        context.line_to(width, y)
    context.close_path()
    context.set_line_width(0.25)
    context.set_source_rgb(0.5, 0.5, 0.5)
    context.set_dash([20.0, 20.0])
    context.stroke()
    context.restore()


def plotentities(context, offset, entities, colors, lw=0.5):
    """Draw the entities

    :param context: Cairo context
    :param offset: tuple for translating the coordinate system
    :param entities: list of nctools.ent entities
    :param colors: list of (r,g,b) tuples or one (r,g,b) tuple
    :param lw: line width
    """
    if isinstance(colors, tuple) and len(colors) == 3:
        colors = [colors]*len(entities)
    elif len(colors) != len(entities):
        raise ValueError('the amount of colors should be equal to entities')
    context.save()
    context.set_line_width(lw)
    context.translate(offset[0], offset[1])
    for e, (r, g, b) in zip(entities, colors):
        context.new_path()
        context.set_source_rgb(r/255.0, g/255.0, b/255.0)
        if isinstance(e, ent.Arc):
            context.new_sub_path()
            a0 = e.a[0]
            a1 = e.a[1]
            if e.ccw:
                context.arc(e.cx, e.cy, e.R, a0, a1)
            else:
                context.arc_negative(e.xc, e.cy, e.R, a0, a1)
        # Line needs to go _last_ because all entities as subclasses of line!
        elif isinstance(e, ent.Line):
            s, x = e.points
            context.move_to(*s)
            context.line_to(*x)
        context.stroke()
    context.restore()


def plotcolorbar(context, width, nument, colors):
    """Plot a color bar

    :param context: Cairo context
    :param width: width of the canvas
    :param nument: number of entities
    :param colors: list of colors
    """
    sw = width/float(2*nument)
    context.set_line_cap(cairo.LINE_CAP_BUTT)
    context.set_line_width(sw)
    xs = 5
    for r, g, b in colors:
        context.set_source_rgb(r/255.0, g/255.0, b/255.0)
        context.move_to(xs, 5)
        context.rel_line_to(0, 5)
        context.stroke()
        xs += sw
