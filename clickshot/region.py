from collections import namedtuple
from pathlib import Path
import inspect

from .element import Element


def Region(name, config, element_configs, boundary=None):
    element_names = [element.name for element in element_configs]

    if config.image_dir is None:
        config = config._replace(image_dir=(_get_calling_dir() / "images"))

    if config.screenshot_dir is None:
        config = config._replace(screenshot_dir=(_get_calling_dir() / "screenshots"))

    class Region(namedtuple("RegionBase", element_names)):
        def __new__(cls, name, config, element_configs, boundary):
            cls._name = name
            cls._config = config
            cls._boundary = boundary

            elements = [Element(element, cls) for element in element_configs]
            return super().__new__(cls, *elements)

    return Region(name, config, element_configs, boundary)


def _get_calling_dir():
    return Path(inspect.stack()[2].filename).parent
