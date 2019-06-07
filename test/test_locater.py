import pytest
from unittest import mock
from unittest.mock import patch
from hamcrest import assert_that, is_, calling, raises
from pathlib import Path

from clickshot import ElementNotFoundError
from clickshot.locater import Locater


@patch("clickshot.locater.pyautogui")
@patch("clickshot.locater.Path.exists", autospec=True, spec_set=True, return_value=True)
class TestLocationMatchesExpected:
    def test_returns_true_if_image_is_in_the_screenshot(self, exists_mock, pyautogui):
        pyautogui.locate.return_value = (1, 2, 3, 4)

        result = Locater().location_matches_expected("image", (10, 20))

        assert_that(result, is_(True))

    def test_returns_false_if_image_is_outside_the_screenshot(
        self, exists_mock, pyautogui
    ):
        pyautogui.locate.return_value = None

        result = Locater().location_matches_expected("image", (10, 20))

        assert_that(result, is_(False))

    def test_returns_false_if_image_file_doesnt_exist(self, exists_mock, pyautogui):
        exists_mock.return_value = False

        result = Locater().location_matches_expected("image", (10, 20))

        assert_that(result, is_(False))

    def test_pyautogui_api_is_called_correctly(self, exists_mock, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        Locater().location_matches_expected("image", (10, 20))

        pyautogui.screenshot.assert_called_with(region=(10, 20))
        pyautogui.locate.assert_called_with("image", "Screenshot")

    def test_converts_path_to_str(self, exists_mock, pyautogui):
        Locater().location_matches_expected(Path("image"), (10, 20))

        pyautogui.locate.assert_called_with("image", mock.ANY)


@patch("clickshot.locater.pyautogui")
@patch("clickshot.locater.Path.resolve", autospec=True, spec_set=True)
class TestLocate:
    def test_returns_location_if_element_is_found(self, resolve_mock, pyautogui):
        pyautogui.locate.return_value = (4, 5, 6, 7)

        result = Locater().locate("image", (1, 2, 3, 4))

        assert_that(result, is_((4, 5, 6, 7)))

    def test_raises_error_if_element_is_not_found(self, resolve_mock, pyautogui):
        pyautogui.locate.return_value = None

        assert_that(
            calling(Locater().locate).with_args("image", (1, 2, 3, 4)),
            raises(ElementNotFoundError),
        )

    def test_raises_error_if_image_file_doesnt_exist(self, resolve_mock, pyautogui):
        resolve_mock.side_effect = FileNotFoundError

        assert_that(
            calling(Locater().locate).with_args("image", (1, 2, 3, 4)),
            raises(FileNotFoundError),
        )

    def test_screenshot_if_image_file_doesnt_exist(self, resolve_mock, pyautogui):
        resolve_mock.side_effect = FileNotFoundError

        with pytest.raises(FileNotFoundError):
            Locater().locate("image", (1, 2, 3, 4)),

        pyautogui.screenshot.assert_called()

    def test_pyautogui_api_is_called_correctly(self, resolve_mock, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        Locater().locate("image", (10, 20))

        pyautogui.screenshot.assert_called_with(region=(10, 20))
        pyautogui.locate.assert_called_with("image", "Screenshot")


@patch("clickshot.locater.pyautogui")
@patch("clickshot.locater.Path.resolve", autospec=True, spec_set=True)
class TestLastScreenshot:
    def test_last_screenshot_is_none_by_default(self, resolve_mock, pyautogui):
        locater = Locater()

        assert_that(locater.last_screenshot, is_(None))

    def test_last_screenshot_is_updated_by_location_matches_expected(
        self, resolve_mock, pyautogui
    ):
        pyautogui.screenshot.return_value = "Screenshot"

        locater = Locater()
        locater.location_matches_expected("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_("Screenshot"))

    def test_last_screenshot_is_updated_by_locate(self, resolve_mock, pyautogui):
        pyautogui.screenshot.return_value = "Screenshot"

        locater = Locater()
        locater.locate("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_("Screenshot"))
