from hamcrest import assert_that, is_

from clickshot import Config


class TestConfig:
    def test_config_defaults_are_correct(self):
        config = Config(image_dir="/images/", screenshot_dir="/screenshots/")

        assert_that(config.image_dir, is_("/images/"))
        assert_that(config.screenshot_dir, is_("/screenshots/"))
        assert_that(config.timeout_seconds, is_(30))

    def test_config_can_be_loaded_from_dict(self):
        config_dict = {
            "image_dir": "/img/",
            "screenshot_dir": "/scr/",
            "timeout_seconds": 10,
        }

        config = Config(**config_dict)

        assert_that(config.image_dir, is_("/img/"))
        assert_that(config.screenshot_dir, is_("/scr/"))
        assert_that(config.timeout_seconds, is_(10))
