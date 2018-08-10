# -*- coding: utf-8 -*-
"""Loading nested configs for FMU"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

import yaml


class Loader(yaml.Loader):
    """Class for making it possible to use nested YAML files.

    Code is borrowed from David Hall:
    https://davidchall.github.io/yaml-includes.html
    """
    # pylint: disable=too-many-ancestors

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)
        Loader.add_constructor('!include', Loader.include)
        Loader.add_constructor('!import', Loader.include)

    def include(self, node):
        """Include method"""

        result = None
        if isinstance(node, yaml.ScalarNode):
            result = self.extract_file(self.construct_scalar(node))

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extract_file(filename)

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for knum, val in self.construct_mapping(node).items():
                result[knum] = self.extract_file(val)

        else:
            print('Error:: unrecognised node type in !include statement')
            raise yaml.constructor.ConstructorError

        return result

    def extract_file(self, filename):
        """Extract file method"""

        filepath = os.path.join(self._root, filename)
        with open(filepath, 'r') as yfile:
            return yaml.load(yfile, Loader)
