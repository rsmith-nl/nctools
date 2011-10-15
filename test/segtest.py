# Local module.
import dxfgeom

a = dxfgeom.Arc(100, 100, 500, 45, 60)
lines = a.segments()
print a
print "divided into {} segments".format(len(lines))
for l in lines:
    print l
