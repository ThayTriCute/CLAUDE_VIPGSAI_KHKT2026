# -*- coding: utf-8 -*-
from pathlib import Path
APP = Path(__file__).resolve().parents[1] / "app.py"
data = APP.read_bytes()
lf0 = data.count(b"\n") - data.count(b"\r\n")
old = b"(curriculum_policy, 2026110920)"
new = b"(curriculum_policy, 2026111220)"
if old not in data:
    raise SystemExit("revision marker not found")
data2 = data.replace(old, new, 1)
lf1 = data2.count(b"\n") - data2.count(b"\r\n")
if lf1 != lf0:
    raise SystemExit(f"LF drift {lf0}->{lf1}")
APP.write_bytes(data2)
print("APP_REVISION_OK", lf1)
