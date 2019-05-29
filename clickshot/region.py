from collections import namedtuple

from .element import ConfiguredElement


def Region(name, config, elements, boundary=None):
    element_names = [element.name for element in elements]

    class Region(namedtuple("RegionBase", element_names)):
        def __new__(cls, name, config, elements, boundary):
            cls._name = name
            cls._config = config
            cls._boundary = boundary
            configured_elements = [
                ConfiguredElement(element, cls) for element in elements
            ]
            return super().__new__(cls, *configured_elements)

    return Region(name, config, elements, boundary)
