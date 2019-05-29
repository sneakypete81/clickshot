import pkg_resources

__version__ = pkg_resources.get_distribution(__package__).version

from .config import Config
from .region import Region
from .element import Element, ElementNotFoundError

__all__ = [Config, Region, Element, ElementNotFoundError]
