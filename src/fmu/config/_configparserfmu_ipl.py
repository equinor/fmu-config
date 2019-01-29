# -*- coding: utf-8 -*-
"""Addon to configparser.py. Focus on IPL handling"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from copy import deepcopy
from collections import OrderedDict

import os
import datetime

from fmu.config import etc

xfmu = etc.Interaction()
logger = xfmu.functionlogger(__name__)

# pylint: disable=protected-access
# pylint: disable=too-many-branches


class ConfigError(ValueError):
    """Exception used for config error, derived from ValueError"""
    pass


def to_ipl(self, rootname='global_variables', destination=None,
           template=None, tool='rms'):
    """Export the config as a global variables IPL and/or template
    form of the IPL.

    Args:
        rootname: Root file name without extension. An extension
            .ipl will be added for destination, and .ipl.tmpl
            for template output.
        destination (str): The output file destination (folder)
        template (str): The folder for the templated version of the
            IPL (for ERT).
        tool (str): Which section in the master to use (default is 'rms')
    """

    if not destination and not template:
        raise ConfigError('Both destination and template for IPL cannot '
                          'be None.')

    if destination and not os.path.isdir(destination):
        raise ConfigError('Given "destination" {} is not a directory'
                          .format(destination))
    if template and not os.path.isdir(template):
        raise ConfigError('Given "template" {} is not a directory'
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

    hdecl, hlist = _ipl_kwlists_format(self, tool=tool)
    if hdecl is not None:
        declarations.extend(hdecl)
        expressions_dest.extend(hlist)
        expressions_tmpl.extend(hlist)

    if destination:
        hdecl, hlist = _ipl_freeform_format(self)
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions_dest.extend(hlist)

        destfile = os.path.join(destination, rootname + '.ipl')
        with open(destfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_dest:
                stream.write(line)

    if template:
        hdecl, hlist = _ipl_freeform_format(self, template=True)
        if hdecl is not None:
            if not destination:
                declarations.extend(hdecl)

            expressions_tmpl.extend(hlist)

        tmplfile = os.path.join(template, rootname + '.ipl.tmpl')
        with open(tmplfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_tmpl:
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
        for inum, element in enumerate(array):
            mylist = '{}[{}] = "{}"\n'.format(variable, inum + 1, element)
            expr.append(mylist)

    expr.append('\n')

    return decl, expr


def _ipl_kwlists_format(self, tool='rms'):
    """Process the rms 'kwlists', and return declarations and values.

    This format is on the form::

      rms:
        kwlists:

          FACIESNAMES:
            OFFSHORE_VI_C: [1, "Offshore mudstones, Viking Gp."]
            MUDDY_SPIC_C: [2, "Muddy spiculites"]
            BIOSTROME_REEF_C: [3, "Biostrome reef"]
            SANDY_SPIC_C: [4, "Sandy spiculites"]
            TSS_Z1_C: [5, "Transgressive sands, Draupne Fm 2"]

    It should then give::

       Int OFFSHORE_VI_C = 1
       Int MUDDY_SPIC_C = 2
       etc...

       String FACIESNAMES[]

       FACIESNAMES[OFFSHORE_VI_C] = "Offshore mudstones, Viking Gp."
       etc
    """

    cfg = self.config[tool].get('kwlists')
    if cfg is None:
        return None, None

    decl = []
    expr = []
    for key, var in cfg.items():
        mydecl = 'String {}[]\n'.format(key)
        decl.append(mydecl)

        for subkey, (code, fullname) in var.items():
            logger.info(subkey, code, fullname)
            mydecl = 'Int {} = {}\n'.format(subkey, code)
            decl.append(mydecl)

            mylist = '{}[{}] = "{}"\n'.format(key, subkey, fullname)
            expr.append(mylist)

        expr.append('\n')

    return decl, expr


def _cast_value(value):
    """Convert data type when a number is represented as a string,
    e.g. '1' or '34.33'
    """

    logger.info('Value is of type %s', type(value))
    result = value
    if isinstance(value, str):
        if '.' in value:
            try:
                result = float(value)
            except ValueError:
                result = value
        elif value.lower() in ('yes', 'true'):
            result = True
        elif value.lower() in ('no', 'false'):
            result = False
        else:
            try:
                result = int(value)
            except ValueError:
                result = value
    else:
        result = value

    return result


def _guess_dtype(var, entry):
    """Guess the IPL dtype from value or values if dtype is missing.

    The entry itself will then be a scalar or a list, which need to be
    analysed. If a list, only the first value is analysed for data
    type.

    Returns a dict (OrderedDict) as usekey[keyword]['dtype'] and
    usekey[keyword]['value'] or usekey[keyword]['values']
    """
    values = entry[var]
    keyword = var
    logger.info('Guess dtype and value(s) for %s %s', var, values)

    usekey = OrderedDict()
    usekey[keyword] = OrderedDict()
    usekey[keyword]['dtype'] = None
    usekey[keyword]['value'] = None   # Keep "value" if singel entry
    usekey[keyword]['values'] = None  # Keep "values", if list

    if isinstance(values, list):
        checkval = values[0]
        scheckval = str(checkval)
        if '~' in scheckval:
            val, _xtmp = scheckval.split('~')
            checkval = val.strip()
            checkval = _cast_value(checkval)

        usekey[keyword]['values'] = values
        del usekey[keyword]['value']
    else:
        checkval = values
        scheckval = str(checkval)
        if '~' in scheckval:
            val, _xtmp = scheckval.split('~')
            checkval = val.strip()
            checkval = _cast_value(checkval)
        usekey[keyword]['value'] = values
        del usekey[keyword]['values']

    for alt in ('int', 'str', 'float', 'bool'):
        if alt in str(type(checkval)):
            usekey[keyword]['dtype'] = alt

            break

    if not usekey[keyword]['dtype']:
        # dtype is still None; evaluate for date or datepair:
        if isinstance(checkval, list):
            checkval = checkval[0]
            if isinstance(checkval, datetime.date):
                usekey[keyword]['dtype'] = 'datepair'
        else:
            if isinstance(checkval, datetime.date):
                usekey[keyword]['dtype'] = 'date'

    # final check
    if not usekey[keyword]['dtype']:
        raise RuntimeError('Cannot find dtype')

    logger.info('Updated key dtype is %s', usekey[keyword]['dtype'])
    logger.info('Updated key is %s', usekey)
    return usekey


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
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    decl = ['\n// Declare free form:\n']
    expr = ['\n// Free form expressions:\n']

    cfg = self.config['rms']

    # collect uppercase keys in 'rms'
    freeform_keys = []
    for key in cfg:
        if all(word[0].isupper() for word in key if word.isalpha()):
            freeform_keys.append(key)

    if not freeform_keys:
        return None, None

    for variable in freeform_keys:
        logger.info('Variable to process is %s', variable)
        expr.append('\n')

        if variable.startswith('_IPL_CODE'):
            logger.info('IPL code stub: %s \n%s', variable, cfg[variable])
            expr.append(cfg[variable])
            continue

        if variable.startswith('_IPL_DECLARE'):
            logger.info('IPL declare only: %s \n%s', variable, cfg[variable])
            decl.append(cfg[variable])
            continue

        if not isinstance(cfg[variable], dict):
            guesscfg = _guess_dtype(variable, cfg)

            usecfg = guesscfg[variable]
        else:
            usecfg = deepcopy(cfg[variable])

        mydtype = usecfg['dtype']
        if mydtype is not None:
            subtype = mydtype.capitalize()
        if 'Str' in subtype:
            subtype = 'String'
        elif 'Date' in subtype:
            subtype = 'String'

        logger.info('SUBTYPE: %s %s', variable, subtype)

        myvalue = usecfg.get('value')
        myvalues = usecfg.get('values')

        logger.info('For %s value: %s and values: %s, subtype %s',
                    variable, myvalue, myvalues, subtype)

        if subtype == 'Bool':
            tmpvalue = str(myvalue)
            try:
                val, var = tmpvalue.split('~')
                val = val.strip()
                var = var.strip()
            except ValueError:
                val = tmpvalue.strip()
                var = None

            for somebool in ('True', 'yes', 'YES', 'Yes', 'true', 'TRUE'):
                val = val.replace(somebool, 'TRUE')
            for somebool in ('False', 'no', 'NO', 'No', 'false', 'FALSE'):
                val = val.replace(somebool, 'FALSE')

            myvalue = val
            if var:
                myvalue = myvalue + ' ~ ' + var

        if myvalue is None and myvalues is None:
            raise ConfigError('"value" or "values" is missing for RMS '
                              'variable {}'.format(variable))

        logger.info('myvalue is %s for %s', myvalue, variable)

        if myvalue is not None:
            logger.info('Check %s with value: %s of type %s',
                        variable, myvalue, type(myvalue))
            if not isinstance(myvalue, (int, float, str, bool, datetime.date,
                                        list)):
                raise ConfigError('"value" is of wrong type for '
                                  'variable {}: {} ({})'
                                  .format(variable, myvalue, type(myvalue)))
        if myvalues is not None:
            if not isinstance(myvalues, (list)):
                raise ConfigError('"values" is of wrong type for '
                                  'variable {}: {} ({})'
                                  .format(variable, myvalues, type(myvalues)))

        myvalue = _fix_date_format(variable, mydtype, myvalue, aslist=False)
        myvalues = _fix_date_format(variable, mydtype, myvalues, aslist=True)

        logger.info('Check again %s with value: %s and dtype %s',
                    variable, myvalue, mydtype)
        logger.info('Check again %s with values: %s and dtype %s',
                    variable, myvalues, mydtype)

        listtype = ''
        if myvalue is not None:

            logger.info('Working with %s', variable)
            isstring = False
            if subtype == 'String':
                isstring = True
            logger.info('Process value: %s', myvalue)

            myvalue = _get_required_iplform(str(myvalue), template=template,
                                            string=isstring)

            logger.info('Returns value: %s', myvalue)
            myexpr = '{} = {}'.format(variable, myvalue)

            expr.append(myexpr)

        # list of values:
        elif myvalues is not None:
            listtype = '[]'
            for inum, val in enumerate(myvalues):
                fnutt = ''
                if subtype == 'String':
                    fnutt = '"'
                myexpr = '{}[{}] = {}{}{}\n'.format(variable, inum + 1,
                                                    fnutt, val, fnutt)
                logger.info('Stream for list %s', myexpr)
                pre, post = myexpr.split('=')
                pre = pre.strip()
                post = post.strip()
                myexpr = (pre + ' = ' +
                          _get_required_iplform(str(post), template=template))
                expr.append(myexpr)

        mydecl = '{} {}{}\n'.format(subtype, variable, listtype)
        decl.append(mydecl)

    decl.append('//{} {}\n\n'.format('-*- END IPL DECLARATIONS -*-', '-' * 48))
    return decl, expr


def _fix_date_format(var, dtype, value, aslist=False):
    """Make dateformat to acceptable RMS IPL format."""

    logger.info('Fix dates...')
    if value is None:
        return None

    logger.info('Fix dates...2 dtype is %s', dtype)
    if dtype not in ('date', 'datepair'):
        logger.info('Fix dates...2 dtype is %s RETURN', dtype)
        return value

    values = None
    if aslist:
        logger.debug('Dates is a list')
        values = value
        value = None

    result = None
    if dtype == 'date':
        logger.info('Process date ...')
        if value:
            raise RuntimeError('<{}>: Treating <date> as "value" is not '
                               'possible, rather make into list "values" '
                               'with one entry instead!'.format(var))
            # logger.info('Process date as ONE value for %s', var)
            # if isinstance(value, (datetime.datetime, datetime.date)):
            #     value = str(value)
            #     value = value.replace('-', '')
            # result = value
        if values:
            mynewvalues = []
            logger.info('Process date as values')
            for val in values:
                if isinstance(val, (datetime.datetime, datetime.date)):
                    val = str(val)
                    val = val.replace('-', '')
                    mynewvalues.append(val)
            result = mynewvalues

    if dtype == 'datepair':
        if value:
            raise RuntimeError('<{}> Treating <datepair> as "value" is not '
                               'possible, rather make into list "values" '
                               'with one entry instead!'.format(var))
            # date1, date2 = value
            # if isinstance(date1, (datetime.datetime, datetime.date)):
            #     date1 = str(date1)
            #     date1 = date1.replace('-', '')

            # if isinstance(date2, (datetime.datetime, datetime.date)):
            #     date2 = str(date2)
            #     date2 = date1.replace('-', '')
            # result = date1 + '_' + date2

        if values:
            mynewvalues = []
            for val in values:
                date1, date2 = val
                if isinstance(date1, (datetime.datetime, datetime.date)):
                    date1 = str(date1)
                    date1 = date1.replace('-', '')
                if isinstance(date2, (datetime.datetime, datetime.date)):
                    date2 = str(date2)
                    date2 = date2.replace('-', '')
                mynewvalues.append(date1 + '_' + date2)

            result = mynewvalues

    return result


def _get_required_iplform(stream, template=False, string=False):
    """Strip a string for IPL output.

    If template is True, keep the value if no ~ is present,
    otherwise return the <...> string and the value as a comment.

    If template is False, return the value with <...> as comment
    if present.

    If string is True, secure correct handling of '"' around values
    """

    if isinstance(stream, str):
        logger.info('STREAM is a str object: %s', stream)
    else:
        raise NotImplementedError('Wait')

    if '~' in stream:
        val, var = stream.split('~')
        val = val.strip()
        var = var.strip()
        if string:
            val = '"' + val + '"'
            var = '"' + var + '"'
        if template:
            result = var + '  // ' + val
        else:
            result = val + '  // ' + var
    else:
        result = stream.strip()
        if string:
            result = '"' + result + '"'

    if '\n' not in result:
        result = result + '\n'

    return result
