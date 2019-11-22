from unittest import mock
from hamcrest import assert_that, is_
from pathlib import Path

from clickshot.image import Image


@mock.patch("clickshot.image.Path.exists", autospec=True, spec_set=True)
@mock.patch("clickshot.image.Path.mkdir", autospec=True, spec_set=True)
@mock.patch("clickshot.image.cv2", autospec=True, spec_set=True)
class TestSave:
    def test_image_dir_is_created_if_necessary(self, cv2, mkdir, exists):
        image = Image()
        exists.return_value = False

        image.save("/dir/image_name.png")

        mkdir.assert_called_with(Path("/dir"), exist_ok=True)

    def test_image_path_is_returned(self, cv2, mkdir, exists):
        image = Image()
        exists.return_value = False

        path = image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name.png")))

    def test_image_is_saved(self, cv2, mkdir, exists):
        image = Image(mock.sentinel.ImageData)
        exists.return_value = False

        image.save("/dir/image_name.png")

        cv2.imwrite.assert_called_with("/dir/image_name.png", mock.sentinel.ImageData)

    def test_unique_name_with_existing_screenshot(self, cv2, mkdir, exists):
        image = Image()
        exists.side_effect = [True, False]

        path = image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name_2.png")))
        cv2.imwrite.assert_called_with("/dir/image_name_2.png", mock.ANY)

    def test_unique_name_with_two_existing_screenshots(self, cv2, mkdir, exists):
        image = Image()
        exists.side_effect = [True, True, False]

        path = image.save("/dir/image_name.png")

        assert_that(path, is_(Path("/dir/image_name_3.png")))
        cv2.imwrite.assert_called_with("/dir/image_name_3.png", mock.ANY)
