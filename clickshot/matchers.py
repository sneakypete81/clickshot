from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.base_description import BaseDescription

from .element import Element

EVENTUAL_TIMEOUT_SECONDS = 30


class _Visible(BaseMatcher):
    def __init__(self, timeout_seconds: int = 0):
        self.timeout_seconds = timeout_seconds

    def _matches(self, element: Element) -> bool:
        try:
            return element.is_visible(timeout_seconds=self.timeout_seconds)
        except FileNotFoundError:
            element.save_last_screenshot()
            raise

    def describe_to(self, description: BaseDescription) -> None:
        description.append_text("to be visible")

    def describe_mismatch(
        self, element: Element, mismatch_description: BaseDescription
    ) -> None:
        mismatch_description.append_text("it was not found")
        element.save_last_screenshot()


def visible() -> BaseMatcher:
    return _Visible()


def eventually_visible(within_seconds: int = EVENTUAL_TIMEOUT_SECONDS) -> BaseMatcher:
    return _Visible(within_seconds)
