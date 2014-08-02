.PHONY: all install uninstall dist clean refresh

# Installation locations
PREFIX=/usr/local
MANDIR=${PREFIX}/man
BINDIR=${PREFIX}/bin

# Leave these as they are.
ALLSCRIPTS=dxf2nc dxf2pdf dxfgerber nc2pdf readdxf readnc
DISTFILES=Makefile README.txt

# Default target
all: ${ALLSCRIPTS}

dxf2nc: src/dxf2nc.py src/nctools/*.py
	cd src && ln dxf2nc.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >dxf2nc
	cat foo.zip >>dxf2nc
	rm -f foo.zip
	chmod a+x dxf2nc

dxf2pdf: src/dxf2pdf.py src/nctools/*.py
	cd src && ln dxf2pdf.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >dxf2pdf
	cat foo.zip >>dxf2pdf
	rm -f foo.zip
	chmod a+x dxf2pdf

dxfgerber: src/dxfgerber.py src/nctools/*.py
	cd src && ln dxfgerber.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >dxfgerber
	cat foo.zip >>dxfgerber
	rm -f foo.zip
	chmod a+x dxfgerber

nc2pdf: src/nc2pdf.py src/nctools/*.py
	cd src && ln nc2pdf.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >nc2pdf
	cat foo.zip >>nc2pdf
	rm -f foo.zip
	chmod a+x nc2pdf

readdxf: src/readdxf.py src/nctools/*.py
	cd src && ln readdxf.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >readdxf
	cat foo.zip >>readdxf
	rm -f foo.zip
	chmod a+x readdxf

readnc: src/readnc.py src/nctools/*.py
	cd src && ln readnc.py __main__.py && zip -q ../foo.zip __main__.py nctools/*.py
	rm -f src/__main__.py
	echo '#!/usr/bin/env python' >readnc
	cat foo.zip >>readnc
	rm -f foo.zip
	chmod a+x readnc

clean::
	rm -f dxf2nc dxf2pdf dxfgerber nc2pdf readdxf readnc foo.zip src/__main__.py

install: ${ALLSCRIPTS}
	install ${ALLSCRIPTS} ${BINDIR}

