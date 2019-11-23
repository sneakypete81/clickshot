from hamcrest import assert_that, is_, calling, raises
import pytest

from clickshot import ElementNotFoundError
from clickshot.locater import Locater


class TestLocate:
    def test_returns_location_if_element_is_found(self, mocker):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")
        screenshot.match_template.return_value = (4, 5, 6, 7)

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        template = Image("Template")
        Image.load.return_value = template

        result = Locater().locate("image", (1, 2, 3, 4))

        assert_that(result, is_((4, 5, 6, 7)))
        ScreenGrabber().grab.assert_called_with((1, 2, 3, 4))
        Image.load.assert_called_with("image")
        screenshot.match_template.assert_called_with(template)

    def test_raises_error_if_element_is_not_found(self, mocker):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")
        screenshot.match_template.side_effect = ElementNotFoundError

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        assert_that(
            calling(Locater().locate).with_args("image", (1, 2, 3, 4)),
            raises(ElementNotFoundError),
        )

    def test_raises_error_if_image_file_doesnt_exist(self, mocker):
        mocker.patch("clickshot.locater.ScreenGrabber")
        Image = mocker.patch("clickshot.locater.Image")
        Image.load.side_effect = FileNotFoundError

        assert_that(
            calling(Locater().locate).with_args("image", (1, 2, 3, 4)),
            raises(FileNotFoundError),
        )


class TestLastScreenshot:
    def test_last_screenshot_is_none_by_default(self):
        locater = Locater()

        assert_that(locater.last_screenshot, is_(None))

    def test_last_screenshot_is_updated_by_locate(self, mocker):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        locater = Locater()
        locater.locate("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_(screenshot))

    def test_last_screenshot_is_updated_by_locate_if_image_file_doesnt_exist(
        self, mocker
    ):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        Image.load.side_effect = FileNotFoundError

        locater = Locater()
        with pytest.raises(FileNotFoundError):
            locater.locate("image", (1, 2, 3, 4))

        assert_that(locater.last_screenshot, is_(screenshot))
