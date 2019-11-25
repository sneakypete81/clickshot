import inspect
from pathlib import Path
from typing import Dict, List, Optional

from .config import Config
from .element import Element, ElementConfig
from .types import Rect


class Region:
    def __init__(self, name: str, config: Config, boundary: Optional[Rect] = None):
        self._name = name
        self._boundary = boundary
        self._config = config
        self._elements: Dict[str, Element] = {}

        if self._config.image_dir == "":
            self._config = self._config._replace(
                image_dir=str(_get_calling_dir() / "images")
            )
        if self._config.screenshot_dir == "":
            self._config = self._config._replace(
                screenshot_dir=str(_get_calling_dir() / "screenshots")
            )

    def configure(self, element_configs: List[ElementConfig]) -> "Region":
        self._elements = {e.name: Element(e, self) for e in element_configs}
        return self

    def __getattr__(self, name: str) -> Element:
        if name not in self._elements:
            self._elements[name] = Element(ElementConfig(name), self)
        return self._elements[name]


def _get_calling_dir() -> Path:
    return Path(inspect.stack()[2].filename).parent
