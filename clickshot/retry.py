import time
from typing import Any, Callable
import warnings


def retry_with_timeout(
    method: Callable, timeout_seconds: int, log: bool = False
) -> Any:
    emitted_warning = False
    start_time = time.monotonic()
    logger = RetryLogger()

    while True:
        now = time.monotonic()
        if log:
            logger.update(now - start_time)

        try:
            return method()

        except RetryAbort as e:
            if log:
                print("\n")
            raise e.exception

        except Exception as e:
            if now - start_time >= timeout_seconds:
                if log:
                    print("\n")
                raise

            if not emitted_warning and isinstance(e, FileNotFoundError):
                warnings.warn(str(e))
                emitted_warning = True


class RetryLogger:
    def __init__(self) -> None:
        self.count = 0
        self.last_length = 0

    def update(self, elapsed_time: float) -> None:
        while elapsed_time > self.count:
            message = f"{self.count}..."
            print("\b" * self.last_length, end="")
            print(message, end="", flush=True)
            self.count += 1
            self.last_length = len(message)


class RetryAbort(Exception):
    def __init__(self, exception: Exception) -> None:
        super().__init__("Aborting the retry loop")
        self.exception = exception
