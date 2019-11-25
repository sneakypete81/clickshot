from pathlib import Path
from typing import Union

import cv2
import numpy

from .exceptions import ElementNotFoundError
from .types import Rect


class Image:
    def __init__(self, data: numpy.array) -> None:
        self.data = data
        self.height = data.shape[0]
        self.width = data.shape[1]

    @classmethod
    def load(cls, path: Union[Path, str]) -> "Image":
        return cls(cv2.imread(str(path)))

    def save(self, path: Union[Path, str]) -> Path:
        path = Path(path)
        path.parent.mkdir(exist_ok=True)

        unique_path = self._find_unique_path(path)
        cv2.imwrite(str(unique_path), self.data)

        return unique_path

    def match_template(self, template: "Image", threshold: float = 0.001) -> Rect:
        result = cv2.matchTemplate(self.data, template.data, cv2.TM_SQDIFF_NORMED)
        minVal, _, minLoc, _ = cv2.minMaxLoc(result)

        if minVal > threshold:
            raise ElementNotFoundError
        return Rect(
            left=minLoc[0], top=minLoc[1], width=template.width, height=template.height,
        )

    @staticmethod
    def _find_unique_path(path: Path) -> Path:
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
