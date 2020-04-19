import time
from typing import Any, Callable


def retry_with_timeout(method: Callable, timeout_seconds: int) -> Any:
    start_time = time.monotonic()
    while True:
        try:
            return method()
        except RetryAbort as e:
            raise e.exception
        except Exception:
            if time.monotonic() - start_time > timeout_seconds:
                raise


class RetryAbort(Exception):
    def __init__(self, exception: Exception):
        super().__init__("Aborting the retry loop")
        self.exception = exception
