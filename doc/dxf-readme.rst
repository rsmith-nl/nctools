Parsing DXF files with Python
#############################

:date: 2015-04-15
:tags: DXF, parsing, python
:author: Roland Smith

Introduction
============

The purpose of this document is to show how to parse DXF files with Python so
we can extract drawing entities like lines and arcs. This is *not* a complete
reference to the file format nor to all entities since a lot of data in the
file is irrelevant to our purpose and will be discarded.

File format
===========

See the `wikipedia article`_ on DXF for some background information.
Also the DXF reference_ (PDF) for AutoCAD2008 that is linked on that page

.. _wikipedia article: http://en.wikipedia.org/wiki/AutoCAD_DXF
.. _reference: http://images.autodesk.com/adsk/files/acad_dxf0.pdf

The DXF format is a *tagged* format, that is every data element in the file is
preceded in the file by an integer number that is its *group code*.
Every data element is given on its own line.

Reading
-------

So reading the elements and combining them with there group codes can be done
as follows.

.. code-block:: python

    In [1]: with open('lapjes.dxf') as dxffile:
        lines = dxffile.readlines()
    ...:

    In [2]: lines = [ln.strip() for ln in lines]

    In [3]: len(lines)
    Out[3]: 50966

    In [4]: data = list(zip(lines[::2], lines[1::2]))

    In [5]: data[:10]
    Out[5]:
    [('0', 'SECTION'),
    ('2', 'HEADER'),
    ('9', '$ACADVER'),
    ('1', 'AC1024'),
    ('9', '$ACADMAINTVER'),
    ('70', '63'),
    ('9', '$DWGCODEPAGE'),
    ('3', 'ANSI_1252'),
    ('9', '$LASTSAVEDBY'),
    ('1', 'Frans van der Weijst')]


Entities
--------

For the purpose of seing what is actually drawn, the only interesting section
of the file is the ENTITIES section. We can find the entities section and its
end by:

.. code-block:: python

    In [21]: [(n, d) for n, d in enumerate(data) if d[1] == 'ENDSEC']
    Out[21]:
    [(558, ('0', 'ENDSEC')),
    (641, ('0', 'ENDSEC')),
    (1167, ('0', 'ENDSEC')),
    (8856, ('0', 'ENDSEC')),
    (19379, ('0', 'ENDSEC')),
    (25481, ('0', 'ENDSEC'))]

    In [22]: [(n, d) for n, d in enumerate(data) if d[1] == 'ENTITIES']
    Out[22]: [(8859, ('2', 'ENTITIES'))]

    In [25]: entdata = data[8859:19379]

    In [26]: entdata[:25]
    Out[26]:
    [('0', 'LINE'),
    ('5', '7E5'),
    ('330', '1F'),
    ('100', 'AcDbEntity'),
    ('8', 'snij'),
    ('100', 'AcDbLine'),
    ('10', '-928.2789291041099'),
    ('20', '1442.556821161015'),
    ('30', '0.0'),
    ('11', '-958.2789291041098'),
    ('21', '1442.556821161015'),
    ('31', '0.0'),
    ('0', 'LINE'),
    ('5', '7E6'),
    ('330', '1F'),
    ('100', 'AcDbEntity'),
    ('8', 'snij'),
    ('100', 'AcDbLine'),
    ('10', '-928.2789291041099'),
    ('20', '1387.556821161014'),
    ('30', '0.0'),
    ('11', '-958.2789291041098'),
    ('21', '1387.556821161014'),
    ('31', '0.0'),
    ('0', 'LINE')]

Now would be a good time to change the group code into integers;

.. code-block:: python

    In [38]: entdata = [(int(g), d) for g, d in entdata]

    In [39]: entdata[:10]
    Out[39]:
    [(0, 'LINE'),
    (5, '7E5'),
    (330, '1F'),
    (100, 'AcDbEntity'),
    (8, 'snij'),
    (100, 'AcDbLine'),
    (10, '-928.2789291041099'),
    (20, '1442.556821161015'),
    (30, '0.0'),
    (11, '-958.2789291041098')]


So we need have taken data items 8859 up to 19379 as the data where our
entities are. As one can see, lines et cetera have group code 0. Let's find
all of those;

.. code-block:: python

    In [29]: [(n, d) for n, d in enumerate(entdata) if d[0] == '0'][:10]
    Out[29]:
    [(0, ('0', 'LINE')),
    (12, ('0', 'LINE')),
    (24, ('0', 'LINE')),
    (36, ('0', 'LINE')),
    (48, ('0', 'LINE')),
    (60, ('0', 'LINE')),
    (72, ('0', 'LINE')),
    (84, ('0', 'ARC')),
    (97, ('0', 'LINE')),
    (109, ('0', 'ARC'))]

Actually, we need the indices of the group code 0 to separate each entity;

.. code-block:: python

    In [40]: idx = [n for n, d in enumerate(entdata) if d[0] == 0]

    In [41]: len(idx)
    Out[41]: 870

    In [42]: idx[:10]
    Out[42]: [0, 12, 24, 36, 48, 60, 72, 84, 97, 109]

    In [43]: pairs = list(zip(idx, idx[1:]))

    In [44]: pairs[:10]
    Out[44]:
    [(0, 12),
    (12, 24),
    (24, 36),
    (36, 48),
    (48, 60),
    (60, 72),
    (72, 84),
    (84, 97),
    (97, 109),
    (109, 122)]

There is actually an error here; we need to append the length of the entdata
list to the idx list, otherwise we skip one entity! So;

.. code-block:: python

    idx = [n for n, d in enumerate(entdata) if d[0] == 0] + [len(entdata)]

Generating the pairs and the rest of the code goes as shown above.
Now we can group the entities together;

.. code-block:: python

    In [45]: entities = [dict(entdata[b:e]) for b, e in pairs]

    In [46]: entities[0]
    Out[46]:
    {0: 'LINE',
    100: 'AcDbLine',
    5: '7E5',
    31: '0.0',
    8: 'snij',
    20: '1442.556821161015',
    330: '1F',
    11: '-958.2789291041098',
    10: '-928.2789291041099',
    30: '0.0',
    21: '1442.556821161015'}

    In [47]: len(entities)
    Out[47]: 869

Note that the conversion to a dictionary *requires* that each group only
occurs once in an entity. This works fine.

Compare the first entity with the equivalent ``entdata``, in the sequence it
was given in the file;

.. code-block:: python

    In [49]: entdata[0:12]
    Out[49]:
    [(0, 'LINE'),
    (5, '7E5'),
    (330, '1F'),
    (100, 'AcDbEntity'),
    (8, 'snij'),
    (100, 'AcDbLine'),
    (10, '-928.2789291041099'),
    (20, '1442.556821161015'),
    (30, '0.0'),
    (11, '-958.2789291041098'),
    (21, '1442.556821161015'),
    (31, '0.0')]

From the group codes in the DXF reference;

    0
        Text string indicating the entity type

    8
        Layer name

    10, 20, 30
        Primary point X, Y and Z value. Floating point strings.

    11, 21, 31
        Secundary point X, Y and Z value. Floating point strings.

The remaining group codes are not relevant to our purpose.

Let's look at an arc;

.. code-block:: python

    In [58]: entities[7]
    Out[58]:
    {0: 'ARC',
    40: '215.1165613922064',
    50: '184.7895889379881',
    51: '199.8264426968666',
    100: 'AcDbArc',
    5: '7F2',
    8: 'snij',
    20: '1409.512744495635',
    330: '1F',
    10: '-375.6410358181863',
    30: '0.0'}

    In [59]: pairs[7]
    Out[59]: (84, 97)

    In [60]: entdata[84:97]
    Out[60]:
    [(0, 'ARC'),
    (5, '7F2'),
    (330, '1F'),
    (100, 'AcDbEntity'),
    (8, 'snij'),
    (100, 'AcDbCircle'),
    (10, '-375.6410358181863'),
    (20, '1409.512744495635'),
    (30, '0.0'),
    (40, '215.1165613922064'),
    (100, 'AcDbArc'),
    (50, '184.7895889379881'),
    (51, '199.8264426968666')]

From the group code reference;

    10, 20, 30
        Center of the arc.

    40
        Radius of the arc.

    50, 50
        Start and end angle in degrees.

The example file only has arcs and lines;

.. code-block:: python

    In [63]: {e[0] for e in entities}
    Out[63]: {'ARC', 'LINE'}

For polylines there is an additional grouping that must be done;
After a POLYLINE entity there will follow a number of VERTEX entities until
you get to a SEQEND entity. Below is an example of the ``entities`` of a DXF
containing a single polyline;

.. code-block:: python

    In [32]: entities
    Out[32]:
    [{0: 'POLYLINE', 66: '1', 20: '0.0', 5: '2BC', 8: '0', 10: '0.0',
      30: '0.0', 70: '0'},
    {0: 'VERTEX', 20: '0.0', 5: '302', 8: '0', 10: '0.0', 30: '0.0'},
    {0: 'VERTEX', 20: '100.0', 5: '303', 8: '0', 10: '100.0', 30: '0.0'},
    {0: 'VERTEX', 20: '100.0', 5: '304', 8: '0', 10: '200.0', 30: '0.0'},
    {0: 'VERTEX', 20: '0.0', 5: '305', 8: '0', 10: '200.0', 30: '0.0'},
    {0: 'SEQEND', 8: '0', 5: '306'}]

Notice that the primary point of the polyline is a dummy point; the X and Y
values are always 0. The group code 70 is important; its value is a bit-field
that can indicate;

1   This is a closed polyline (or a polygon mesh closed in the M direction).
2   Curve-fit vertices have been added.
4   Spline-fit vertices have been added.
8   This is a 3D polyline.
16  This is a 3D polygon mesh.
32  The polygon mesh is closed in the N direction.
64  The polyline is a polyface mesh.
128 The linetype pattern is generated continuously around the vertices polyline.

The default value is 0, which indicates an open polyline.
