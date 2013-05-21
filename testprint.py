import dxfgeom
from math import fabs

def peq(j, k):
    lim = 1e-4
    dx = fabs(j[0]-k[0]) < lim
    dy = fabs(j[1]-k[1]) < lim
#    dx = j[0] == k[0]
#    dy = j[1] == k[1]
    return dx and dy

def pp(p):
    print '({:.3f},{:.3f})'.format(p[0], p[1]),

ent = dxfgeom.read_entities('test/Snijbestand 6 carrier Assy v2.dxf')
lo = dxfgeom.find_entities("LINE", ent)
lines = [dxfgeom.line_from_elist(ent, nn) for nn in lo]
ao = dxfgeom.find_entities("ARC", ent)
arcs = [dxfgeom.arc_from_elist(ent, m) for m in ao]
q = arcs[0]
print q.cx, q.cy, q.R, q.a1, q.a2, q.x1, q.y1, q.x2, q.y2
with open('arcs.txt', 'w+') as of:
    for a in arcs:
        a.segments = a._gensegments() #pylint: disable=W0212
        p1 = (a.x1, a.y1)
        p2 = (a.x2, a.y2)
        p3 = (a.segments[0].x1, a.segments[0].y1)
        p4 = (a.segments[0].x2, a.segments[0].y2)
        p5 = (a.segments[-1].x1, a.segments[-1].y1)
        p6 = (a.segments[-1].x2, a.segments[-1].y2)
        if not (peq(p1, p3) or peq(p1, p4)):
            print a
            print "Startpunt komt niet overeen"
            pp(p3)
            pp(p4)
            print
        if not (peq(p2, p5) or peq(p2, p6)):
            print a
            print "Eindpunt komen niet overeen!"
            pp(p5)
            pp(p6)
            print

