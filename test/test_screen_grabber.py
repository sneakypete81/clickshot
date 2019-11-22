from unittest import mock
from hamcrest import assert_that, is_
import numpy
import pytest

from clickshot.screen_grabber import ScreenGrabber
from mss.screenshot import ScreenShot as PixelArray


@pytest.fixture
def pixels():
    monitor = {"left": 0, "top": 0, "width": 2, "height": 3}
    return PixelArray(range(4 * 2 * 3), monitor)


@pytest.fixture
def rgb_array():
    return numpy.array(
        [
            [[0, 1, 2], [4, 5, 6]],
            [[8, 9, 10], [12, 13, 14]],
            [[16, 17, 18], [20, 21, 22]],
        ],
        numpy.uint8,
    )


@mock.patch("clickshot.screen_grabber.mss", autospec=True, spec_set=True)
class TestGrab:
    def test_returns_rgb_image_from_mss(self, mss, pixels, rgb_array):
        grabber = ScreenGrabber()
        mss().grab.return_value = pixels

        image = grabber.grab((0, 0, 2, 3))

        numpy.testing.assert_array_equal(image.data, rgb_array)

    def test_passes_rect_parameter_to_mss(self, mss, pixels):
        grabber = ScreenGrabber()
        mss().grab.return_value = pixels

        grabber.grab((0, 1, 2, 3))

        mss().grab.assert_called_with({"left": 0, "top": 1, "width": 2, "height": 3})

    def test_defaults_to_all_monitors(self, mss, pixels):
        grabber = ScreenGrabber()
        mss().grab.return_value = pixels
        mss().monitors = [{"left": 0, "top": 1, "width": 200, "height": 300}]

        grabber.grab()

        mss().grab.assert_called_with(
            {"left": 0, "top": 1, "width": 200, "height": 300}
        )

    @mock.patch("clickshot.screen_grabber.cv2.resize", autospec=True, spec_set=True)
    def test_resizes_from_hidpi_monitor(self, resize_mock, mss, pixels, rgb_array):
        grabber = ScreenGrabber()
        mss().grab.return_value = pixels
        resize_mock.return_value = mock.sentinel.resized_image

        # Ask for a smaller region than is returned by mss().grab.
        # This indicates a HiDPI monitor, which should then be resized back to the
        # requested region size.
        image = grabber.grab((0, 0, 2, 1))

        assert_that(image.data, is_(mock.sentinel.resized_image))
        numpy.testing.assert_array_equal(resize_mock.call_args[0][0], rgb_array)
        assert_that(resize_mock.call_args[0][1], is_((2, 1)))
