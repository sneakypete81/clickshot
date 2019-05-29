from hamcrest import assert_that, is_

from clickshot import Config


class TestConfig:
    def test_config_defaults_are_correct(self):
        config = Config(image_dir="/images/", screenshot_dir="/screenshots/")

        assert_that(config.image_dir, is_("/images/"))
        assert_that(config.screenshot_dir, is_("/screenshots/"))
        assert_that(config.click_retry_seconds, is_(30))
        assert_that(config.screenshot_scaling, is_(1))
        assert_that(config.warn_for_delayed_detections, is_(False))

    def test_config_can_be_loaded_from_dict(self):
        config_dict = {
            "image_dir": "/img/",
            "screenshot_dir": "/scr/",
            "click_retry_seconds": 10,
            "screenshot_scaling": 2,
            "warn_for_delayed_detections": True,
        }

        config = Config(**config_dict)

        assert_that(config.image_dir, is_("/img/"))
        assert_that(config.screenshot_dir, is_("/scr/"))
        assert_that(config.click_retry_seconds, is_(10))
        assert_that(config.screenshot_scaling, is_(2))
        assert_that(config.warn_for_delayed_detections, is_(True))
