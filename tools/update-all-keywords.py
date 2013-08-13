#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
# $Revision$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to update-all-keywords.py. This work is 
# published from the Netherlands. 
# See http://creativecommons.org/publicdomain/zero/1.0/

"""Remove and check out all files under git's control that contain keywords in
the current working directory."""

from __future__ import print_function, division
import os
import mmap
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
    try:
        with open(os.devnull, 'w') as bb:
            subprocess.check_call(args, stdout=bb, stderr=bb)
    except subprocess.CalledProcessError:
        print("Required program '{}' not found! exiting.".format(args[0]))
        sys.exit(1)


def git_ls_files():
    """Find ordinary files that are controlled by git. 

    :returns: A list of files
    """
    args = ['git', 'ls-files']
    flist = subprocess.check_output(args).splitlines()
    return flist


def git_not_checkedin():
    """Find files that are modified but are not checked in.

    :returns: A list of modified files that are not checked in.
    """
    lns = subprocess.check_output(['git', 'status', '-s']).splitlines()
    lns = [l.split()[-1] for l in lns]
    return lns


def keywordfiles(fns):
    """Filter those files that have keywords in them

    :fns: A list of filenames
    :returns: A list for filenames for files that contain keywords.
    """
    # These lines are encoded otherwise they would be mangled if this file
    # is checked in!
    datekw = 'JERhdGU='.decode('base64')
    revkw = 'JFJldmlzaW9u'.decode('base64')
    rv = []
    for fn in fns:
        with open(fn, 'rb') as f:
            try:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                if mm.find(datekw) > -1 or mm.find(revkw) > -1:
                    rv.append(fn)
                mm.close()
            except ValueError:
                pass
    return rv


def main(args):
    """Main program.

    :args: command line arguments
    """
    # Check if git is available.
    checkfor(['git', '--version'])
    # Check if .git exists
    if not os.access('.git', os.F_OK):
        print('No .git directory found!')
        sys.exit(1)
    # Get all files that are controlled by git.
    files = git_ls_files()
    # Remove those that aren't checked in
    mod = git_not_checkedin()
    if mod:
        files = [f for f in files if not f in mod]
    if not files:
        print('{}: Only uncommitted changes, nothing to do.'.format(args[0]))
        sys.exit(0)
    files.sort()
    # Find files that have keywords in them
    kwfn = keywordfiles(files)
    if kwfn:
        print('{}: Updating all files.'.format(args[0]))
        for fn in kwfn:
            os.remove(fn)
        args = ['git', 'checkout', '-f'] + kwfn
        subprocess.call(args)
    else:
        print('{}: Nothing to update.'.format(args[0]))


if __name__ == '__main__':
    main(sys.argv)
