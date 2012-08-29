About pyModis
==============

How to install pyModis
-----------------------

It is possible to install ``pyModis`` in a very simple way. First you 
need to download ``pyModis`` source code from 
`github repository <https://github.com/lucadelu/pyModis>`_.

You can use `git <http://git-scm.com/>`_ to download the latest code 
(with the different stable version, the last and the older) ::

    git clone git://github.com/lucadelu/pyModis.github

or `download the latest stable version <https://github.com/lucadelu/pyModis/tags>`_ 
from the repository and decompress it

Now enter inside the ``pyModis`` folder and launch as administrator of 
your computer ::

    python setup.py install

If the installation doesn't return any errors you should be able to use
``pyModis`` library from a Python console. So launch a your favorite
Python console (I really suggest ``ipython``) and digit ::

    import pymodis

If the console doesn't return any error like this ::

    ImportError: No module named pymodis

the ``pyModis`` library is installed correctly and you can use it
or one of the tools distributed with ``pyModis`` 

How to report bug
------------------

If you find any problems in ``pyModis`` library you can report it using
the `issues tracker of github <https://github.com/lucadelu/pyModis/issues>`_.

How to compile documentation
-----------------------------

This documentation is make with `Sphinx <sphinx.pocoo.org>`_, so you
need to install it to compile the original files to obtain different
output formats.

Please enter inside ``docs`` folder of ``pymodis`` source and run ::

    make <target>
    
with one of the following target to obtain the desired output:

  - **html**: to make standalone HTML files
  - **dirhtml**: to make HTML files named index.html in directories
  - **singlehtml**: to make a single large HTML file
  - **pickle**: to make pickle files
  - **json**: to make JSON files
  - **htmlhelp**: to make HTML files and a HTML help project
  - **qthelp**: to make HTML files and a qthelp project
  - **devhelp**: to make HTML files and a Devhelp project
  - **epub**: to make an epub
  - **latex**: to make LaTeX files, you can set PAPER=a4 or PAPER=letter
  - **latexpdf**: to make LaTeX files and run them through pdflatex
  - **text**: to make text files
  - **man**: to make manual pages
  - **texinfo**: to make Texinfo files
  - **info**: to make Texinfo files and run them through makeinfo
  - **gettext**: to make PO message catalogs
  - **changes**: to make an overview of all changed/added/deprecated items
  - **linkcheck**: to check all external links for integrity
  - **doctest**: to run all doctests embedded in the documentation (if enabled)
