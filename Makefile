.PHONY: all install dist clean backup
.SUFFIXES: .ps .pdf .py

#beginskip
PROG = dxf4gerber
ALL = ${PROG}.1 ${PROG}.1.pdf setup.py ${PROG} tools/replace.sed .git/hooks/post-commit
all: ${ALL}
#endskip

install: ${PROG}.1 setup.py ${PROG}
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
	python setup.py install
	rm -rf build

#beginskip
dist: ${ALL} ${PROG}.1 ${PROG}.1.pdf
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist
	mv Makefile.org Makefile
	rm -f MANIFEST

clean::
	rm -rf dist build dxftools-*.tar.gz *.pyc MANIFEST ${PROG}.1 ${PROG}.1.pdf setup.py ${PROG}

backup::
	sh tools/genbackup

.git/hooks/post-commit: tools/post-commit
	install -m 755 $> $@

tools/replace.sed: .git/index
	tools/post-commit

setup.py: setup.in.py tools/replace.sed
	sed -f tools/replace.sed setup.in.py >$@

${PROG}: ${PROG}.in.py tools/replace.sed
	sed -f tools/replace.sed ${PROG}.in.py >$@
	chmod 755 ${PROG}

${PROG}.1: ${PROG}.1.in tools/replace.sed
	sed -f tools/replace.sed ${PROG}.1.in >$@

${PROG}.1.pdf: ${PROG}.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps
#endskip
