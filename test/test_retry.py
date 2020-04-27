from hamcrest import assert_that, is_
import pytest

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
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        with pytest.raises(NormalTestError):
            retry_with_timeout(method, 30)

    def test_raises_immediately_if_exception_and_no_timeout_set(self, mocker):
        time = mocker.patch("clickshot.retry.time")
        time.monotonic.return_value = 1000
        method = mocker.Mock(side_effect=NormalTestError)

        with pytest.raises(NormalTestError):
            retry_with_timeout(method, 0)

        method.assert_called_once()

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
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
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
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        with pytest.raises(AbortedTestError):
            retry_with_timeout(method, 30)

    def test_emits_single_warning_if_file_not_found(self, mocker):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, FileNotFoundError("error message")),
            (11, FileNotFoundError("error message")),
            (21, FileNotFoundError("error message")),
            (29, FileNotFoundError("error message")),
            (31, FileNotFoundError("error message")),
            (41, FileNotFoundError("error message")),
            (51, FileNotFoundError("error message")),
        ]
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        with pytest.raises(FileNotFoundError):
            with pytest.warns(UserWarning) as record:
                retry_with_timeout(method, 30)

        warning_messages = [r.message.args[0] for r in record]
        assert_that(warning_messages, is_(["error message"]))

    def test_logs_progress_if_logging_enabled(self, mocker, capsys):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, NormalTestError),
            (4, 40),
            (21, 41),
            (29, 42),
            (31, 43),
            (41, 44),
            (51, 45),
        ]
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        retry_with_timeout(method, 30, log=True)

        assert_that(
            capsys.readouterr().out, is_("0...\b\b\b\b1...\b\b\b\b2...\b\b\b\b3...")
        )

    def test_does_not_log_progress_by_default(self, mocker, capsys):
        time = mocker.patch("clickshot.retry.time")
        method_timing = [
            (0, NormalTestError),
            (4, 40),
            (21, 41),
            (29, 42),
            (31, 43),
            (41, 44),
            (51, 45),
        ]
        time.monotonic.side_effect = [0] + [s[0] for s in method_timing]
        method = mocker.Mock(side_effect=[s[1] for s in method_timing])

        retry_with_timeout(method, 30)

        assert_that(capsys.readouterr().out, is_(""))
