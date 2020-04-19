from hamcrest import assert_that, is_
from pathlib import Path
import pytest

from clickshot.image import Image


@pytest.fixture
def empty_image():
    class EmptyImageData:
        shape = [0, 0]

    return Image(EmptyImageData())


class TestLoad:
    def test_checks_if_image_exists(self, mocker, empty_image):
        mocker.patch("clickshot.image.Path.exists").return_value = False

        with pytest.raises(FileNotFoundError):
            Image.load("invalid/path.png")


class TestSave:
    def test_image_dir_is_created_if_necessary(self, mocker, empty_image):
        mocker.patch("clickshot.image.cv2")
        mocker.patch("clickshot.image.Path.exists").return_value = False
        mkdir = mocker.patch("clickshot.image.Path.mkdir", autospec=True)

        empty_image.save("/dir/image_name.png")

        mkdir.assert_called_with(Path("/dir"), exist_ok=True)

    def test_image_path_is_returned(self, mocker, empty_image):
        mocker.patch("clickshot.image.cv2")
        mocker.patch("clickshot.image.Path.exists").return_value = False
        mocker.patch("clickshot.image.Path.mkdir")

        path = empty_image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name.png")))

    def test_image_is_saved(self, mocker, empty_image):
        cv2 = mocker.patch("clickshot.image.cv2")
        mocker.patch("clickshot.image.Path.exists").return_value = False
        mocker.patch("clickshot.image.Path.mkdir")

        empty_image.save("/dir/image_name.png")

        cv2.imwrite.assert_called_with("/dir/image_name.png", empty_image.data)

    def test_unique_name_with_existing_screenshot(self, mocker, empty_image):
        cv2 = mocker.patch("clickshot.image.cv2")
        mocker.patch("clickshot.image.Path.exists").side_effect = [True, False]
        mocker.patch("clickshot.image.Path.mkdir")

        path = empty_image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name_2.png")))
        cv2.imwrite.assert_called_with("/dir/image_name_2.png", mocker.ANY)

    def test_unique_name_with_two_existing_screenshots(self, mocker, empty_image):
        cv2 = mocker.patch("clickshot.image.cv2")
        mocker.patch("clickshot.image.Path.exists").side_effect = [True, True, False]
        mocker.patch("clickshot.image.Path.mkdir")

        path = empty_image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name_3.png")))
        cv2.imwrite.assert_called_with("/dir/image_name_3.png", mocker.ANY)
