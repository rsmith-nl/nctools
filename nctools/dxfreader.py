# vim:fileencoding=utf-8:ft=python
# file: dxfreader.py
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2015-04-16T11:57:29 +0200
# Last modified: 2024-12-24T11:06:55+0100
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
# NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Module for retrieving the drawing entities from DXF files."""

import re


def parse(filename):
    """
    Read a DXF file and break it into (group, data) tuples.

    Arguments:
        filename: Name of a DXF file to read.

    Returns:
        A list of (group, data) tuples.
    """
    with open(filename, encoding="cp1252") as dxffile:
        lines = dxffile.readlines()
    lines = [ln.strip() for ln in lines]
    data = list(zip(lines[::2], lines[1::2]))
    return [(int(g), d) for g, d in data]


def entities(data):
    """
    Isolate the entity data from a list of (group, data) tuples.

    Arguments:
        data: Input list of DXF (group, data) tuples.

    Returns:
        A list of drawing entities, each as a dictionary
        keyed by group code.
    """
    soe = [n for n, d in enumerate(data) if d[1] == "ENTITIES"][0]
    eoe = [n for n, d in enumerate(data) if d[1] == "ENDSEC" and n > soe][0]
    entdata = data[soe + 1 : eoe]
    idx = [n for n, d in enumerate(entdata) if d[0] == 0] + [len(entdata)]
    pairs = list(zip(idx, idx[1:]))
    entities = [tuple(entdata[b:e]) for b, e in pairs]
    return entities


def layername(ent):
    """Get the layer name of an entity."""
    return [v for k, v in ent if k == 8][0]


def bycode(ent, group):
    """
    Get the data with the given group code from an entity.

    Arguments:
        ent: An iterable of (group, data) tuples.
        group: Group code that you want to retrieve.

    Returns:
        The data for the given group code. Can be a list of items if the group
        code occurs multiple times.
    """
    data = [v for k, v in ent if k == group]
    if len(data) == 1:
        return data[0]
    return data


def layernames(entities):
    """
    Get all layer names from the entities.

    Arguments:
        entities: An iterable if dictionaries, each containing a DXF entity.

    Returns:
        A sorted list of layer names.
    """
    lnames = list(set(layername(e) for e in entities))
    lnames.sort()
    return lnames


def numberedlayers(entities):
    """
    Get layer names from entities that contain a number, except for layer 0.

    Arguments:
        entities: An iterable of dictionaries, each containing a DXF entity.

    Returns:
        A list of layer names with a number in them, sorted by ascending
        number.
    """
    layers = layernames(entities)
    numbered = [ln for ln in layers if len(re.findall(r"[1-9]\d*", ln)) == 1]
    numbered.sort(key=lambda ln: int(re.search(r"[1-9]\d*", ln).group()))
    return numbered


def fromlayer(entities, name):
    """
    Return only the entities from the named layer.

    Arguments:
        entities: An iterable of dictionaries, each containing a DXF entity.
        name: The name of the layer to filter on.

    Returns:
        A list of entities.
    """
    return [e for e in entities if layername(e) == name]
