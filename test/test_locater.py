from hamcrest import assert_that, is_, calling, raises
import pytest

from clickshot import ElementNotFoundError, Rect
from clickshot.locater import Locater


class TestLocate:
    def test_returns_location_if_element_is_found(self, mocker):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")
        screenshot.match_template.return_value = Rect(left=4, top=5, width=6, height=7)

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        template = Image("Template")
        Image.load.return_value = template

        result = Locater().locate("image", Rect(left=1, top=2, width=3, height=4))

        assert_that(result, is_(Rect(left=4, top=5, width=6, height=7)))
        ScreenGrabber().grab.assert_called_with(Rect(left=1, top=2, width=3, height=4))
        Image.load.assert_called_with("image")
        screenshot.match_template.assert_called_with(template)

    def test_raises_error_if_element_is_not_found(self, mocker):
        Image = mocker.patch("clickshot.locater.Image")
        screenshot = Image("Screenshot")
        screenshot.match_template.side_effect = ElementNotFoundError

        ScreenGrabber = mocker.patch("clickshot.locater.ScreenGrabber")
        ScreenGrabber().grab.return_value = screenshot

        assert_that(
            calling(Locater().locate).with_args(
                "image", Rect(left=1, top=2, width=3, height=4)
            ),
            raises(ElementNotFoundError),
        )

    def test_raises_error_if_image_file_doesnt_exist(self, mocker):
        mocker.patch("clickshot.locater.ScreenGrabber")
        Image = mocker.patch("clickshot.locater.Image")
        Image.load.side_effect = FileNotFoundError

        assert_that(
            calling(Locater().locate).with_args(
                "image", Rect(left=1, top=2, width=3, height=4)
            ),
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
        locater.locate("image", Rect(left=1, top=2, width=3, height=4))

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
            locater.locate("image", Rect(left=1, top=2, width=3, height=4))

        assert_that(locater.last_screenshot, is_(screenshot))
