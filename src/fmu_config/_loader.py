import yaml
import os.path


class Loader(yaml.Loader):
    """Class for making it possible to use nested YAML files.

    Code is borrowed from David Hall:
    https://davidchall.github.io/yaml-includes.html
    """

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)
        Loader.add_constructor('!include', Loader.include)
        Loader.add_constructor('!import', Loader.include)

    def include(self, node):
        if isinstance(node, yaml.ScalarNode):
            return self.extract_file(self.construct_scalar(node))

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extract_file(filename)
            return result

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for k, v in self.construct_mapping(node).iteritems():
                result[k] = self.extract_file(v)
            return result

        else:
            print('Error:: unrecognised node type in !include statement')
            raise yaml.constructor.ConstructorError

    def extract_file(self, filename):
        filepath = os.path.join(self._root, filename)
        with open(filepath, 'r') as f:
            return yaml.load(f, Loader)
