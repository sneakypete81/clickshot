import inspect
from pathlib import Path
import platform
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
                image_dir=_get_image_dir(inspect.stack())
            )
        if self._config.screenshot_dir == "":
            self._config = self._config._replace(
                screenshot_dir=_get_screenshot_dir(inspect.stack())
            )

    def configure(self, element_configs: List[ElementConfig]) -> "Region":
        self._elements = {e.name: Element(e, self) for e in element_configs}
        return self

    def __getattr__(self, name: str) -> Element:
        if name not in self._elements:
            self._elements[name] = Element(ElementConfig(name), self)
        return self._elements[name]


def _get_image_dir(stack: List[inspect.FrameInfo]) -> str:
    image_dir = _get_calling_dir(stack) / "images"

    if platform.system().lower() == "darwin":
        mac_release_dir = image_dir / f"{platform.system()}-{platform.mac_ver()[0]}"
        if mac_release_dir.exists():
            return str(mac_release_dir)

    release_dir = image_dir / f"{platform.system()}-{platform.release()}"
    if release_dir.exists():
        return str(release_dir)

    system_dir = image_dir / platform.system()
    if system_dir.exists():
        return str(system_dir)

    return str(image_dir)


def _get_screenshot_dir(stack: List[inspect.FrameInfo]) -> str:
    return str(_get_calling_dir(stack) / "screenshots")


def _get_calling_dir(stack: List[inspect.FrameInfo]) -> Path:
    return Path(stack[1].filename).parent
