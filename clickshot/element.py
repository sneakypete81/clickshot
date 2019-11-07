import time
import warnings
from typing import NamedTuple
from pathlib import Path

import pyautogui

from .locater import Locater, ElementNotFoundError
from .screenshot import save_screenshot


class ElementConfig(NamedTuple):
    name: str
    expected_rect: tuple = None
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
        self.expected_rect = element.expected_rect

        self.click_offset = element.click_offset
        if self.click_offset is None:
            self.click_offset = (0, 0)

        self._locater = Locater()

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

        pyautogui.click(
            (x + self.click_offset[0]) // self.config.screenshot_scaling,
            (y + self.click_offset[1]) // self.config.screenshot_scaling,
        )

    def is_visible(self, timeout_seconds=0):
        try:
            self._locate_centre_with_retry(timeout_seconds)
            return True
        except ElementNotFoundError:
            return False

    def _locate_centre_with_retry(self, timeout_seconds):
        if self.expected_rect is None:
            rect = self._locate_with_retry(timeout_seconds)
        else:
            if self._location_matches_expected_with_retry(timeout_seconds):
                rect = self.expected_rect
            else:
                # Element is not where we expected it to be, so search in the boundary
                rect = self._locate()

        self._issue_warnings(rect)
        return self._find_centre(rect)

    def _locate_with_retry(self, timeout_seconds):
        start_time = time.monotonic()
        while True:
            try:
                return self._locate()
            except (ElementNotFoundError, FileNotFoundError):
                elapsed_time = time.monotonic() - start_time
                if elapsed_time > timeout_seconds:
                    raise

    def _locate(self):
        return self._locater.locate(self.image_path, self.boundary)

    def _location_matches_expected_with_retry(self, timeout_seconds):
        start_time = time.monotonic()
        while True:
            if self._location_matches_expected():
                return True
            if time.monotonic() - start_time > timeout_seconds:
                return False

    def _location_matches_expected(self):
        return self._locater.location_matches_expected(
            self.image_path, self.expected_rect
        )

    def _issue_warnings(self, rect):
        if rect == self.expected_rect:
            return

        if self.expected_rect is None:
            warnings.warn(
                f"Location of {self.name} {tuple(rect)} " f"has not been defined."
            )
        else:
            warnings.warn(
                f"Location of {self.name} {tuple(rect)} "
                f"doesn't match expected {self.expected_rect}."
            )

    def save_last_screenshot(self):
        screenshot = self._locater.last_screenshot
        if screenshot is None:
            return

        screenshot_path = save_screenshot(
            screenshot, self.config.screenshot_dir, self.full_name
        )

        print(f"Expected Image: {self.image_path}")
        print(f"Screenshot: {screenshot_path}")

        if self.expected_rect is not None:
            self._save_cropped_screenshot(screenshot)

    def _save_cropped_screenshot(self, screenshot):
        box = self._rect_to_box(self.expected_rect)
        cropped_screenshot = screenshot.crop(box)

        screenshot_path = save_screenshot(
            cropped_screenshot, self.config.screenshot_dir, self.full_name + "-cropped"
        )
        print(f"Cropped Screenshot: {screenshot_path}")

    @staticmethod
    def _find_centre(rect):
        return (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)

    @staticmethod
    def _rect_to_box(rect):
        return (rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3])
