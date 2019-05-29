from unittest import mock
from hamcrest import assert_that, is_, calling, raises
from pathlib import Path

from clickshot import ElementNotFoundError
from clickshot.locater import Locater


@mock.patch("clickshot.locater.pyautogui")
class TestLocationMatchesExpected:
    def test_returns_false_if_expected_is_none(self, pyautogui):
        result = Locater().location_matches_expected("image", None)

        assert_that(result, is_(False))

    def test_returns_true_if_image_is_in_the_screenshot(self, pyautogui):
        pyautogui.locate.return_value = (1, 2, 3, 4)

        result = Locater().location_matches_expected("image", (10, 20))

        assert_that(result, is_(True))

    def test_returns_false_if_image_is_outside_the_screenshot(self, pyautogui):
        pyautogui.locate.return_value = None

        result = Locater().location_matches_expected("image", (10, 20))

        assert_that(result, is_(False))

    def test_pyautogui_api_is_called_correctly(self, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        Locater().location_matches_expected("image", (10, 20))

        pyautogui.screenshot.assert_called_with(region=(10, 20))
        pyautogui.locate.assert_called_with("image", "Screenshot")

    def test_converts_path_to_str(self, pyautogui):
        Locater().location_matches_expected(Path("image"), (10, 20))

        pyautogui.locate.assert_called_with("image", mock.ANY)


@mock.patch("clickshot.locater.pyautogui")
class TestLocate:
    def test_returns_location_if_element_is_found(self, pyautogui):
        pyautogui.locate.return_value = (4, 5, 6, 7)

        result = Locater().locate("image", (1, 2, 3, 4))

        assert_that(result, is_((4, 5, 6, 7)))

    def test_raises_error_if_element_is_not_found(self, pyautogui):
        pyautogui.locate.return_value = None

        assert_that(
            calling(Locater().locate).with_args("image", (1, 2, 3, 4)),
            raises(ElementNotFoundError),
        )

    def test_pyautogui_api_is_called_correctly(self, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        Locater().locate("image", (10, 20))

        pyautogui.screenshot.assert_called_with(region=(10, 20))
        pyautogui.locate.assert_called_with("image", "Screenshot")


@mock.patch("clickshot.locater.pyautogui")
class TestLastScreenshot:
    def test_last_screenshot_is_none_by_default(self, pyautogui):
        locater = Locater()

        assert_that(locater.last_screenshot, is_(None))

    def test_last_screenshot_is_updated_by_location_matches_expected(self, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        locater = Locater()
        locater.location_matches_expected("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_("Screenshot"))

    def test_last_screenshot_is_updated_by_locate(self, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        locater = Locater()
        locater.locate("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_("Screenshot"))
