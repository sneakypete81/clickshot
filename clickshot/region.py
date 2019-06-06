from pathlib import Path
import inspect

from .element import Element


class Region:
    def __init__(self, name, config, boundary=None):
        self._name = name
        self._config = config
        self._boundary = boundary
        self._elements = []

        if self._config.image_dir is None:
            self._config = self._config._replace(
                image_dir=(_get_calling_dir() / "images")
            )
        if self._config.screenshot_dir is None:
            self._config = self._config._replace(
                screenshot_dir=(_get_calling_dir() / "screenshots")
            )

    def configure(self, element_configs):
        self._elements = {e.name: Element(e, self) for e in element_configs}
        return self

    def __getattr__(self, name):
        if name not in self._elements:
            raise AttributeError()
        return self._elements[name]


def _get_calling_dir():
    return Path(inspect.stack()[2].filename).parent
