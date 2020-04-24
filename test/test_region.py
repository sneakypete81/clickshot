import pytest
from hamcrest import assert_that, is_
from pathlib import Path

from clickshot import Config, Rect, Region, ElementConfig


@pytest.fixture
def default_config():
    return Config("img", "scr")


def mock_stack(mocker, path):
    stack_item = mocker.Mock(filename=str(path / "somefile.py"))
    return ["", stack_item]


class TestRegion:
    def test_a_region_can_be_created_with_one_element(self, default_config):
        element = ElementConfig("test")

        region = Region(
            "screen", default_config, boundary=Rect(left=0, top=10, width=32, height=8)
        )
        region.configure([element])

        assert_that(region._name, is_("screen"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region._boundary, is_(Rect(left=0, top=10, width=32, height=8)))

    def test_a_region_can_be_created_with_two_elements(self, default_config):
        element = ElementConfig("test")
        element2 = ElementConfig("test2")

        region = Region("area", default_config).configure([element, element2])

        assert_that(region._name, is_("area"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region.test2.name, is_("test2"))

    def test_a_region_is_automatically_created_when_accessed(self, default_config):
        region = Region(
            "screen", default_config, boundary=Rect(left=0, top=10, width=32, height=8)
        )

        assert_that(region.test.name, is_("test"))

    def test_the_default_config_paths_are_subdirectories_of_the_caller(self):
        region = Region("area", Config())
        this_dir = Path(__file__).parent

        assert_that(region._config.image_dir, is_(str(this_dir / "images")))
        assert_that(region._config.screenshot_dir, is_(str(this_dir / "screenshots")))

    def test_system_image_dir_is_used(self, mocker, tmp_path):
        (tmp_path / "images" / "Darwin").mkdir(parents=True)
        mocker.patch("clickshot.region.platform.system").return_value = "Darwin"
        mocker.patch("clickshot.region.inspect.stack").return_value = mock_stack(
            mocker, tmp_path
        )

        region = Region("area", Config())

        assert_that(region._config.image_dir, is_(str(tmp_path / "images" / "Darwin")))

    def test_release_image_dir_is_preferred(self, mocker, tmp_path):
        (tmp_path / "images" / "Darwin").mkdir(parents=True)
        (tmp_path / "images" / "Darwin-19.4.0").mkdir(parents=True)
        mocker.patch("clickshot.region.platform.system").return_value = "Darwin"
        mocker.patch("clickshot.region.platform.release").return_value = "19.4.0"
        mocker.patch("clickshot.region.inspect.stack").return_value = mock_stack(
            mocker, tmp_path
        )

        region = Region("area", Config())

        assert_that(
            region._config.image_dir, is_(str(tmp_path / "images" / "Darwin-19.4.0"))
        )

    def test_mac_ver_image_dir_is_preferred(self, mocker, tmp_path):
        (tmp_path / "images" / "Darwin").mkdir(parents=True)
        (tmp_path / "images" / "Darwin-19.4.0").mkdir(parents=True)
        (tmp_path / "images" / "Darwin-10.15.4").mkdir(parents=True)
        mocker.patch("clickshot.region.platform.system").return_value = "Darwin"
        mocker.patch("clickshot.region.platform.release").return_value = "19.4.0"
        mocker.patch("clickshot.region.platform.mac_ver").return_value = ("10.15.4",)
        mocker.patch("clickshot.region.inspect.stack").return_value = mock_stack(
            mocker, tmp_path
        )

        region = Region("area", Config())

        assert_that(
            region._config.image_dir, is_(str(tmp_path / "images" / "Darwin-10.15.4"))
        )
