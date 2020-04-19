from hamcrest import assert_that, is_, calling, raises

from clickshot.retry import retry_with_timeout, RetryAbort


class NormalTestError(Exception):
    pass


class AbortedTestError(Exception):
    pass


class TestRetry:
    def test_returns_if_no_exception(self, mocker):
        method = mocker.Mock(return_value=42)

        result = retry_with_timeout(method, 30)

        assert_that(result, is_(42))

    def test_raises_if_exception_after_timeout(self, mocker):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, NormalTestError),
            (11, NormalTestError),
            (21, NormalTestError),
            (29, NormalTestError),
            (31, NormalTestError),
            (41, NormalTestError),
            (51, NormalTestError),
        ]
        time.monotonic.side_effect = [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        assert_that(
            calling(retry_with_timeout).with_args(method, 30), raises(NormalTestError)
        )

    def test_returns_if_no_exception_just_before_timeout(self, mocker):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, NormalTestError),
            (11, NormalTestError),
            (21, NormalTestError),
            (29, 42),
            (31, 43),
            (41, 44),
            (51, 45),
        ]
        time.monotonic.side_effect = [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        result = retry_with_timeout(method, 30)

        assert_that(result, is_(42))

    def test_raises_if_abort_is_raised(self, mocker):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, NormalTestError),
            (11, NormalTestError),
            (21, RetryAbort(AbortedTestError())),
            (29, 42),
            (31, 43),
            (41, 44),
            (51, 45),
        ]
        time.monotonic.side_effect = [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        assert_that(
            calling(retry_with_timeout).with_args(method, 30), raises(AbortedTestError)
        )
