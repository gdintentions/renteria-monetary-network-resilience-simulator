from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO

from PIL import Image


@dataclass(frozen=True)
class Observation:
    image: Image.Image
    sha256: str
    logical_size: tuple[int, int]


def capture_screen(target_width: int = 1280) -> Observation:
    import pyautogui

    pyautogui.FAILSAFE = True
    image = pyautogui.screenshot()
    logical_size = pyautogui.size()
    if image.width > target_width:
        ratio = target_width / image.width
        image = image.resize((target_width, round(image.height * ratio)), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return Observation(image, hashlib.sha256(buffer.getvalue()).hexdigest(), tuple(logical_size))


def normalized_to_screen(x: int, y: int, size: tuple[int, int]) -> tuple[int, int]:
    """Map Gemini's inclusive normalized grid to valid zero-based screen pixels."""
    width, height = size
    return min(width - 1, round(x * (width - 1) / 1000)), min(
        height - 1, round(y * (height - 1) / 1000)
    )
