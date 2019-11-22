import pytest
from unittest import mock
from hamcrest import assert_that, is_, contains_string, calling, raises
from pathlib import Path

from clickshot import Config, Region, ElementConfig, ElementNotFoundError
from clickshot.element import Element


@pytest.fixture
def config():
    config = mock.create_autospec(Config, spec_set=True, instance=True)
    config.image_dir = "images/"
    config.screenshot_dir = "screenshots/"
    config.click_retry_seconds = 30
    return config


@pytest.fixture
def region(config):
    region = mock.create_autospec(Region, instance=True)
    region._name = "my_region"
    region._boundary = (5, 10, 20, 30)
    region._config = config
    return region


@mock.patch("clickshot.element.Mouse", autospec=True, spec_test=True)
@mock.patch("clickshot.element.Locater", autospec=True, spec_set=True)
class TestClick:
    def test_element_is_clicked(self, Locater, Mouse, region):
        Locater().locate.return_value = (0, 15, 10, 20)
        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        element.click()

        Mouse().click.assert_called_with(x=5, y=25)
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), region._boundary,
        )

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_element_is_clicked_if_found_just_before_timeout(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, (0, 15, 10, 20)),
            (31, (0, 15, 10, 20)),
            (41, (0, 15, 10, 20)),
            (51, (0, 15, 10, 20)),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        element.click()

        Mouse().click.assert_called_with(x=5, y=25)
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), region._boundary
        )
        assert_that(next(time.monotonic.side_effect), is_(31))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_exception_raised_if_element_not_found_after_timeout(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, ElementNotFoundError()),
            (31, ElementNotFoundError()),
            (41, ElementNotFoundError()),
            (51, ElementNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        assert_that(calling(element.click), raises(ElementNotFoundError))

        assert_that(next(time.monotonic.side_effect), is_(41))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_exception_raised_if_element_not_found_after_custom_timeout(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, ElementNotFoundError()),
            (31, ElementNotFoundError()),
            (41, ElementNotFoundError()),
            (51, ElementNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        assert_that(
            calling(element.click).with_args(timeout_seconds=40),
            raises(ElementNotFoundError),
        )

        assert_that(next(time.monotonic.side_effect), is_(51))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_screenshot_saved_if_element_not_found_after_retries(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, ElementNotFoundError()),
            (31, ElementNotFoundError()),
            (41, ElementNotFoundError()),
            (51, ElementNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            element.click()

        element.save_last_screenshot.assert_called()

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_screenshot_saved_if_image_file_not_found_after_retries(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, FileNotFoundError()),
            (11, FileNotFoundError()),
            (21, FileNotFoundError()),
            (29, FileNotFoundError()),
            (31, FileNotFoundError()),
            (41, FileNotFoundError()),
            (51, FileNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(FileNotFoundError):
            element.click()

        element.save_last_screenshot.assert_called()
        assert_that(next(time.monotonic.side_effect), is_(41))

    def test_click_offset_is_applied(self, Locater, Mouse, region):
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", click_offset=(2, 3)), region,
        )
        element.click()

        Mouse().click.assert_called_with(x=7, y=28)

    def test_failsafe_aborts_click_attempt(self, Locater, Mouse, region):
        Locater().locate.side_effect = ElementNotFoundError()
        Mouse().get_position.return_value = (0, 0)

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            with pytest.warns(UserWarning):
                element.click()

    def test_mouse_is_moved_away_from_failsafe(self, Locater, Mouse, region):
        Locater().locate.return_value = (0, 15, 10, 20)
        Mouse().get_position.return_value = (0, 0)

        element = Element(ElementConfig(name="my_element"), region)
        element.click()

        Mouse().move_to.assert_called_with(x=10, y=10)


@mock.patch("clickshot.element.Mouse", autospec=True, spec_set=True)
@mock.patch("clickshot.element.Locater", autospec=True, spec_set=True)
class TestIsVisible:
    def test_returns_true_if_element_is_found(self, Locater, Mouse, region):
        Locater().locate.return_value = (0, 15, 10, 20)
        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible()

        assert_that(result, is_(True))
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), region._boundary
        )

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_true_if_found_just_before_timeout(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, (0, 15, 10, 20)),
            (31, (0, 15, 10, 20)),
            (41, (0, 15, 10, 20)),
            (51, (0, 15, 10, 20)),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible(timeout_seconds=30)

        assert_that(result, is_(True))
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), region._boundary,
        )
        assert_that(next(time.monotonic.side_effect), is_(31))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_false_if_element_not_found_after_timeout(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, ElementNotFoundError()),
            (31, ElementNotFoundError()),
            (41, ElementNotFoundError()),
            (51, ElementNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible(timeout_seconds=30)

        assert_that(result, is_(False))
        assert_that(next(time.monotonic.side_effect), is_(41))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_false_if_element_not_found_with_no_timeout_by_default(
        self, time, Locater, Mouse, region
    ):
        locate_timing = [
            (0, ElementNotFoundError()),
            (11, ElementNotFoundError()),
            (21, ElementNotFoundError()),
            (29, ElementNotFoundError()),
            (31, ElementNotFoundError()),
            (41, ElementNotFoundError()),
            (51, ElementNotFoundError()),
        ]

        time.monotonic.side_effect = [s[0] for s in locate_timing]
        Locater().locate.side_effect = [s[1] for s in locate_timing]

        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible()

        assert_that(result, is_(False))
        assert_that(next(time.monotonic.side_effect), is_(21))

    def test_failsafe_aborts_is_visible_attempt(self, Locater, Mouse, region):
        Locater().locate.side_effect = ElementNotFoundError()
        Mouse().get_position.return_value = (0, 0)

        element = Element(ElementConfig(name="my_element"), region)

        with pytest.warns(UserWarning):
            result = element.is_visible(30)

        assert_that(result, is_(False))

    def test_mouse_is_moved_away_from_failsafe(self, Locater, Mouse, region):
        Locater().locate.return_value = (0, 15, 10, 20)
        Mouse().get_position.return_value = (0, 0)

        element = Element(ElementConfig(name="my_element"), region)

        element.is_visible(30)

        Mouse().move_to.assert_called_with(10, 10)


@mock.patch("clickshot.element.Locater", autospec=True)
class TestSaveLastScreenshot:
    def test_screenshot_saved(self, Locater, region, capsys):
        screenshot = mock.Mock()
        Locater().last_screenshot = screenshot
        screenshot.save.return_value = "screenshots/my_region-my-element.png"

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot()

        screenshot.save.assert_called_with(Path("screenshots/my_region-my_element.png"))

        stdout = capsys.readouterr().out
        assert_that(
            stdout, contains_string("Expected Image: images/my_region-my_element.png\n")
        )
        assert_that(
            stdout,
            contains_string("Screenshot: screenshots/my_region-my-element.png\n"),
        )

    def test_screenshot_not_saved_if_it_is_none(self, Locater, region):
        Locater().last_screenshot = None

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot()


class TestStr:
    def test_string_representation_is_informative(self, region):
        element = Element(ElementConfig(name="my_element"), region)

        assert_that(str(element), is_("<Element name='my_element'>"))
