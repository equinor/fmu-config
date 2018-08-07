# -*- coding: utf-8 -*-
"""Testing the classes/functions in in the etc module."""

from __future__ import division, absolute_import
from __future__ import print_function

import pytest  # need the pytest-catchlog plugin installed!

from fmu.config import etc

xfmu = etc.Interaction()


@pytest.fixture()
def mylogger():
    # need to do it like this...
    mylogger = xfmu.basiclogger(__name__)
    mylogger.logginglevel = 'INFO'
    return mylogger


def test_info_logger(mylogger, caplog):
    """Test basic logger behaviour, will capture output to stdin"""

    mylogger.info('This is a test')
    print(caplog.text)
    assert 'This is a test' in caplog.text

    mylogger.warn('This is a warning')
    print(caplog.text)
    assert 'This is a warning' in caplog.text


def test_print_fmu_header():
    """Test writing an app header."""
    xfmu.print_fmu_header('MYAPP', '0.99')


def test_user_msg():
    """Testing user messages"""

    xfmu.echo('')
    xfmu.echo('This is a message')
    xfmu.warn('This is a warning')
    xfmu.warning('This is also a warning')
    xfmu.error('This is an error')
    xfmu.critical('This is a critical error', sysexit=False)
