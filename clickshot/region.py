from collections import namedtuple

from .element import Element


def Region(name, config, element_configs, boundary=None):
    element_names = [element.name for element in element_configs]

    class Region(namedtuple("RegionBase", element_names)):
        def __new__(cls, name, config, element_configs, boundary):
            cls._name = name
            cls._config = config
            cls._boundary = boundary
            elements = [
                Element(element, cls) for element in element_configs
            ]
            return super().__new__(cls, *elements)

    return Region(name, config, element_configs, boundary)
