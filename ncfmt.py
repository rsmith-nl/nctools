#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Formats G-codes for the Gerber cutter for human readability.
#
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import sys
import os


__proginfo__ = ('ncfmt [ver. ' + '$Revision$'[11:-2] + 
                '] ('+'$Date$'[7:-2]+')')


def main(argv):
    """Main program for the ncformat utility.
    
    :argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print __proginfo__
        print "Usage: {} [file ...]".format(binary)
        sys.exit(0)
    del argv[0]
    for fn in argv:
        try:
            with open(fn, 'r') as inf:
                rd = inf.read()
        except IOError as e:
            print "Cannot read file: {}".format(e)
            print "Skipping file '{}'".format(fn)
            continue
        rd = rd.split('*')
        if len(rd) == 1 or rd[0] != 'H1':
            print "'{}' is not a valid NC code file. Skipping it".format(fn)
            continue
        if len(rd[-1]) == 0:
            del rd[-1]
        print 'file:', fn
        for e in rd:
            print e + '*'

if __name__ == '__main__':
    main(sys.argv)
