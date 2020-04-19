import pytest
from unittest import mock
from hamcrest import assert_that, is_, has_item, contains_string, calling, raises
from pathlib import Path

from clickshot import Button, Config, ElementConfig, ElementNotFoundError, Rect, Region
from clickshot.element import Element


@pytest.fixture
def config():
    config = mock.create_autospec(Config, spec_set=True, instance=True)
    config.image_dir = "images/"
    config.screenshot_dir = "screenshots/"
    config.timeout_seconds = 30
    return config


@pytest.fixture
def region(config):
    region = mock.create_autospec(Region, instance=True)
    region._name = "my_region"
    region._boundary = Rect(left=5, top=10, width=20, height=30)
    region._config = config
    return region


class TestClick:
    def test_element_is_clicked(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mocker.Mock()

        element.click()

        assert_that(Mouse().position, is_((5, 25)))
        Mouse().click.assert_called_with(button=Button.left, count=1)

    def test_exception_raised_if_element_not_found(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        retry_with_timeout.side_effect = ElementNotFoundError()

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        assert_that(calling(element.click), raises(ElementNotFoundError))

    def test_default_timeout_is_30(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mocker.Mock()

        element.click()

        retry_with_timeout.assert_called_with(mocker.ANY, 30)

    def test_custom_timeout_can_be_set(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mocker.Mock()

        element.click(timeout_seconds=50)

        retry_with_timeout.assert_called_with(mocker.ANY, 50)

    def test_screenshot_saved_if_element_not_found(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        retry_with_timeout.side_effect = ElementNotFoundError()

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            element.click()

        element.save_last_screenshot.assert_called()

    def test_screenshot_saved_if_image_file_not_found(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        retry_with_timeout.side_effect = FileNotFoundError()

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(FileNotFoundError):
            element.click()

        element.save_last_screenshot.assert_called()

    def test_click_offset_is_applied(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)

        element = Element(
            ElementConfig(name="my_element", click_offset=(2, 3)), region,
        )
        element.click()

        assert_that(Mouse().position, is_((7, 28)))
        Mouse().click.assert_called_with(button=Button.left, count=1)

    def test_click_parameters_are_applied(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)

        element = Element(
            ElementConfig(name="my_element", click_offset=(2, 3)), region,
        )
        element.click(button=Button.right, count=2)

        assert_that(Mouse().position, is_((7, 28)))
        Mouse().click.assert_called_with(button=Button.right, count=2)

    def test_failsafe_aborts_click_attempt(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        position_mock = mocker.PropertyMock(return_value=(0, 0))
        type(Mouse()).position = position_mock

        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.side_effect = ElementNotFoundError()

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot = mock.Mock()

        with pytest.raises(ElementNotFoundError):
            with pytest.warns(UserWarning):
                element.click()

    def test_mouse_is_moved_away_from_failsafe(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        position_mock = mocker.PropertyMock(return_value=(0, 0))
        type(Mouse()).position = position_mock

        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)

        element = Element(ElementConfig(name="my_element"), region)
        element.click()

        assert_that(position_mock.mock_calls, has_item(mock.call((10, 10))))


class TestIsVisible:
    def test_returns_true_if_element_is_found(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)
        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible()

        assert_that(result, is_(True))
        Locater().locate.assert_called_with(
            Path("images/my_region-my_element.png"), region._boundary
        )

    def test_returns_false_if_element_not_found(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        retry_with_timeout.side_effect = ElementNotFoundError()
        element = Element(ElementConfig(name="my_element"), region)

        result = element.is_visible()

        assert_that(result, is_(False))

    def test_default_timeout_is_0(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        element = Element(ElementConfig(name="my_element"), region)

        element.is_visible()

        retry_with_timeout.assert_called_with(mocker.ANY, 0)

    def test_custom_timeout_can_be_set(self, mocker, region):
        mocker.patch("clickshot.element.Mouse")
        retry_with_timeout = mocker.patch("clickshot.element.retry_with_timeout")
        element = Element(ElementConfig(name="my_element"), region)

        element.is_visible(timeout_seconds=15)

        retry_with_timeout.assert_called_with(mocker.ANY, 15)

    def test_failsafe_aborts_is_visible_attempt(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        position_mock = mocker.PropertyMock(return_value=(0, 0))
        type(Mouse()).position = position_mock

        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.side_effect = ElementNotFoundError()

        element = Element(ElementConfig(name="my_element"), region)

        with pytest.warns(UserWarning):
            result = element.is_visible(30)

        assert_that(result, is_(False))

    def test_mouse_is_moved_away_from_failsafe(self, mocker, region):
        Mouse = mocker.patch("clickshot.element.Mouse")
        position_mock = mocker.PropertyMock(return_value=(0, 0))
        type(Mouse()).position = position_mock

        Locater = mocker.patch("clickshot.element.Locater")
        Locater().locate.return_value = Rect(left=0, top=15, width=10, height=20)

        element = Element(ElementConfig(name="my_element"), region)

        element.is_visible(30)

        assert_that(position_mock.mock_calls, has_item(mock.call((10, 10))))


class TestSaveLastScreenshot:
    def test_screenshot_saved(self, mocker, region, capsys):
        screenshot = mock.Mock()
        Locater = mocker.patch("clickshot.element.Locater")
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

    def test_screenshot_not_saved_if_it_is_none(self, mocker, region):
        Locater = mocker.patch("clickshot.element.Locater")
        Locater().last_screenshot = None

        element = Element(ElementConfig(name="my_element"), region)
        element.save_last_screenshot()


class TestStr:
    def test_string_representation_is_informative(self, region):
        element = Element(ElementConfig(name="my_element"), region)

        assert_that(str(element), is_("<Element name='my_element'>"))
