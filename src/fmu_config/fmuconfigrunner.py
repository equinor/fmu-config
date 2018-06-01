# -*- coding: utf-8 -*-
"""Script for converting the global config to various flavours of suiteble
flavours"""

from __future__ import division, print_function, absolute_import

import argparse
import sys
import os.path

import fmu_config
from xtgeo.common import XTGeoDialog

from fmu_config import _version as vv

appname = 'fmuconfigrunner'

__version__ = vv.get_versions()['version']

xtg = XTGeoDialog()

logger = xtg.functionlogger(__name__)


def _do_parse_args(args):

    if args is None:
        args = sys.argv[1:]
    else:
        args = args

    usetxt = 'fmuconfig ... '

    parser = argparse.ArgumentParser(
        description='Configure from FMU global master',
        usage=usetxt
    )

    parser.add_argument('--input',
                        dest='infile',
                        type=str,
                        help='Input file name')

    parser.add_argument('--output',
                        dest='outfile',
                        type=str,
                        help='Output file name')

    parser.add_argument('--mode',
                        dest='mode',
                        default='ipl',
                        type=str,
                        help='Mode for conversion: "ipl" etc...')

    parser.add_argument('--rootname',
                        dest='rootname',
                        default='global_variables',
                        type=str,
                        help='Root of file name')

    parser.add_argument('--destination',
                        dest='destination',
                        type=str,
                        help='Destination folder (for actual values)')

    parser.add_argument('--template',
                        dest='template',
                        type=str,
                        help='Template folder (for files with <xxxx> values)')

    parser.add_argument('--tool',
                        dest='tool',
                        default='rms',
                        type=str,
                        help='Tool section to apply, e.g. rms or eclipse')

    if len(args) < 2:
        parser.print_help()
        print('QUIT')
        sys.exit(0)

    args = parser.parse_args(args)
    return args


def main(args=None):

    args = _do_parse_args(args)

    cfg = fmu_config.ConfigParserFMU()

    xtg.say('OK {}'.format(cfg))

    if isinstance(args.infile, str):
        if not os.path.isfile(args.infile):
            raise IOError('Input file does not exist')
        cfg.parse(args.infile)

    if args.mode == 'ipl':
        print('Mode is IPL')
        cfg.to_ipl(rootname=args.rootname, destination=args.destination,
                   template=args.template, tool=args.tool)

    if args.mode == 'yaml':
        print('Mode is YAML')
        cfg.to_yaml(rootname=args.rootname, destination=args.destination,
                    template=args.template, tool=args.tool)


if __name__ == '__main__':
    main()
