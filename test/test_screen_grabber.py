from hamcrest import assert_that, is_
import numpy
import pytest

from clickshot import Rect
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


class TestGrab:
    def test_returns_rgb_image_from_mss(self, mocker, pixels, rgb_array):
        mss = mocker.patch("clickshot.screen_grabber.mss")
        mss().grab.return_value = pixels
        grabber = ScreenGrabber()

        image = grabber.grab(Rect(left=0, top=1, width=2, height=3))

        numpy.testing.assert_array_equal(image.data, rgb_array)

    def test_passes_rect_parameter_to_mss(self, mocker, pixels):
        mss = mocker.patch("clickshot.screen_grabber.mss")
        mss().grab.return_value = pixels

        grabber = ScreenGrabber()
        grabber.grab(Rect(left=0, top=1, width=2, height=3))

        mss().grab.assert_called_with({"left": 0, "top": 1, "width": 2, "height": 3})

    def test_defaults_to_all_monitors(self, mocker, pixels):
        mss = mocker.patch("clickshot.screen_grabber.mss")
        mss().grab.return_value = pixels
        mss().monitors = [{"left": 0, "top": 1, "width": 200, "height": 300}]

        grabber = ScreenGrabber()
        grabber.grab()

        mss().grab.assert_called_with(
            {"left": 0, "top": 1, "width": 200, "height": 300}
        )

    def test_resizes_from_hidpi_monitor(self, mocker, pixels, rgb_array):
        mss = mocker.patch("clickshot.screen_grabber.mss")
        mss().grab.return_value = pixels

        resized_image_data = numpy.array([[24]])
        resize = mocker.patch("clickshot.screen_grabber.cv2.resize")
        resize.return_value = resized_image_data

        # Ask for a smaller region than is returned by mss().grab.
        # This indicates a HiDPI monitor, which should then be resized back to the
        # requested region size.
        grabber = ScreenGrabber()
        image = grabber.grab(Rect(left=0, top=0, width=2, height=1))

        numpy.testing.assert_array_equal(image.data, resized_image_data)
        numpy.testing.assert_array_equal(resize.call_args[0][0], rgb_array)
        assert_that(resize.call_args[0][1], is_((2, 1)))
