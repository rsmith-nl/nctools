.PHONY: all install dist clean backup deinstall check
.SUFFIXES: .py

BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'

help::
	@echo "You can use one of the following commands:"
	@echo "  install -- install the package system-wide"
	@echo "  deinstall -- remove the system-wide installation"
#beginskip
	@echo "  dist -- create a distribution file"
	@echo "  clean -- remove all generated files"
	@echo "  backup -- make a complete backup"
#endskip


install: ${ALL}
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
# Let Python do most of the install work.
	python setup.py install
# Lose the extension; this is UNIX. :-)
	mv $(BINDIR)/dxf2nc.py $(BINDIR)/dxf2nc
	mv $(BINDIR)/dxf2pdf.py $(BINDIR)/dxf2pdf
	mv $(BINDIR)/dxfgerber.py $(BINDIR)/dxfgerber
	mv $(BINDIR)/nc2pdf.py $(BINDIR)/nc2pdf
	mv $(BINDIR)/ncfmt.py $(BINDIR)/ncfmt
	mv $(BINDIR)/readdxf.py $(BINDIR)/readdxf
	rm -rf build

deinstall::
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to deinstall the program!"; \
		exit 1; \
	fi
	rm -f ${PYSITE}/nctools
	rm -f $(BINDIR)/dxf2nc* $(BINDIR)/dxf2pdf* $(BINDIR)/dxfgerber* \
	    $(BINDIR)/nc2pdf* $(BINDIR)/ncfmt* $(BINDIR)/readdxf*

#beginskip
dist: ${ALL}
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist --format=zip
	mv Makefile.org Makefile
	rm -f MANIFEST
	#cd dist ; sha256 nctools-* >../port/stltools/distinfo 
	#cd dist ; ls -l nctools-* | awk '{printf "SIZE (%s) = %d\n", $$9, $$5};' >>../port/stltools/distinfo 

clean::
	rm -rf dist build backup-*.tar.gz *.pyc MANIFEST
	#rm -f port/nctools/distinfo

backup::
	sh tools/genbackup

#endskip
