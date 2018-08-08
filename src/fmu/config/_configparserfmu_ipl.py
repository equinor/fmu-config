# -*- coding: utf-8 -*-
"""Addon to configparser.py. Focus on IPL handling"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import datetime

from fmu.config import etc

xfmu = etc.Interaction()
logger = xfmu.functionlogger(__name__)


def to_ipl(self, rootname='global_variables', destination=None,
           template=None, tool='rms'):
    """Export the config as a global variables IPL and/or template
    form of the IPL.

    Args:
        rootname: Root file name without extension. An extension
            .ipl will be added for destination, and .tmpl
            for template output.
        destination (str): The output file destination (folder)
        template (str): The folder for the templated version of the
            IPL (for ERT).
        tool (str): Which section in the master to use (default is 'rms')
    """

    if not destination and not template:
        raise ValueError('Both destination and template for IPL cannot '
                         'be None.')

    if destination and not os.path.isdir(destination):
        raise ValueError('Given "destination" {} is not a directory'
                         .format(destination))
    if template and not os.path.isdir(template):
        raise ValueError('Given "template" {} is not a directory'
                         .format(template))

    declarations = []
    expressions_dest = []
    expressions_tmpl = []

    metadata = self._get_sysinfo(commentmarker='//')
    declarations.extend(metadata)

    hdecl, hlist = _ipl_stringlist_format(self, 'horizons', tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    hdecl, hlist = _ipl_stringlist_format(self, 'zones', tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    if destination:
        hdecl, hlist = _ipl_freeform_format(self)
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions_dest.extend(hlist)

    if template:
        hdecl, hlist = _ipl_freeform_format(self, template=True)
        if hdecl is not None:
            if not destination:
                declarations.extend(hdecl)

            expressions_tmpl.extend(hlist)

    if template:
        tmplfile = os.path.join(template, rootname + '.tmpl')
        with open(tmplfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_tmpl:
                stream.write(line)

    if destination:
        destfile = os.path.join(destination, rootname + '.ipl')
        with open(destfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_dest:
                stream.write(line)


def _ipl_stringlist_format(self, subtype, tool='rms'):
    """Process the rms horizons etc, and return declarations and values."""

    cfg = self.config[tool].get(subtype)
    if cfg is None:
        return None, None

    decl = []
    expr = []
    for variable in cfg:
        mydecl = 'String {}[]\n'.format(variable)
        decl.append(mydecl)

        array = cfg[variable]
        for i, element in enumerate(array):
            mylist = '{}[{}] = "{}"\n'.format(variable, i + 1, element)
            expr.append(mylist)

    expr.append('\n')

    return decl, expr


# this function is too long...
def _ipl_freeform_format(self, template=False):
    """Process the RMS IPL YAML config freeform types.

    The freeform types are e.g. like this::

        rms:
          KH_MULT_MTR:
            dtype: float
            value: 1.0 ~ <KH_MULT_MTR>  # <..> be used in ERT template

          GOC:
            dtype: float
            values:
              - 2010.0
              - 2016.0

    I.e. they are defined as *UPPERCASE_LETTER* keys within
    the RMS section, in contrast to 'horizons' and 'zones'

    Args:
        template (bool): If True, then the tvalue* are returned, if present

    """

    decl = ['// Declare free form:\n']
    expr = ['// Free form expressions:\n']

    cfg = self.config['rms']

    # collect uppercase keys in 'rms'
    freeform_keys = []
    for key in cfg:
        if all(word[0].isupper() for word in key if word.isalpha()):
            freeform_keys.append(key)

    if len(freeform_keys) == 0:
        return None, None

    for variable in freeform_keys:
        logger.info('Variable to process is %s', variable)
        expr.append('\n')
        mydtype = cfg[variable]['dtype']
        subtype = mydtype.capitalize()
        if 'Str' in subtype:
            subtype = 'String'
        elif 'Date' in subtype:
            subtype = 'String'

        myvalue = cfg[variable].get('value')
        myvalues = cfg[variable].get('values')
        logger.info('myvalue %s', myvalue)

        myvalue = _fix_date_format(mydtype, myvalue, aslist=False)
        myvalues = _fix_date_format(mydtype, myvalues, aslist=True)

        listtype = ''
        if myvalue:
            fnutt = ''
            if subtype == 'String':
                fnutt = '"'
            myvalue = '{}{}{}'.format(fnutt, myvalue, fnutt)
            print('XXX', myvalue)

            myvalue = self._get_required_form(myvalue, template=template,
                                              ipl=True)

            myexpr = '{} = {}\n'.format(variable, myvalue)

            expr.append(myexpr)

        # list of values:
        elif myvalues:
            listtype = '[]'
            for i, val in enumerate(myvalues):
                fnutt = ''
                if subtype == 'String':
                    fnutt = '"'
                myexpr = '{}[{}] = {}{}{}\n'.format(variable, i + 1,
                                                    fnutt, val, fnutt)
                expr.append(myexpr)

        mydecl = '{} {}{}\n'.format(subtype, variable, listtype)
        decl.append(mydecl)

    decl.append('{}\n'.format('/' * 79))
    return decl, expr


def _fix_date_format(dtype, value, aslist=False):
    """Make dateformat to acceptable RMS IPL format."""

    if not value:
        return None

    if dtype not in ('date', 'datepair'):
        return value

    values = None
    if aslist:
        values = value
        value = None

    if dtype == 'date':
        if value:
            if type(value) in (datetime.datetime, datetime.date):
                value = str(value)
                value = value.replace('-', '')

        if values:
            mynewvalues = []
            for val in values:
                if type(val) in (datetime.datetime, datetime.date):
                    val = str(val)
                    val = val.replace('-', '')
                    mynewvalues.append(val)
            values = mynewvalues

    if dtype == 'datepair':
        if value:
            date1, date2 = value
            if type(date1) in (datetime.datetime, datetime.date):
                date1 = str(date1)
                date1 = date1.replace('-', '')

            if type(date2) in (datetime.datetime, datetime.date):
                date2 = str(date2)
                date2 = date1.replace('-', '')
            value = date1 + '_' + date2

        if values:
            mynewvalues = []
            for val in values:
                date1, date2 = val
                if type(date1) in (datetime.datetime, datetime.date):
                    date1 = str(date1)
                    date1 = date1.replace('-', '')
                if type(date2) in (datetime.datetime, datetime.date):
                    date2 = str(date2)
                    date2 = date2.replace('-', '')
                mynewvalues.append(date1 + '_' + date2)

            values = mynewvalues

    return values
