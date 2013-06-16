import nctools.dxf as dxf
from collections import Counter, defaultdict

rd = dxf.Reader('test/snijden-multimat1.dxf')
pc = Counter([e.startpoint for e in rd] + [e.endpoint for e in rd])
connections = [pnt for pnt, cnt in pc.iteritems() if cnt > 1]

starters = [e for e in rd if e.startpoint in connections or e.endpoint in
            connections]
inbetweens = [e for e in rd if e.startpoint in connections and e.endpoint in
              connections]


## OR

pnts = set([e.startpoint for e in rd] + [e.endpoint for e in rd])
pd = defaultdict(list)
for e in rd:
    pd[e.startpoint].append(e)
    pd[e.endpoint].append(e)

ends = [pnt for pnt in pd.keys() if len(pd[pnt]) == 1]
contours = []
for e in ends:
    contour = pd[e]
    start = e
    end = contour[-1].other(start)

