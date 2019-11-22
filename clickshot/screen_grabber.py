import cv2
from mss import mss
import numpy

from .image import Image


class ScreenGrabber:
    def __init__(self):
        self._mss = mss()

    def grab(self, rect=None):
        if rect is None:
            monitor = self._mss.monitors[0]
        else:
            monitor = {
                "left": rect[0],
                "top": rect[1],
                "width": rect[2],
                "height": rect[3],
            }

        rgba_screenshot = numpy.array(self._mss.grab(monitor))
        rgb_screenshot = cv2.cvtColor(rgba_screenshot, cv2.COLOR_RGBA2RGB)

        expected_shape = (monitor["height"], monitor["width"])
        if rgb_screenshot.shape[:2] != expected_shape:
            return Image(
                cv2.resize(rgb_screenshot, (monitor["width"], monitor["height"]))
            )

        return Image(rgb_screenshot)
