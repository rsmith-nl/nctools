Installation instructions for NCtools
#####################################

Installation on Windows
=======================

- First install the Python interpreter, e.g. version 3.4.x and make sure that
  it works.
- Make sure that the Python directory and the scripts directory in is the
  path; Under XP, go to My Computer, right-click and select Properties. In the
  dialog box select the Avanced tab and click on the Environment Variables
  button. In the system variable Path, you should see two paths, for the
  Python interpreter and for installed scripts. It should look like this:
  ";C:\Python34;C:\Python34\Scripts" (for Python version 3.4.x). If you don't
  see them, add them. Note: for distributions such as anaconda, it will be
  different.
- Run ``python build.py`` to build the compressed scripts.
- Copy the files dxf2nc, dxf2pdf, dxfgerber, nc2pdf, readdxf and readnc to the
  “Scripts” directory of your Python. Give them the extension ``.pyz``.
  Copy the file dumpgerber.py to the same directory.
- Install the ``pycairo`` library that are necessary for ``dxf2pdf and
  nc2pdf``. You can find pre-built binaries e.g. at
  http://www.lfd.uci.edu/~gohlke/pythonlibs/


Installation on UNIX/Linux
==========================

- Install Python 3.
- Install Cairo and the Python bindings.
- Run ``make`` to build the compressed scripts.
- Run ``make install``.
