from pathlib import Path
import time
from typing import NamedTuple
import warnings

from .exceptions import ElementNotFoundError
from .locater import Locater
from .mouse import Mouse, Button


class ElementConfig(NamedTuple):
    name: str
    click_offset: tuple = None


class Element:
    def __init__(self, element, region):
        self.boundary = region._boundary
        self.config = region._config

        self.name = element.name
        self.full_name = f"{region._name}-{element.name}"
        self.image_path = (Path(self.config.image_dir) / self.full_name).with_suffix(
            ".png"
        )
        self.click_offset = element.click_offset
        if self.click_offset is None:
            self.click_offset = (0, 0)

        self._locater = Locater()
        self._mouse = Mouse()

    def __str__(self):
        return f"<Element name='{self.name}'>"

    def click(self, timeout_seconds=None):
        if timeout_seconds is None:
            timeout_seconds = self.config.click_retry_seconds

        try:
            x, y = self._locate_centre_with_retry(timeout_seconds)
        except Exception:
            self.save_last_screenshot()
            raise

        self._mouse.position = (x + self.click_offset[0], y + self.click_offset[1])
        time.sleep(0.01)
        self._mouse.click(Button.left)

    def is_visible(self, timeout_seconds=0):
        try:
            self._locate_centre_with_retry(timeout_seconds)
            return True
        except ElementNotFoundError:
            return False

    def _locate_centre_with_retry(self, timeout_seconds):
        rect = self._locate_with_retry(timeout_seconds)
        return self._find_centre(rect)

    def _locate_with_retry(self, timeout_seconds):
        # Ensure the mouse isn't in the abort position
        if self._mouse.position == (0, 0):
            self._mouse.position = (10, 10)

        start_time = time.monotonic()
        while True:
            try:
                return self._locater.locate(self.image_path, self.boundary)
            except (ElementNotFoundError, FileNotFoundError):
                elapsed_time = time.monotonic() - start_time
                if elapsed_time > timeout_seconds:
                    raise

                # Abort if mouse pointer gets moved to (0, 0)
                if self._mouse.position == (0, 0):
                    warnings.warn("Aborted - mouse pointer moved to (0, 0)")
                    raise

    def save_last_screenshot(self):
        screenshot = self._locater.last_screenshot
        if screenshot is None:
            return

        screenshot_path = (
            Path(self.config.screenshot_dir) / self.full_name
        ).with_suffix(".png")

        unique_screenshot_path = screenshot.save(screenshot_path)

        print(f"Expected Image: {self.image_path}")
        print(f"Screenshot: {unique_screenshot_path}")

    @staticmethod
    def _find_centre(rect):
        return (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
