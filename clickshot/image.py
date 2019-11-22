from pathlib import Path
import cv2

from .exceptions import ElementNotFoundError


class Image:
    def __init__(self, data=None):
        self.data = data
        try:
            self.height = data.shape[0]
            self.width = data.shape[1]
        except AttributeError:
            self.height = None
            self.width = None

    @classmethod
    def load(cls, path):
        return cls(cv2.imread(str(path)))

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(exist_ok=True)

        unique_path = self._find_unique_path(path)
        cv2.imwrite(str(unique_path), self.data)

        return unique_path

    def match_template(self, template, threshold=0.001):
        result = cv2.matchTemplate(self.data, template.data, cv2.TM_SQDIFF_NORMED)
        minVal, _, minLoc, _ = cv2.minMaxLoc(result)

        if minVal > threshold:
            raise ElementNotFoundError
        return (
            minLoc[0],
            minLoc[1],
            template.width,
            template.height,
        )

    @staticmethod
    def _find_unique_path(path):
        if not path.exists():
            return path

        prefix = path.with_suffix("")
        suffix = path.suffix
        count = 2
        while True:
            unique_prefix = prefix.with_name(prefix.name + f"_{count}")
            unique_path = unique_prefix.with_suffix(suffix)
            if not unique_path.exists():
                return unique_path
            count += 1
