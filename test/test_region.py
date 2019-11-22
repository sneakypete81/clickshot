import pytest
from unittest import mock
from hamcrest import assert_that, is_
from pathlib import Path

from clickshot import Config, Region, ElementConfig


@pytest.fixture
def default_config():
    return Config("img", "scr")


class TestRegion:
    def test_a_region_can_be_created_with_one_element(self, default_config):
        element = mock.create_autospec(ElementConfig, spec_set=True)
        element.name = "test"

        region = Region("screen", default_config, boundary=(0, 10, 32, 64))
        region.configure([element])

        assert_that(region._name, is_("screen"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region._boundary, is_((0, 10, 32, 64)))

    def test_a_region_can_be_created_with_two_elements(self, default_config):
        element = mock.create_autospec(ElementConfig, spec_set=True)
        element.name = "test"
        element2 = mock.create_autospec(ElementConfig, spec_set=True)
        element2.name = "test2"

        region = Region("area", default_config).configure([element, element2])

        assert_that(region._name, is_("area"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region.test2.name, is_("test2"))

    def test_a_region_is_automatically_created_when_accessed(self, default_config):
        region = Region("screen", default_config, boundary=(0, 10, 32, 64))

        assert_that(region.test.name, is_("test"))

    def test_the_default_config_paths_are_subdirectories_of_the_caller(self):
        region = Region("area", Config())
        this_dir = Path(__file__).parent

        assert_that(region._config.image_dir, is_(this_dir / "images"))
        assert_that(region._config.screenshot_dir, is_(this_dir / "screenshots"))
