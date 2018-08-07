# -*- coding: utf-8 -*-
"""Module for basic interaction with user, including logging for debugging.

Logging is enabled by setting a environment variable::

  export FMU_LOGGING_LEVEL=INFO   # if bash; will set logging to INFO level

Other levels are DEBUG and CRITICAL. CRITICAL is default (cf. Pythons logging)

Usage of logging in scripts::

  from fmu.config import etc

  xfmu = etc.Interaction()

  logger = xfmu.basiclogger(__name__)

  logger.info('This is logging of %s', something)

User interaction::

  xfmu.echo('This is a message')
  xfmu.warn('This is a warning')
  xfmu.error('This is an error, will continue')
  xfmu.critical('This is a big error, will exit')

"""

from __future__ import division, absolute_import
from __future__ import print_function

import os
import sys
import inspect
import logging
import timeit


class _BColors:
    # local class for ANSI term color commands
    # bgcolors:
    # 40=black, 41=red, 42=green, 43=yellow, 44=blue, 45=pink, 46 cyan

    HEADER = '\033[1;96m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93;43m'
    ERROR = '\033[93;41m'
    CRITICAL = '\033[1;91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Interaction(object):
    """System for handling interaction; dialogues and messages in FMU.

    This module cooperates with the standard Python logging module.
    """

    def __init__(self):

        # a string, for Python logging:
        logginglevel = os.environ.get('FMU_LOGGING_LEVEL')

        # a number, for format, 1 is simple, 2 is more info etc
        loggingformat = os.environ.get('FMU_LOGGING_FORMAT')

        if logginglevel is None:
            self._logginglevel = 'CRITICAL'
        else:
            self._logginglevel = str(logginglevel)

        if loggingformat is None:
            self._lformatlevel = 1
        else:
            self._lformatlevel = int(loggingformat)

        self._syslevel = 1

    @property
    def logginglevel(self):
        """Will return a logging level property, e.g. logging.CRITICAL"""
        ll = logging.CRITICAL
        if self._logginglevel == 'INFO':
            ll = logging.INFO
        elif self._logginglevel == 'WARNING':
            ll = logging.WARNING
        elif self._logginglevel == 'DEBUG':
            ll = logging.DEBUG

        return ll

    @logginglevel.setter
    def logginglevel(self, level):

        validlevels = ('INFO', 'DEBUG', 'CRITICAL')
        if level in validlevels:
            self._logginglevel == level
        else:
            raise ValueError('Invalid level given, must be '
                             'in {}'.format(validlevels))

    @property
    def loggingformatlevel(self):
        return self._lformatlevel

    @property
    def loggingformat(self):
        """Returns the format string to be used in logging"""

        if self._lformatlevel <= 1:
            self._lformat = '%(name)44s %(funcName)44s '\
                + '%(levelname)8s: \t%(message)s'
        else:
            self._lformat = '%(asctime)s Line: %(lineno)4d %(name)44s '\
                + '[%(funcName)40s()]'\
                + '%(levelname)8s:'\
                + '\t%(message)s'

        return self._lformat

    @staticmethod
    def print_fmu_header(appname, appversion):
        """Prints a banner for a FMU app to STDOUT."""

        cur_version = 'Python ' + str(sys.version_info[0]) + '.'
        cur_version += str(sys.version_info[1]) + '.' \
            + str(sys.version_info[2])

        app = appname + ' (version ' + str(appversion) + ')'
        print('')
        print(_BColors.HEADER)
        print('#' * 79)
        print('#{}#'.format(app.center(77)))
        print('#{}#'.format(cur_version.center(77)))
        print('#' * 79)
        print(_BColors.ENDC)
        print('')

    def basiclogger(self, name):
        """Initiate the logger by some default settings."""

        format = self.loggingformat
        logging.basicConfig(format=format, stream=sys.stdout)
        logging.getLogger().setLevel(self.logginglevel)  # root logger!
        logging.captureWarnings(True)

        return logging.getLogger(name)

    @staticmethod
    def functionlogger(name):
        """Get the logger for functions (not top level)."""

        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        return logger

    def _testsetup(self):
        """Basic setup for FMU testing (private; only relevant for tests)"""

        path = 'TMP'
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

        testpath = './examples'

        self.test_env = True
        self.tmpdir = path
        self.testpath = testpath

        return True

    @staticmethod
    def timer(*args):
        """Without args; return the time, with a time as arg return the
        difference.

        Example::

            time1 = timer()
            for i in range(10000):
                i = i + 1
            time2 = timer(time1)
            print('Execution took {} seconds'.format(time2)

        """
        time1 = timeit.default_timer()

        if len(args) > 0:
            return time1 - args[0]
        else:
            return time1

    def echo(self, string):
        level = -5
        idx = 3

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def warn(self, string):
        """Show warnings at Runtime (pure user info/warns)."""
        level = 0
        idx = 6

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    warning = warn

    def error(self, string):
        """Issue an error, will not exit system by default"""
        level = -8
        idx = 8

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def critical(self, string, sysexit=True):
        """Issue a critical error, default is SystemExit."""
        level = -9
        idx = 9

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)
        if sysexit:
            raise SystemExit('STOP!')

    def get_callerinfo(self, caller, frame):
        the_class = self._get_class_from_frame(frame)

        # just keep the last class element
        x = str(the_class)
        x = x.split('.')
        the_class = x[-1]

        self._caller = caller
        self._callclass = the_class

        return (self._caller, self._callclass)

# =============================================================================
# Private routines
# =============================================================================

    def _get_class_from_frame(self, fr):
        args, _, _, value_dict = inspect.getargvalues(fr)
        # we check the first parameter for the frame function is
        # named 'self'
        if len(args) and args[0] == 'self':
            instance = value_dict.get('self', None)
            if instance:
                # return its class
                return getattr(instance, '__class__', None)
        # return None otherwise
        return None

    def _output(self, idx, level, string):

        prefix = ''
        endfix = ''

        if idx == 0:
            prefix = '++'
        elif idx == 1:
            prefix = '**'
        elif idx == 3:
            prefix = '>>'
        elif idx == 6:
            prefix = _BColors.WARN + '##'
            endfix = _BColors.ENDC
        elif idx == 8:
            prefix = _BColors.ERROR + '!#'
            endfix = _BColors.ENDC
        elif idx == 9:
            prefix = _BColors.CRITICAL + '!!'
            endfix = _BColors.ENDC

        prompt = False
        if level <= self._syslevel:
            prompt = True

        if prompt:
            if self._syslevel <= 1:
                print('{} {}{}'.format(prefix, string, endfix))
            else:
                ulevel = str(level)
                if (level == -5):
                    ulevel = 'M'
                if (level == -8):
                    ulevel = 'E'
                if (level == -9):
                    ulevel = 'W'
                print('{0} <{1}> [{2:23s}->{3:>33s}] {4}{5}'
                      .format(prefix, ulevel, self._callclass,
                              self._caller, string, endfix))
