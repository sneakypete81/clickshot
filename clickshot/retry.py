import time
from typing import Any, Callable
import warnings


def retry_with_timeout(method: Callable, timeout_seconds: int) -> Any:
    emitted_warning = False
    start_time = time.monotonic()
    while True:
        try:
            return method()

        except RetryAbort as e:
            raise e.exception

        except Exception as e:
            if time.monotonic() - start_time > timeout_seconds:
                raise

            if not emitted_warning and isinstance(e, FileNotFoundError):
                warnings.warn(str(e))
                emitted_warning = True


class RetryAbort(Exception):
    def __init__(self, exception: Exception):
        super().__init__("Aborting the retry loop")
        self.exception = exception
