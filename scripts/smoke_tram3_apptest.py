# -*- coding: utf-8 -*-
"""Smoke Trạm 3 after UX patch (no secrets printed)."""
from streamlit.testing.v1 import AppTest

from pathlib import Path
APP = Path(__file__).resolve().parents[1] / "app.py"
at = AppTest.from_file(str(APP), default_timeout=45)
at.run(timeout=90)
print("RUN_OK")
print("exceptions", len(at.exception))
for x in list(at.exception)[:3]:
    print("EX", str(x)[:200])

for box in at.text_input:
    label = str(getattr(box, "label", "") or "")
    if "Họ và tên" in label:
        box.set_value("Minh Test T3").run(timeout=60)
        print("SET_NAME")
        break

switched = False
for r in at.radio:
    opts = list(getattr(r, "options", []) or [])
    if any("Trạm 3" in str(o) for o in opts):
        for o in opts:
            if "Trạm 3" in str(o):
                r.set_value(o).run(timeout=90)
                print("SWITCHED", str(o)[:80])
                switched = True
                break
    if switched:
        break
print("SWITCHED_OK", switched)

markers = []
for m in list(at.markdown) + list(at.caption) + list(at.subheader):
    val = str(getattr(m, "value", "") or "")
    if any(k in val for k in ["Trạm 3", "Khảo Thí", "Làm bài kín", "Mã đề", "PHÒNG THI", "Giáo viên", "In đề trắng"]):
        markers.append(val.replace("\n", " ")[:140])
print("MARKERS", len(markers))
for t in markers[:20]:
    print(" -", t)

for cb in at.checkbox:
    lab = str(getattr(cb, "label", "") or "")
    if "Làm bài kín" in lab:
        print("SEALED_CB", lab[:100])
        cb.check().run(timeout=60)
        print("SEALED_ON")

for box in at.text_input:
    lab = str(getattr(box, "label", "") or "")
    if "Mã đề" in lab or "truy cập" in lab:
        print("ACCESS", lab[:100])
        box.set_value("1011").run(timeout=60)
        print("ACCESS_SET")

for r in at.radio:
    opts = list(getattr(r, "options", []) or [])
    if any("Nguyên Đề" in str(o) or "Luyện Tập Chuyên Đề" in str(o) for o in opts):
        print("EXAM_MODES", [str(o)[:55] for o in opts])
        for o in opts:
            if "Nguyên Đề" in str(o):
                r.set_value(o).run(timeout=90)
                print("MODE_REAL")
                break

clicked = False
for b in at.button:
    lab = str(getattr(b, "label", "") or "")
    if "Bốc Ngẫu Nhiên" in lab or "Nạp Đề Đang Chọn" in lab:
        print("BTN", lab[:90])
        try:
            b.click().run(timeout=120)
            print("LOADED")
            clicked = True
            break
        except Exception as e:
            print("LOAD_FAIL", type(e).__name__, str(e)[:160])

print("exam_state", at.session_state.get("exam_state"))
print("has_exam", bool(at.session_state.get("exam_data")))
print("sealed", at.session_state.get("tram3_sealed_mode"))

after = []
for m in list(at.markdown) + list(at.caption) + list(at.warning) + list(at.info) + list(at.success):
    val = str(getattr(m, "value", "") or "")
    if any(k in val for k in ["Phiếu trả lời", "PHÒNG LUYỆN", "ĐANG LÀM BÀI", "Làm bài kín", "Nộp bài", "In đề trắng"]):
        after.append(val.replace("\n", " ")[:160])
print("AFTER", len(after))
for t in after[:20]:
    print(" *", t)
print("DONE")
