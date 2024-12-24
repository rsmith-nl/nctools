# file: Makefile
# vim:fileencoding=utf-8:ft=make
#
# NOTE: This Makefile is mainly intended for developers.
#       It is only meant for UNIX-like operating systems.
#       Most of the commands require extra software.
#       Building the documentation requires a working LaTeX/docutils installation.
.POSIX:
.SUFFIXES:
.PHONY: clean check tags format test wheel zip working-tree-clean

PROJECT:=nctools

# For a Python program, help is the default target.
help::
	@echo "Command  Meaning"
	@echo "-------  -------"
	@sed -n -e '/##/s/:.*\#\#/\t/p' -e '/@sed/d' Makefile

clean:: ## remove all generated files.
	rm -rf dist/
	rm -f backup-*.tar* ${PROJECT}-*.zip
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

.ifmake check || format
FILES!=find . -type f -name '*.py*'
.endif
check:: .IGNORE ## check all python files. (requires pylama)
	pylama ${FILES}

tags:: ## regenerate tags file. (requires uctags)
	uctags -R --languages=Python

format:: ## format the source. (requires black)
	black ${FILES}

test:: ## run the built-in tests. (requires py.test)
	py.test -v

wheel:: ## build a wheel file. (requires build and flit_core)
	python -m build -n -w

.ifmake zip
TAGCOMMIT!=git rev-list --tags --max-count=1
TAG!=git describe --tags ${TAGCOMMIT}
.endif
zip:: clean working-tree-clean ## create a zip-file from the most recent tagged state of the repository.
	cd doc && make clean
	git checkout ${TAG}
	cd .. && zip -r ${PROJECT}-${TAG}.zip ${PROJECT} \
		-x '*/.git/*' '*/.pytest_cache/*' '*/__pycache__/*' '*/.cache/*'
	git checkout main
	mv ../${PROJECT}-${TAG}.zip .

working-tree-clean:: ## check if the working tree is clean. (requires git)
	git status | grep -q 'working tree clean'
