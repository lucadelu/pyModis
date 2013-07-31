About pyModis
==============

Requirements
-------------

Some Python library are used from some modules, the required are: GDAL, numpy, wxPython.
The libraries will be checked and if they are absent on your computer they will be
downloaded during the installation.

The `MODIS Reprojection Tool <https://lpdaac.usgs.gov/tools/modis_reprojection_tool>`_
software is used to convert or mosaic MODIS HDF files.

For *download* or *parse* HDF files only standard Python modules are used 
by ``pyModis`` library and tools.

How to install pyModis
-----------------------

Using pip
^^^^^^^^^^^^^^

From version 0.6.3 it is possible to install ``pyModis`` using
`pip <https://pypi.python.org/pypi/pip>`_. You have to run the following
command as administrator

::

  pip install pyModis

If you need to update your ``pyModis`` version you have to run

::

  pip install --upgrade pyModis

With ``pip`` it is also really simple to remove the library

::

  pip uninstall pyModis

Compile from source
^^^^^^^^^^^^^^^^^^^^^^

Compile ``pyModis`` is very simple. First you need to download ``pyModis``
source code from `github repository <https://github.com/lucadelu/pyModis>`_.

You can use `git <http://git-scm.com/>`_ to download the latest code 
(with the whole history and so it contain all the different stable versions, 
from the last to the first) ::

    git clone https://github.com/lucadelu/pyModis.git

or `download the latest stable version <https://github.com/lucadelu/pyModis/tags>`_ 
from the repository and decompress it.

Now enter the ``pyModis`` folder and launch as administrator of 
your computer ::

    python setup.py install

If the installation doesn't return any errors you should be able to use
``pyModis`` library from a Python console. Then, launch a your favorite
Python console (I really suggest ``ipython``) and digit ::

    import pymodis

If the console doesn't return any error like this ::

    ImportError: No module named pymodis

the ``pyModis`` library has been installed properly and you can use it
or one of the tools distributed with ``pyModis``.

Install on Windows
^^^^^^^^^^^^^^^^^^^^^

The simple way to install ``pyModis`` on Windows is to install latest Python 2.7
from http://python.org/download/

Now you have to modify the "Path" environment variable using *powershell* running ::

    [Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Python27\;C:\Python27\Scripts\", "User")

Download and install the last version of Distribute for Windows from
http://python-distribute.org/distribute_setup.py

At this point you have to move to standard command line (*cmd*) and install *pip*
using *easy_install* ::

    easy_install pip

Now install `numpy <http://www.numpy.org>`_ library using *easy_install* because
installation from pip is broken (this is required only for version >= 0.7.1) ::

    easy_install numpy

Finally install ``pyModis`` using *pip* ::

    pip install pyModis


How to report a bug or enhancement
------------------------------------

If you find any problems in ``pyModis`` library or you **want suggest enhancements**
you can report them using the `issues tracker of GitHub <https://github.com/lucadelu/pyModis/issues>`_.

How to compile documentation
------------------------------

This documentation has been made with `Sphinx <http://sphinx.pocoo.org>`_, so you
need to install it to compile the original files to obtain different
output formats.

Please enter the ``docs`` folder of ``pyModis`` source and run ::

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

PDF link in HTML
^^^^^^^^^^^^^^^^^^
To insert a link to PDF file of pyModis documentation into HTML documentation
(the link will be added on the sidebar) you have to compile first the PDF and
after the HTML, so you need to launch::

  make latexpdf
  make html

If PDF file is missing no link will be added

Ohloh statistics
-----------------

.. only:: html 

  .. raw:: html

      <table align="center">
	<tr>
	  <td align="center">
	    <script type="text/javascript" src="http://www.ohloh.net/p/486825/widgets/project_basic_stats.js"></script>
	  </td>
	  <td align="center">
	    <script type="text/javascript" src="http://www.ohloh.net/p/486825/widgets/project_factoids.js"></script>
	  </td>
	</tr>
	<tr>
	  <td align="center">
	    <script type="text/javascript" src="http://www.ohloh.net/p/486825/widgets/project_languages.js"></script>
	  </td>	
	  <td align="center">
	    <script type="text/javascript" src="http://www.ohloh.net/p/486825/widgets/project_cocomo.js"></script>
	  </td>
	</tr>
      </table>

.. only:: latex

  For more information about ``pyModis`` please visit the 
  `pyModis Ohloh page <http://www.ohloh.net/p/pyModis>`_