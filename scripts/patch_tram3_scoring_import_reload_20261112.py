# -*- coding: utf-8 -*-
"""Fix Streamlit stale-module: reload scoring_service; stub không raise nữa."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
SCORING = ROOT / "services" / "scoring_service.py"

OLD_IMPORT = """try:
    from services.scoring_service import calculate_part2_statement_score, grade_part1, grade_part2, grade_part3, grade_exam_by_profile
except Exception as _e_sc:
    logging.warning("Không thể nạp services.scoring_service: %s", _e_sc)
    def calculate_part2_statement_score(c):
        return {1: 0.1, 2: 0.25, 3: 0.5, 4: 1.0}.get(c, 0.0)
    def grade_exam_by_profile(exam, user_answers, subject, grade):
        raise RuntimeError("scoring_service chưa sẵn sàng để chấm điểm Trạm 3.")"""

NEW_IMPORT = """try:
    from importlib import reload as _reload_scoring
    import qa_runtime as _qa_runtime_for_scoring
    _reload_scoring(_qa_runtime_for_scoring)
    import services.scoring_service as _scoring_service_mod
    if getattr(_scoring_service_mod, "T3_SCORING_REVISION", None) != 2026111219:
        _reload_scoring(_scoring_service_mod)
    from services.scoring_service import calculate_part2_statement_score, grade_part1, grade_part2, grade_part3, grade_exam_by_profile
    if not callable(grade_exam_by_profile):
        raise RuntimeError("grade_exam_by_profile không callable sau reload")
except Exception as _e_sc:
    logging.warning("Không thể nạp services.scoring_service: %s", _e_sc)
    def calculate_part2_statement_score(c):
        return {1: 0.1, 2: 0.25, 3: 0.5, 4: 1.0}.get(c, 0.0)
    def grade_exam_by_profile(exam, user_answers, subject, grade):
        # Stub an toàn: ép reload lần nữa rồi chấm — không raise làm gãy phòng thi
        from importlib import reload as _reload_fb
        import qa_runtime as _qa_fb
        _reload_fb(_qa_fb)
        import services.scoring_service as _sc_fb
        _reload_fb(_sc_fb)
        return _sc_fb.grade_exam_by_profile(exam, user_answers, subject, grade)"""


def crlf(text: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


def patch_scoring_revision():
    text = SCORING.read_text(encoding="utf-8")
    marker = "T3_SCORING_REVISION = 2026111219"
    if marker in text:
        print("scoring revision already present")
        return
    needle = "from __future__ import annotations\n"
    if needle not in text:
        raise SystemExit("scoring_service future import missing")
    text = text.replace(
        needle,
        needle + "\nT3_SCORING_REVISION = 2026111219  # reload contract cho worker Streamlit\n",
        1,
    )
    SCORING.write_text(text, encoding="utf-8")
    print("scoring revision added")


def patch_app():
    data = APP.read_bytes()
    lf0 = data.count(b"\n") - data.count(b"\r\n")
    old = crlf(OLD_IMPORT)
    new = crlf(NEW_IMPORT)
    if old not in data:
        # try LF form (top region sometimes LF)
        old_lf = OLD_IMPORT.replace("\r\n", "\n").encode("utf-8")
        new_lf = NEW_IMPORT.replace("\r\n", "\n").encode("utf-8")
        if old_lf in data:
            data2 = data.replace(old_lf, new_lf, 1)
        else:
            raise SystemExit("import block not found")
    else:
        data2 = data.replace(old, new, 1)
    lf1 = data2.count(b"\n") - data2.count(b"\r\n")
    if lf1 != lf0:
        raise SystemExit(f"LF drift {lf0}->{lf1}")
    bad = 'raise RuntimeError("scoring_service chưa sẵn sàng'.encode("utf-8")
    if bad in data2:
        raise SystemExit("raising stub still present")
    APP.write_bytes(data2)
    print("app import patched", "lf_only", lf1)


def main():
    patch_scoring_revision()
    patch_app()
    print("PATCH_OK")


if __name__ == "__main__":
    main()
