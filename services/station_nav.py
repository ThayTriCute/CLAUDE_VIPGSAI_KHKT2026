# -*- coding: utf-8 -*-
"""Nhãn & điều hướng 5 trạm UI (tách khỏi app.py)."""
from __future__ import annotations

from typing import Any, MutableMapping, Sequence

STATION_LABELS: list[str] = [
    "📖 Trạm 1: Học Tập & Phòng Lab",
    "✍️ Trạm 2: Gia Sư Socratic & Nộp Bài",
    "📝 Trạm 3: Luyện Tập & Khảo Thí",
    "💚 Trạm 4: Tư Vấn Tâm Lý Học Đường",
    "📊 Trạm 5: Dữ Liệu & Nghiên Cứu",
]

TRAM5_INDEX = 4


def ensure_station_selection(state: MutableMapping[str, Any], labels: Sequence[str] | None = None) -> str:
    labels = list(labels or STATION_LABELS)
    forced = state.pop("_force_selected_station", None)
    if forced in labels:
        state["selected_station"] = forced
        state["sb_station_radio_selector"] = forced
    if "selected_station" not in state or state["selected_station"] not in labels:
        state["selected_station"] = labels[0]
    if "sb_station_radio_selector" not in state:
        state["sb_station_radio_selector"] = state["selected_station"]
    elif state["sb_station_radio_selector"] != state["selected_station"]:
        state["sb_station_radio_selector"] = state["selected_station"]
    return str(state["selected_station"])


def navigate_to_station(state: MutableMapping[str, Any], label: str, labels: Sequence[str] | None = None) -> None:
    labels = list(labels or STATION_LABELS)
    if label in labels:
        state["selected_station"] = label
        state["sb_station_radio_selector"] = label


def force_tram5(state: MutableMapping[str, Any], labels: Sequence[str] | None = None) -> None:
    labels = list(labels or STATION_LABELS)
    label = labels[TRAM5_INDEX]
    state["selected_station"] = label
    state["_force_selected_station"] = label
