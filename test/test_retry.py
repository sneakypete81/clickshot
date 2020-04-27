from hamcrest import assert_that, is_
import pytest

from clickshot.retry import retry_with_timeout, RetryAbort


class NormalTestError(Exception):
    pass


class AbortedTestError(Exception):
    pass


class Timer:
    def __init__(self):
        self.time = 0

    def increment(self):
        self.time += 0.1
        return self.time


@pytest.fixture
def time_mock(mocker):
    timer = Timer()
    mock = mocker.patch("clickshot.retry.time")
    mock.monotonic.side_effect = timer.increment
    return timer


class TestRetry:
    def test_returns_if_no_exception(self, mocker):
        method = mocker.Mock(return_value=42)

        result = retry_with_timeout(method, 30)

        assert_that(result, is_(42))

    def test_raises_if_exception_after_timeout(self, mocker, time_mock):
        method = mocker.Mock(side_effect=NormalTestError)

        with pytest.raises(NormalTestError):
            retry_with_timeout(method, 30)

    def test_raises_immediately_if_exception_and_no_timeout_set(
        self, mocker, time_mock
    ):
        method = mocker.Mock(side_effect=NormalTestError)

        with pytest.raises(NormalTestError):
            retry_with_timeout(method, 0)

        method.assert_called_once()

    def test_returns_if_no_exception_just_before_timeout(self, mocker, time_mock):
        def side_effect():
            if time_mock.time < 30:
                raise NormalTestError
            return 42

        method = mocker.Mock(side_effect=side_effect)

        result = retry_with_timeout(method, 30)

        assert_that(result, is_(42))

    def test_raises_if_abort_is_raised(self, mocker, time_mock):
        def side_effect():
            if time_mock.time < 10:
                raise NormalTestError
            elif time_mock.time < 11:
                raise RetryAbort(AbortedTestError())
            return 42

        method = mocker.Mock(side_effect=side_effect)

        with pytest.raises(AbortedTestError):
            retry_with_timeout(method, 30)

    def test_emits_single_warning_if_file_not_found(self, mocker, time_mock):
        method = mocker.Mock(side_effect=FileNotFoundError("error message"))

        with pytest.raises(FileNotFoundError):
            with pytest.warns(UserWarning) as record:
                retry_with_timeout(method, 30)

        warning_messages = [r.message.args[0] for r in record]
        assert_that(warning_messages, is_(["error message"]))

    def test_logs_progress_if_logging_enabled(self, mocker, time_mock, capsys):
        def side_effect():
            if time_mock.time < 4:
                raise NormalTestError
            return 42

        method = mocker.Mock(side_effect=side_effect)

        retry_with_timeout(method, 30, log=True)

        assert_that(
            capsys.readouterr().out, is_("0...\b\b\b\b1...\b\b\b\b2...\b\b\b\b3...")
        )

    def test_does_not_log_progress_by_default(self, mocker, time_mock, capsys):
        def side_effect():
            if time_mock.time < 4:
                raise NormalTestError
            return 42

        method = mocker.Mock(side_effect=side_effect)

        retry_with_timeout(method, 30)

        assert_that(capsys.readouterr().out, is_(""))
