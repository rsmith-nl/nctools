What characterizes drawing/cutting elements?
============================================

* They have a start and end point
* They have a start and end direction.
* They may have intermediate points.

So we can have e.g.

line -> [start, end]
arc -> [start, center, end]
polyline -> [start, point, point, ..., end]


How do we find connected elements?
==================================

Suppose we have the following lines;

* L0 from P1 to P4
* L1 from P3 to P4
* L2 from P1 to P2
* L3 from P2 to P3
* L4 from P0 to P3

We can put this in a matrix like this;


M: P0 P1 P2 P3 P4
P0          L4 
P1       L2    L0
P2    L2    L3
P3 L4    L3    L1
P4    L0    L1

By moving horizontally and vertically through the matrix one can reconstruct
the connecting lines:

M: P0 P1 P2 P3 P4
P0--------->L4
P1       XX |  XX
P2    L2<---L3
P3 XX |  XX    XX
P4    L0--->L1

Let's make a dictionary of all points:

P0: [L4]
P1: [L0, L2]
P2: [L2, L3]
P3: [L1, L3, L4]
P4: [L0, L1]

We how create an empty list of points, and an empty list of lines.

Points: []
Contour: []

We start with P0 because this is the only point that is part of a single line.
L4 contains this point. We remove P0 from the dictionary, and put it in the
list of points. L4 is added to the contour.

Step 1
P1: [L0, L2]
P2: [L2, L3]
P3: [L1, L3, L4]
P4: [L0, L1]

Points: [P0]
Lines: [L4]

Which of the other points has L4? In this case P3. We remove it from the dict,
and add it to the list. P3 also is part of L1 (and L3 bit we'll skip that for now). So L1 is added to
the lines.

Step 2
P1: [L0, L2]
P2: [L2, L3]
P3: [L1, L3]
P4: [L0]

points: [P0, P3]
Lines: [L4, L1]


Step 3
P0: []
P1: [L2]
P2: [L2, L3]
P3: [L3]
P4: [L0]

points: [P0, P3, P4]
Lines: [L4, L1, L0]

Step 4
P0: [L2]
P1: []
P2: [L2, L3]
P3: [L3]

points: [P0, P3, P4, P1]
Lines: [L4, L1, L0, L2]

Step 5
points: [P0, P3, P4, P1, P2]
Lines: [L4, L1, L0, L2]

    In [22]: pl = [[random.randint(0, 100) for k in range(random.randint(1,4))] for n in range(30)]

    In [23]: pl
    Out[23]: [[40, 47, 97], [29, 50], [9, 85, 90, 69], [80, 27], [96, 25, 42, 56], [98, 96], [82, 44, 57, 6], [86], [28], [60, 51, 36], [50], [12, 38, 48], [26, 88], [22, 58], [18, 42], [30, 41, 73], [90, 24], [8, 44, 49], [53, 34, 47], [83], [20], [78, 60], [70, 72], [21], [65, 68, 3, 94], [0], [34, 5, 11, 69], [56, 98, 79, 79], [32, 89, 3], [69]]

    In [24]: [i for i in range(len(pl)) if len(pl[i]) == 1]
    Out[24]: [7, 8, 10, 19, 20, 23, 25, 29]

In [36]: pl[7]
Out[36]: [86]

In [37]: pl[7][0]
Out[37]: 86

