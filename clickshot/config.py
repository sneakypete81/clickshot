from typing import NamedTuple


class Config(NamedTuple):
    image_dir: str = None
    screenshot_dir: str = None

    # Default time to wait for a clickable element to appear
    click_retry_seconds: int = 30
