from hamcrest.core.base_matcher import BaseMatcher

EVENTUAL_TIMEOUT_SECONDS = 30


class _Visible(BaseMatcher):
    def __init__(self, timeout_seconds=0):
        self.timeout_seconds = timeout_seconds

    def _matches(self, element):
        try:
            return element.is_visible(timeout_seconds=self.timeout_seconds)
        except FileNotFoundError:
            element.save_last_screenshot()
            raise

    def describe_to(self, description):
        description.append_text("to be visible")

    def describe_mismatch(self, element, mismatch_description):
        mismatch_description.append_text("it was not found")
        element.save_last_screenshot()


def visible():
    return _Visible()


def eventually_visible(within_seconds=EVENTUAL_TIMEOUT_SECONDS):
    return _Visible(within_seconds)
