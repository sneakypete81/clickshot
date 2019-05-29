from pathlib import Path


def save_screenshot(screenshot, screenshot_dir, screenshot_name):
    screenshot_dir = Path(screenshot_dir)
    screenshot_dir.mkdir(exist_ok=True)

    screenshot_path = _find_unique_screenshot_path(screenshot_dir, screenshot_name)
    screenshot.save(screenshot_path)

    return screenshot_path


def _find_unique_screenshot_path(screenshot_dir, screenshot_name):
    prefix = screenshot_dir / screenshot_name
    screenshot_path = prefix.with_suffix(".png")
    if not screenshot_path.exists():
        return screenshot_path

    count = 2
    while True:
        unique_prefix = prefix.with_name(prefix.name + f"_{count}")
        screenshot_path = unique_prefix.with_suffix(".png")
        if not screenshot_path.exists():
            return screenshot_path
        count += 1
