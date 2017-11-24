#!/bin/bash

echo "You should updated the following: CHANGES, pymodis/__init__.py"
echo "Could it \"procede\" (answer yes or no)?"
read procede

if [ $procede = "yes" ]; then

  pymodis_version=`python setup.py -V`
  curdir=`pwd`

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

  python setup.py sdist upload

fi

echo "Do you want create \"Debian\" packages (answer yes or no)?"
read Debian
if [ $Debian = "yes" ]; then

  su -c "dpkg-buildpackage -us -uc -d"

fi
