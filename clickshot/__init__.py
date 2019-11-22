import pkg_resources

__version__ = pkg_resources.get_distribution(__package__).version

from .config import Config
from .exceptions import ElementNotFoundError
from .region import Region
from .element import ElementConfig

__all__ = [Config, Region, ElementConfig, ElementNotFoundError]
