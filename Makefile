.PHONY: all install uninstall dist clean refresh check setver

# Installation locations
PREFIX=/usr/local
MANDIR=${PREFIX}/man
BINDIR=${PREFIX}/bin

# Leave these as they are.
PYFILES!=find . -type f -name "*.py"
ALLSCRIPTS=dxf2nc dxf2pdf dxfgerber nc2pdf readdxf
DISTFILES=Makefile README.txt
VER=2.0.0-beta

# Default target
all: dxf2nc

# This actually builds all scripts.
dxf2nc: build.py src/*.py src/nctools/*.py
	python3 build.py

clean::
	rm -f dxf2nc dxf2pdf dxfgerber nc2pdf readdxf readnc foo.zip src/__main__.py
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

install: dxf2nc
	install ${ALLSCRIPTS} ${BINDIR}

check::
	pep8 ${PYFILES}

setver::
	sed -i '' -e "s/^__version__.*/__version__ = '${VER}'/" ${PYFILES}
