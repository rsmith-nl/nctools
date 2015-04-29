points = [(1.0, 2.0), (3.0, 1.0), (1.0, 1.0), (2.0, 2.0), (4.0, 2.0)]
lines = [(points[1], points[4]), (points[3], points[4]),
         (points[1], points[2]), (points[2], points[3]),
         (points[0], points[3])]

xrefs = {p: [l for l in lines if p in l] for p in points}
starts = [k for k in xrefs.keys() if len(xrefs[k]) == 1]

cp = []
cl = []
for p in starts:
    cp.append(p)
    cl.append(xrefs[p][0])
    del xrefs[p]
    while xrefs:
        for k in xrefs.keys():
            if len(xrefs[k]) == 0:
                del xrefs[k]
                continue
            if cl[-1] in xrefs[k]:
                xrefs[k].remove(cl[-1])
                cp.append(k)
                if len(xrefs[k]) > 0:
                    cl.append(xrefs[k].pop(0))
                p = k
                break
