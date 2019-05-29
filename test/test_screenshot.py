from unittest import mock
from hamcrest import assert_that, is_
from pathlib import Path

from clickshot.screenshot import save_screenshot


@mock.patch("clickshot.screenshot.Path.exists", autospec=True, spec_set=True)
@mock.patch("clickshot.screenshot.Path.mkdir", autospec=True, spec_set=True)
class TestSaveScreenshot:
    def test_screenshot_dir_is_created_if_necessary(self, mkdir_mock, exists_mock):
        screenshot = mock.Mock()

        exists_mock.return_value = False

        save_screenshot(screenshot, "/screenshot_dir", "screenshot_name")

        mkdir_mock.assert_called_with(Path("/screenshot_dir"), exist_ok=True)

    def test_screenshot_is_saved(self, mkdir_mock, exists_mock):
        screenshot = mock.Mock()
        exists_mock.return_value = False

        save_screenshot(screenshot, "/screenshot_dir", "screenshot_name")

        screenshot.save.assert_called_with(Path("/screenshot_dir/screenshot_name.png"))

    def test_screenshot_path_is_returned(self, mkdir_mock, exists_mock):
        screenshot = mock.Mock()
        exists_mock.return_value = False

        result = save_screenshot(screenshot, "/screenshot_dir", "screenshot_name")

        assert_that(result, is_(Path("/screenshot_dir/screenshot_name.png")))

    def test_unique_name_with_existing_screenshot(self, mkdir_mock, exists_mock):
        screenshot = mock.Mock()
        exists_mock.side_effect = [True, False]

        result = save_screenshot(screenshot, "/screenshot_dir", "screenshot_name")

        assert_that(result, is_(Path("/screenshot_dir/screenshot_name_2.png")))

    def test_unique_name_with_two_existing_screenshots(self, mkdir_mock, exists_mock):
        screenshot = mock.Mock()
        exists_mock.side_effect = [True, True, False]

        result = save_screenshot(screenshot, "/screenshot_dir", "screenshot_name")

        assert_that(result, is_(Path("/screenshot_dir/screenshot_name_3.png")))
