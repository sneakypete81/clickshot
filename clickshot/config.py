from typing import NamedTuple


class Config(NamedTuple):
    image_dir: str = ""
    screenshot_dir: str = ""

    # Default time to wait for an element to become visible
    timeout_seconds: int = 30
