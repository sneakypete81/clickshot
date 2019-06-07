from pathlib import Path
import pyautogui


class Locater:
    last_screenshot = None

    def location_matches_expected(self, image_path, expected_rect):
        screenshot = pyautogui.screenshot(region=expected_rect)
        self.last_screenshot = screenshot

        if not Path(image_path).exists():
            return False

        result = pyautogui.locate(str(image_path), screenshot)
        return result is not None

    def locate(self, image_path, boundary):
        screenshot = pyautogui.screenshot(region=boundary)
        self.last_screenshot = screenshot

        # FileNotFoundError if the image doesn't exist
        Path(image_path).resolve(strict=True)

        result = pyautogui.locate(str(image_path), screenshot)
        if result is None:
            raise ElementNotFoundError()

        return result


class ElementNotFoundError(Exception):
    pass
