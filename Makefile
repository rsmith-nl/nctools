.PHONY: all install dist clean backup check
.SUFFIXES: .ps .pdf .py

#beginskip
PROG = dxfgerber
PROG2 = dxf2nc
ALL = ${PROG}.1.pdf 
all: ${ALL} .git/hooks/post-commit
#endskip
BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'

install: ${PROG}.1 setup.py ${PROG}.py
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
# Let Python do most of the install work.
	python setup.py install
# Lose the extension; this is UNIX. :-)
	mv $(BINDIR)/${PROG}.py $(BINDIR)/${PROG}
	rm -rf build
#Install the manual page.
	gzip -c ${PROG}.1 >${PROG}.1.gz
	install -m 644 ${PROG}.1.gz $(MANDIR)/man1
	rm -f ${PROG}.1.gz

deinstall::
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to deinstall the program!"; \
		exit 1; \
	fi
	rm -f ${PYSITE}/module.py
	rm -f $(BINDIR)/${PROG}
	rm -f $(MANDIR)/man1/${PROG}.1.gz

#beginskip
dist: ${ALL}
# Make simplified makefile.
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
# Create distribution file. Use zip format to make deployment easier on windoze.
	python setup.py sdist --format=zip
	mv Makefile.org Makefile
	rm -f MANIFEST

clean::
	rm -rf dist build backup-*.tar.gz *.pyc ${ALL} MANIFEST

backup: ${ALL}
# Generate a full backup.
	sh tools/genbackup

check: .IGNORE
	pylint --rcfile=tools/pylintrc ${SRCS}

.git/hooks/post-commit: tools/post-commit
	install -m 755 $> $@

${PROG}.1.pdf: ${PROG}.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps
#endskip
