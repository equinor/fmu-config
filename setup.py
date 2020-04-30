#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
from os.path import basename
from os.path import splitext
from glob import glob

from setuptools import setup, find_packages


def parse_requirements(filename):
    """Load requirements from a pip requirements file"""
    try:
        lineiter = (line.strip() for line in open(filename))
        return [line for line in lineiter if line and not line.startswith("#")]
    except IOError:
        return []


def src(fil):
    """Getting src path"""
    root = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(root, fil))


with open("README.rst") as readme_file:
    README = readme_file.read()

with open("HISTORY.rst") as history_file:
    HISTORY = history_file.read()

REQUIREMENTS = parse_requirements("requirements.txt")

# for 'python setup.py test' to work; need pytest runner:
SETUP_REQUIREMENTS = ["pytest-runner", "setuptools_scm>=3.2.0", "wheel"]

TEST_REQUIREMENTS = ["pytest"]

# entry points setting
FMUCONFIG_RUNNER = "fmuconfig=" "fmu.config.fmuconfigrunner:main"


setup(
    name="fmu_config",
    use_scm_version={"root": src(""), "write_to": src("src/fmu/config/_theversion.py")},
    description="Library for various config scripts in FMU scope",
    long_description=README + "\n\n" + HISTORY,
    author="Jan C. Rivenaes",
    author_email="jriv@equinor.com",
    url="https://git.equinor.com/fmu-utilities/fmu-config",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,
    entry_points={"console_scripts": [FMUCONFIG_RUNNER]},
    keywords="fmu, config",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
)
