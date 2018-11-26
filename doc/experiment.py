from nctools import dxf

ents = dxf.reader('../test/test1.dxf')

from collections import defaultdict

d = defaultdict(list)

for e in ents:
    s, f = e.points
    d[s].append(e)
    d[f].append(e)

# All points that are in >1 lines.
[ln for k in d for ln in d[k] if len(d[k]) > 1]
