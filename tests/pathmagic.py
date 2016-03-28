# file: pathmagic.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-03-28 01:55:57 +0200
# Last modified: 2016-03-28 10:35:49 +0200

"""Path hack to make tests work."""

import os
import sys

bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
modpath = os.sep.join(bp + ['src'])
sys.path.insert(0, modpath)
