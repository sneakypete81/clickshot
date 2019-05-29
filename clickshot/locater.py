import pyautogui


class Locater:
    last_screenshot = None

    def location_matches_expected(self, image_path, expected_rect):
        if expected_rect is None:
            return False

        screenshot = pyautogui.screenshot(region=expected_rect)
        self.last_screenshot = screenshot

        result = pyautogui.locate(str(image_path), screenshot)
        return result is not None

    def locate(self, image_path, boundary):
        screenshot = pyautogui.screenshot(region=boundary)
        self.last_screenshot = screenshot

        result = pyautogui.locate(str(image_path), screenshot)
        if result is None:
            raise ElementNotFoundError()

        return result


class ElementNotFoundError(Exception):
    pass
