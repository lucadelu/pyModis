#!/usr/bin/env python
#  class to parse modis data
#
#  (c) Copyright Luca Delucchi 2013
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at iasma dot it
#
##################################################################
#
#  This MODIS Python class is licensed under the terms of GNU GPL 2.
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
##################################################################
"""Module to extend optparse, it add required options and new types to use
into gui module.

Classes:

* :class:`OptionWithDefault`
* :class:`OptionParser`

"""

import optparse

# classes for required options
STREQUIRED = 'required'


class OptionWithDefault(optparse.Option):
    """Extend optparse.Option add required to the attributes and some new
       types for the GUI
    """
    ATTRS = optparse.Option.ATTRS + [STREQUIRED]
    TYPES = optparse.Option.TYPES + ('file', 'output', 'directory')

    def __init__(self, *opts, **attrs):
        """Function to initialize the object"""
        if attrs.get(STREQUIRED, False):
            attrs['help'] = '(Required) ' + attrs.get('help', "")
        optparse.Option.__init__(self, *opts, **attrs)


class OptionParser(optparse.OptionParser):
    """Extend optparse.OptionParser"""
    def __init__(self, **kwargs):
        """Function to initialize the object"""
        kwargs['option_class'] = OptionWithDefault
        optparse.OptionParser.__init__(self, **kwargs)

    def check_values(self, values, args):
        """Check if value is required for an option"""
        for option in self.option_list:
            if hasattr(option, STREQUIRED) and option.required:
                if not getattr(values, option.dest):
                    self.error("option {opt} is required".format(opt=str(option)))
        return optparse.OptionParser.check_values(self, values, args)
