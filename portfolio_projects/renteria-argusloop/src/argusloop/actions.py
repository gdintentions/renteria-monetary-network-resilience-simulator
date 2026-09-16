from __future__ import annotations

import time

from .models import Action
from .screen import normalized_to_screen


def execute(action: Action, logical_size: tuple[int, int], wait_seconds: float) -> str:
    import pyautogui

    pyautogui.FAILSAFE = True
    if action.action == "click":
        point = normalized_to_screen(action.x or 0, action.y or 0, logical_size)
        pyautogui.click(*point)
        return f"clicked {point}"
    if action.action == "type":
        pyautogui.write(action.text or "", interval=0.02)
        return f"typed {len(action.text or '')} characters"
    if action.action == "scroll":
        pyautogui.scroll(-500 if action.direction == "down" else 500)
        return f"scrolled {action.direction}"
    if action.action == "press_key":
        pyautogui.press(action.key or "")
        return f"pressed {action.key}"
    if action.action == "wait":
        time.sleep(wait_seconds)
        return f"waited {wait_seconds}s"
    return "done"
