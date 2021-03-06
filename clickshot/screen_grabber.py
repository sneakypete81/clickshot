from typing import Optional

import cv2
from mss import mss
import numpy

from .image import Image
from .types import Rect


class ScreenGrabber:
    def __init__(self) -> None:
        self._mss = mss()

    def grab(self, rect: Optional[Rect] = None) -> Image:
        if rect is None:
            monitor = self._mss.monitors[0]
        else:
            monitor = rect._asdict()

        rgba_screenshot = numpy.array(self._mss.grab(monitor))
        rgb_screenshot = cv2.cvtColor(rgba_screenshot, cv2.COLOR_RGBA2RGB)

        expected_shape = (monitor["height"], monitor["width"])
        if rgb_screenshot.shape[:2] != expected_shape:
            return Image(
                cv2.resize(rgb_screenshot, (monitor["width"], monitor["height"]))
            )

        return Image(rgb_screenshot)
