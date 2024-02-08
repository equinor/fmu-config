"""Script for converting the global config to various flavours of suiteble
flavours."""

import argparse
import os.path
import sys

import fmu.config as fmu_config
from fmu.config import etc

xfmu = etc.Interaction()
logger = xfmu.basiclogger(__name__)


def _do_parse_args(args):
    if args is None:
        args = sys.argv[1:]

    usetxt = "fmuconfig ... "

    parser = argparse.ArgumentParser(
        description="Configure from FMU global master", usage=usetxt
    )

    # positional:
    parser.add_argument(
        "config",
        type=str,
        help=("Input global config master file name on YAML format"),
    )

    parser.add_argument(
        "--mode",
        dest="mode",
        default="ipl",
        type=str,
        help="Mode for conversion: ipl/yaml/json/table etc...",
    )

    parser.add_argument(
        "--rootname",
        dest="rootname",
        default="global_variables",
        type=str,
        help="Root of file name",
    )

    parser.add_argument(
        "--destination",
        dest="destination",
        type=str,
        help="Destination folder (for actual values)",
    )

    parser.add_argument(
        "--template",
        dest="template",
        type=str,
        help="Template folder (for files with <xxxx> values)",
    )

    parser.add_argument(
        "--tool",
        "--entry",
        dest="tool",
        type=str,
        help="Tool or entry section to apply, e.g. rms "
        'or eclipse, or global.FWL where "." separates levels',
    )
    parser.add_argument(
        "--sep",
        dest="sep",
        type=str,
        default=",",
        help="Separator string for table mode",
    )

    if len(args) < 2:
        parser.print_help()
        print("QUIT")
        raise SystemExit

    return parser.parse_args(args)


def main(args=None):
    """The fmuconfigrunner is a script that takes ..."""

    args = _do_parse_args(args)

    cfg = fmu_config.ConfigParserFMU()

    logger.info("OK %s", cfg)

    if isinstance(args.config, str):
        if not os.path.isfile(args.config):
            raise IOError("Input file does not exist")
        cfg.parse(args.config)

    if args.mode == "ipl":
        logger.info("Mode is IPL")
        cfg.to_ipl(
            rootname=args.rootname,
            destination=args.destination,
            template=args.template,
            tool=args.tool,
        )

    elif args.mode in ("yaml", "yml"):
        logger.info("Mode is YAML")
        cfg.to_yaml(
            rootname=args.rootname,
            destination=args.destination,
            template=args.template,
            tool=args.tool,
        )

    elif args.mode in ("json", "jason"):
        logger.info("Mode is JASON")
        cfg.to_json(
            rootname=args.rootname,
            destination=args.destination,
            template=args.template,
            tool=args.tool,
        )

    elif args.mode == "table":
        logger.info("Mode is TABLE")
        cfg.to_table(
            rootname=args.rootname,
            destination=args.destination,
            template=args.template,
            entry=args.tool,
            sep=args.sep,
        )
    else:
        raise RuntimeError("Invalid options for mode")


if __name__ == "__main__":
    main()
