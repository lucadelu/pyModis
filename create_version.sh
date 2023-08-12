#!/bin/bash

t=`which twine`

if [ $? -ne 0 ]; then
  echo "twine is required, please install it"
  exit 1
fi

echo "STEP to be done before:
* update CHANGES and pymodis/__init__.py files
* add new tag
* run this script
";
echo "Could it \"procede\" (answer yes or no)?"
read procede

if [ $procede = "yes" ]; then

  pymodis_version=`python setup.py -V`
  curdir=`pwd`

  rm -rf build/*
  python setup.py build

  rm -rf dist/*
  python setup.py bdist

  cd docs/

  make latexpdf
  make html

  cd build/html/

  find . -type f -name "*~" -exec rm -f {} \;

  cp ../latex/pyModis.pdf .

  zip -r -9 $curdir/pymodis_${pymodis_version}_html.zip *

  cd $curdir

  rm -rf docs/build/

  find . -type f -name "*~" -exec rm -f {} \;

  twine check dist/*

  echo "Is twine \"check\" ok? (answer yes or no)"
  read check

  if [ $check = "yes" ]; then
    twine upload dist/*
  fi

  echo "Do you want create \"Debian\" packages (answer yes or no)?"
  read Debian

  if [ $Debian = "yes" ]; then
    su -c "dpkg-buildpackage -us -uc -d"
  fi

fi
