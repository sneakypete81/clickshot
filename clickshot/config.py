from typing import NamedTuple


class Config(NamedTuple):
    image_dir: str = ""
    screenshot_dir: str = ""

    # Stop and ask questions - useful for debugging and initial setup
    interactive: bool = False

    # Default time to wait for an element to become visible
    timeout_seconds: int = 30
