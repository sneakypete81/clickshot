import pytest
from unittest import mock
from hamcrest import assert_that, is_, contains_string
from pathlib import Path

from clickshot import Config, Region, ElementConfig, ElementNotFoundError
from clickshot.element import Element


@pytest.fixture
def config():
    config = mock.create_autospec(Config, spec_set=True, instance=True)
    config.image_dir = "images/"
    config.screenshot_dir = "screenshots/"
    config.click_retry_seconds = 30
    config.screenshot_scaling = 1
    config.warn_for_delayed_detections = False
    return config


@pytest.fixture
def region(config):
    region = mock.create_autospec(Region, spec_set=True, instance=True)
    region._name = "my_region"
    region._boundary = (5, 10, 20, 30)
    region._config = config
    return region


@mock.patch("clickshot.element.pyautogui")
@mock.patch("clickshot.element.Locater", autospec=True, spec_set=True)
class TestClick:
    def test_element_is_clicked_if_location_matches_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = True

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        element.click()

        Locater().location_matches_expected.assert_called_with(
            Path("images/my_region-my_element.png"), (0, 15, 10, 20)
        )
        pyautogui.click.assert_called_with(5, 25)

    def test_click_offset_is_applied(self, Locater, pyautogui, region):
        Locater().location_matches_expected.return_value = True

        element = Element(
            ElementConfig(
                name="my_element", expected_rect=(0, 15, 10, 20), click_offset=(2, 3)
            ),
            region,
        )
        element.click()

        pyautogui.click.assert_called_with(7, 28)

    def test_screenshot_scaling_is_applied(self, Locater, pyautogui, region):
        Locater().location_matches_expected.return_value = True
        region._config.screenshot_scaling = 2

        element = Element(
            ElementConfig(
                name="my_element", expected_rect=(0, 15, 10, 20), click_offset=(2, 3)
            ),
            region,
        )
        element.click()

        pyautogui.click.assert_called_with(3, 14)

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_post_click_delay_seconds_are_applied(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = True

        element = Element(
            ElementConfig(
                name="my_element",
                expected_rect=(0, 15, 10, 20),
                post_click_delay_seconds=3.4,
            ),
            region,
        )
        element.click()

        time.sleep.assert_called_with(3.4)

    @pytest.mark.filterwarnings("ignore:Location of my_element")
    def test_element_is_clicked_if_location_doesnt_match_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(99, 15, 10, 20)), region
        )
        element.click()

        Locater().location_matches_expected.assert_called_with(
            Path("images/my_region-my_element.png"), (99, 15, 10, 20)
        )
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), (5, 10, 20, 30)
        )
        pyautogui.click.assert_called_with(5, 25)

    def test_warning_raised_if_location_doesnt_match_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(99, 15, 10, 20)), region
        )

        with pytest.warns(UserWarning):
            element.click()

    def test_warning_raised_if_expected_location_is_none(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(ElementConfig(name="my_element", expected_rect=None), region)

        with pytest.warns(UserWarning):
            element.click()

    def test_element_is_clicked_even_if_not_present_immediately(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        element.click()

        pyautogui.click.assert_called_with(5, 25)

    def test_warning_raised_if_enabled_and_element_not_present_immediately(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)
        region._config.warn_for_delayed_detections = True

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        with pytest.warns(UserWarning):
            element.click()

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_exception_raised_if_element_not_found_after_timeout(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = ElementNotFoundError()

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            element.click()

        assert_that(Locater().locate.call_count, is_(3))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_exception_raised_if_element_not_found_after_custom_timeout(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = ElementNotFoundError()

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            element.click(timeout_seconds=40)

        assert_that(Locater().locate.call_count, is_(4))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_element_clicked_if_found_just_before_timeout(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = [
            ElementNotFoundError(),
            ElementNotFoundError(),
            (0, 15, 10, 20),
        ]

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        element.click()

        pyautogui.click.assert_called_with(5, 25)
        assert_that(Locater().locate.call_count, is_(3))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_screenshot_saved_if_element_not_found(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = ElementNotFoundError()

        time.monotonic.side_effect = [0, 31]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            element.click()

        element.save_last_screenshot.assert_called()


@mock.patch("clickshot.element.pyautogui")
@mock.patch("clickshot.element.Locater", autospec=True, spec_set=True)
class TestIsVisible:
    def test_true_returned_if_location_matches_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = True

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        result = element.is_visible()

        assert_that(result, is_(True))
        Locater().location_matches_expected.assert_called_with(
            Path("images/my_region-my_element.png"), (0, 15, 10, 20)
        )

    @pytest.mark.filterwarnings("ignore:Location of my_element")
    def test_true_returned_if_location_doesnt_match_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(99, 15, 10, 20)), region
        )
        result = element.is_visible()

        assert_that(result, is_(True))
        Locater().location_matches_expected.assert_called_with(
            Path("images/my_region-my_element.png"), (99, 15, 10, 20)
        )
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), (5, 10, 20, 30)
        )

    def test_warning_raised_if_location_doesnt_match_expected(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(99, 15, 10, 20)), region
        )

        with pytest.warns(UserWarning):
            element.is_visible()

    def test_warning_raised_if_expected_location_is_none(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(ElementConfig(name="my_element", expected_rect=None), region)

        with pytest.warns(UserWarning):
            element.is_visible()

    def test_returns_true_even_if_not_present_immediately(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )
        result = element.is_visible()

        assert_that(result, is_(True))

    def test_warning_raised_if_enabled_and_element_not_present_immediately(
        self, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.return_value = (0, 15, 10, 20)
        region._config.warn_for_delayed_detections = True

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        with pytest.warns(UserWarning):
            element.is_visible()

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_false_if_element_not_found_after_timeout(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = ElementNotFoundError()

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        result = element.is_visible(timeout_seconds=30)

        assert_that(result, is_(False))
        assert_that(Locater().locate.call_count, is_(3))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_false_if_element_not_found_with_no_timeout_by_default(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = ElementNotFoundError()

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        result = element.is_visible()

        assert_that(result, is_(False))
        assert_that(Locater().locate.call_count, is_(1))

    @mock.patch("clickshot.element.time", autospec=True, spec_set=True)
    def test_returns_true_if_found_just_before_timeout(
        self, time, Locater, pyautogui, region
    ):
        Locater().location_matches_expected.return_value = False
        Locater().locate.side_effect = [
            ElementNotFoundError(),
            ElementNotFoundError(),
            (0, 15, 10, 20),
        ]

        time.monotonic.side_effect = [0, 11, 21, 31, 41]

        element = Element(
            ElementConfig(name="my_element", expected_rect=(0, 15, 10, 20)), region
        )

        result = element.is_visible(timeout_seconds=30)

        assert_that(result, is_(True))
        assert_that(Locater().locate.call_count, is_(3))


@mock.patch("clickshot.element.save_screenshot", autospec=True, spec_set=True)
@mock.patch("clickshot.element.Locater", autospec=True, spec_set=True)
class TestSaveLastScreenshot:
    def test_screenshot_saved(self, Locater, save_screenshot, region, capsys):
        screenshot = mock.sentinel.screenshot
        Locater().last_screenshot = screenshot
        save_screenshot.return_value = "screenshots/my_region-my-element.png"

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot()

        save_screenshot.assert_called_with(
            screenshot, "screenshots/", "my_region-my_element"
        )

        stdout = capsys.readouterr().out
        assert_that(
            stdout, contains_string("Expected Image: images/my_region-my_element.png\n")
        )
        assert_that(
            stdout,
            contains_string("Screenshot: screenshots/my_region-my-element.png\n"),
        )

    def test_screenshot_not_saved_if_it_is_none(self, Locater, save_screenshot, region):
        Locater().last_screenshot = None

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot()

        assert_that(save_screenshot.called, is_(False))


class TestStr:
    def test_string_representation_is_informative(self, region):
        element = Element(ElementConfig(name="my_element"), region)

        assert_that(str(element), is_("<Element name='my_element'>"))
