from pathlib import Path
import time
from typing import NamedTuple, Optional, Tuple, TYPE_CHECKING
import warnings

from .exceptions import ElementNotFoundError
from .locater import Locater
from .mouse import Mouse, Button
from .retry import retry_with_timeout, RetryAbort
from .types import Rect

if TYPE_CHECKING:
    from .region import Region


class ElementConfig(NamedTuple):
    name: str
    click_offset: Optional[Tuple[int, int]] = None


class Element:
    def __init__(self, element_config: ElementConfig, region: "Region") -> None:
        self.boundary = region._boundary
        self.config = region._config

        self.name = element_config.name
        self.full_name = f"{region._name}-{element_config.name}"
        self.image_path = (Path(self.config.image_dir) / self.full_name).with_suffix(
            ".png"
        )

        if element_config.click_offset is None:
            self.click_offset = (0, 0)
        else:
            self.click_offset = element_config.click_offset

        self._locater = Locater()
        self._mouse = Mouse()

    def __str__(self) -> str:
        return f"<Element name='{self.name}'>"

    def click(
        self,
        button: Button = Button.left,
        count: int = 1,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        if timeout_seconds is None:
            timeout_seconds = self.config.timeout_seconds

        print(f"Clicking {self.full_name}: ", end="", flush=True)

        try:
            x, y = self._locate_centre_with_retry(timeout_seconds)
        except Exception:
            self.save_last_screenshot()
            raise

        self._mouse.position = (x + self.click_offset[0], y + self.click_offset[1])
        time.sleep(0.01)
        self._mouse.click(button=button, count=count)
        print("Done")

    def is_visible(self, timeout_seconds: int = 0) -> bool:
        try:
            self._locate_centre_with_retry(timeout_seconds)
            return True
        except ElementNotFoundError:
            return False

    def wait_until_visible(self, timeout_seconds: Optional[int] = None,) -> None:
        if timeout_seconds is None:
            timeout_seconds = self.config.timeout_seconds

        print(f"Waiting for {self.full_name}: ", end="", flush=True)

        try:
            self._locate_centre_with_retry(timeout_seconds)
        except Exception:
            self.save_last_screenshot()
            raise

        print("Done")

    def _locate_centre_with_retry(self, timeout_seconds: int) -> Tuple[int, int]:
        # Ensure the mouse isn't in the abort position
        if self._mouse.position == (0, 0):
            self._mouse.position = (10, 10)

        rect = retry_with_timeout(self._locate, timeout_seconds, log=True)
        return self._find_centre(rect)

    def _locate(self) -> Rect:
        try:
            return self._locater.locate(self.image_path, self.boundary)
        except Exception as e:
            # Abort if mouse pointer gets moved to (0, 0)
            if self._mouse.position == (0, 0):
                warnings.warn("Aborted - mouse pointer moved to (0, 0)")
                raise RetryAbort(e)
            else:
                raise e

    def save_last_screenshot(self) -> None:
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
    def _find_centre(rect: Rect) -> Tuple[int, int]:
        return (rect.left + rect.width // 2, rect.top + rect.height // 2)
