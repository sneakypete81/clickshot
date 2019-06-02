from typing import NamedTuple


class Config(NamedTuple):
    image_dir: str = None
    screenshot_dir: str = None

    # Default time to wait for a clickable element to appear
    click_retry_seconds: int = 30

    # In some scenarios, Screenshots are taken with a zoom factor,
    # perhaps due to HiDPI.
    screenshot_scaling: int = 1

    # When enabled, a warning will be emitted if an element is not detected
    # on the first attempt. This can be useful for optimising post-click
    # delays.
    warn_for_delayed_detections: bool = False
