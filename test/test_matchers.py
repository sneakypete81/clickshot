import pytest
from unittest import mock
from hamcrest import assert_that, is_, is_not, calling, raises

from clickshot.element import Element
from clickshot.matchers import visible, eventually_visible


class TestVisible:
    def test_assertion_passes_when_element_is_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = True

        assert_that(element, is_(visible()))

        element.is_visible.assert_called_with(timeout_seconds=0)

    def test_negative_assertion_passes_when_element_is_not_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = False

        assert_that(element, is_not(visible()))

        element.is_visible.assert_called_with(timeout_seconds=0)

    def test_assertion_fails_when_element_is_not_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = False

        assert_that(
            calling(assert_that).with_args(element, is_(visible())),
            raises(
                AssertionError, r"\s+Expected: to be visible\s+but: it was not found\s+"
            ),
        )

        element.is_visible.assert_called_with(timeout_seconds=0)

    def test_negative_assertion_fails_when_element_is_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = True

        assert_that(
            calling(assert_that).with_args(element, is_not(visible())),
            raises(
                AssertionError,
                r"\s+Expected: not to be visible\s+but: was <.*Element.*>\s+",
            ),
        )

        element.is_visible.assert_called_with(timeout_seconds=0)


class TestEventuallyVisible:
    def test_assertion_passes_when_element_is_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = True

        assert_that(element, is_(eventually_visible()))

        element.is_visible.assert_called_with(timeout_seconds=30)

    @pytest.mark.skip("negative eventually assertion doesn't wait")
    def test_negative_assertion_passes_when_element_is_not_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = False

        assert_that(element, is_not(eventually_visible()))

        element.is_visible.assert_called_with(timeout_seconds=30)

    def test_assertion_fails_when_element_is_not_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = False

        assert_that(
            calling(assert_that).with_args(element, is_(eventually_visible())),
            raises(
                AssertionError, r"\s+Expected: to be visible\s+but: it was not found\s+"
            ),
        )

        element.is_visible.assert_called_with(timeout_seconds=30)

    @pytest.mark.skip("negative eventually assertion doesn't wait")
    def test_negative_assertion_fails_when_element_is_visible(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = True

        assert_that(
            calling(assert_that).with_args(element, is_not(eventually_visible())),
            raises(
                AssertionError,
                r"\s+Expected: not to be visible\s+but: was <.*Element.*>\s+",
            ),
        )

        element.is_visible.assert_called_with(timeout_seconds=0)

    def test_custom_timeout_is_passed_through(self):
        element = mock.create_autospec(Element, spec_set=True)
        element.is_visible.return_value = True

        assert_that(element, is_(eventually_visible(within_seconds=66)))

        element.is_visible.assert_called_with(timeout_seconds=66)
