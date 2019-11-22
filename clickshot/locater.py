from .image import Image
from .screen_grabber import ScreenGrabber


class Locater:
    def __init__(self):
        self.last_screenshot = None
        self._grabber = ScreenGrabber()

    def locate(self, image_path, boundary):
        screenshot = self._grabber.grab(boundary)
        self.last_screenshot = screenshot

        template = Image.load(image_path)
        return screenshot.match_template(template)
