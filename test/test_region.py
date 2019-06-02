import pytest
from unittest import mock
from hamcrest import assert_that, is_

from clickshot import Config, Region, ElementConfig


@pytest.fixture
def default_config():
    return Config(image_dir="", screenshot_dir=None)


class TestRegion:
    def test_a_region_can_be_created_with_one_element(self, default_config):
        element = mock.create_autospec(ElementConfig, spec_set=True)
        element.name = "test"

        region = Region(
            "screen",
            config=default_config,
            element_configs=[element],
            boundary=(0, 10, 32, 64),
        )

        assert_that(region._name, is_("screen"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region._boundary, is_((0, 10, 32, 64)))

    def test_a_region_can_be_created_with_two_elements(self, default_config):
        element = mock.create_autospec(ElementConfig, spec_set=True)
        element.name = "test"
        element2 = mock.create_autospec(ElementConfig, spec_set=True)
        element2.name = "test2"

        region = Region(
            "area", config=default_config, element_configs=[element, element2]
        )

        assert_that(region._name, is_("area"))
        assert_that(region._config, is_(default_config))
        assert_that(region.test.name, is_("test"))
        assert_that(region.test2.name, is_("test2"))
