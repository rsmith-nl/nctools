#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to update-all-keywords.py. This work is 
# published from the Netherlands. 
# See http://creativecommons.org/publicdomain/zero/1.0/

"""Remove and check out all files that contain keywords."""

from __future__ import print_function, division
import os
import sys
import subprocess


def checkfor(args):
    """Make sure that a program necessary for using this script is
    available.

    Arguments:
    args -- string or list of strings of commands. A single string may
            not contain spaces.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('No spaces in single command allowed.')
        args = [args]
    #print('DEBUG: checking for', args[0])
    try:
        with open(os.devnull, 'w') as bb:
            subprocess.check_call(args, stdout=bb, stderr=bb)
    except subprocess.CalledProcessError:
        print("Required program '{}' not found! exiting.".format(args[0]))
        sys.exit(1)


def normalfiles(top='.', exlist=None):
    """Find ordinary files. Exclude files whose paths contain one of the
    parts of the exlist

    :top: Directory to start in
    :exlist: List of paths to skip
    :returns: @todo
    """
    if exlist == None:
        exlist = ['.git', '__pycache__']
    flist = []
    for root, _, files in os.walk(top):
        if all([not b in root for b in exlist]):
            flist += [os.path.join(root, f) for f in files]
    return flist


def gitmodified():
    """Find files that are modified by git.
    :returns: A list of modified files.
    """
    lns = subprocess.check_output(['git', 'status', '-s']).splitlines()
    lns = ['./' + l.split()[-1] for l in lns]
    return lns


def keywordfiles(fns):
    """Filter those files that have keywords in them

    :fns: A list of filenames
    :returns: A list for filenames for files that contain keywords.
    """
    datekw = 'JERhdGU='.decode('base64')
    revkw = 'JFJldmlzaW9u'.decode('base64')
    rv = []
    for fn in fns:
        with open(fn) as f:
            data = f.read()
        if datekw in data or revkw in data:
            rv.append(fn)
            #print('DEBUG: found keyword in', fn)
        #else:
            #print('DEBUG: no keyword in', fn)
    return rv


def main():
    """Main program.
    """
    checkfor(['git', '--version'])
    # Check if .git exists
    if not os.access('.git', os.F_OK):
        print('No .git directory found!')
        sys.exit(1)
    # Get all files
    files = normalfiles()
    # Remove those that aren't checked in
    mod = gitmodified()
    #print('DEBUG: modified files = ', mod)
    if mod:
        files = [f for f in files if not f in mod]
    files.sort()
    # Find files that have keywords in them
    kwfn = keywordfiles(files)
    for fn in kwfn:
        #print('DEBUG: removing', fn)
        os.remove(fn)
    #print('DEBUG: checking out files')
    args = ['git', 'checkout', '-f'] + kwfn
    subprocess.call(args)

if __name__ == '__main__':
    main()
