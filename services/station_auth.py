# -*- coding: utf-8 -*-
"""Cờ xác thực giáo viên (Trạm 5) — một nguồn sự thật."""
from __future__ import annotations

from typing import Any, MutableMapping


def is_teacher_authenticated(state: MutableMapping[str, Any] | None = None) -> bool:
    """True nếu GV đã mở khóa Trạm 5. Đồng bộ alias legacy `tab4_authenticated`."""
    if state is None:
        return False
    authed = bool(state.get("teacher_authenticated") or state.get("tab4_authenticated", False))
    if authed:
        state["teacher_authenticated"] = True
        state["tab4_authenticated"] = True
    return authed


def set_teacher_authenticated(state: MutableMapping[str, Any], value: bool) -> None:
    state["teacher_authenticated"] = bool(value)
    state["tab4_authenticated"] = bool(value)  # legacy alias — giữ tương thích smoke/test cũ
