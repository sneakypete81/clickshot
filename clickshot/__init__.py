import pkg_resources

__version__ = pkg_resources.get_distribution(__package__).version

from .config import Config
from .element import ElementConfig
from .exceptions import ElementNotFoundError
from .keyboard import Keyboard, Key, KeyCode
from .mouse import Mouse, Button
from .region import Region

__all__ = [
    Config,
    ElementConfig,
    ElementNotFoundError,
    Keyboard,
    Key,
    KeyCode,
    Mouse,
    Button,
    Region,
]
