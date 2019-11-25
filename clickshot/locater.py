from pathlib import Path
from typing import Optional, Union

from .image import Image
from .screen_grabber import ScreenGrabber
from .types import Rect


class Locater:
    def __init__(self) -> None:
        self.last_screenshot: Optional[Image] = None
        self._grabber = ScreenGrabber()

    def locate(self, image_path: Union[Path, str], boundary: Optional[Rect]) -> Rect:
        screenshot = self._grabber.grab(boundary)
        self.last_screenshot = screenshot

        template = Image.load(image_path)
        return screenshot.match_template(template)
