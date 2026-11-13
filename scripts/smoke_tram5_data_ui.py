# -*- coding: utf-8 -*-
"""Smoke Trạm 5 (dữ liệu) sau mở khóa — dùng ADMIN_PASS từ secrets.toml."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest


def _plain_from_secrets() -> str:
    """If ADMIN_PASS is plaintext return it; if sha256, return None (caller uses known test plain)."""
    path = ROOT / ".streamlit" / "secrets.toml"
    raw = path.read_text(encoding="utf-8") if path.exists() else ""
    m = re.search(r'^ADMIN_PASS\s*=\s*(".*?"|\'.*?\'|\S+)', raw, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v


def main() -> int:
    evidence = ROOT / "qa_evidence"
    evidence.mkdir(exist_ok=True)
    report: dict = {"ok": False, "checks": {}}

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    import os
    # CI: plaintext cố định. Local: ưu tiên hash trong secrets.toml nếu có.
    if os.environ.get("GITHUB_ACTIONS") or os.environ.get("CI"):
        candidate = "qa-ci-tram5-pass"
        at.secrets["ADMIN_PASS"] = candidate
    else:
        configured = _plain_from_secrets()
        candidate = "KHKT@2026"
        if configured.startswith("sha256:"):
            at.secrets["ADMIN_PASS"] = configured
        elif configured:
            at.secrets["ADMIN_PASS"] = configured
            candidate = configured
        else:
            at.secrets["ADMIN_PASS"] = candidate

    at.run()
    report["checks"]["boot_exc"] = [e.message for e in at.exception][:3]
    assert not list(at.exception), report["checks"]["boot_exc"]

    # Select Trạm 5
    picked = False
    for r in at.radio:
        for o in list(r.options or []):
            if "Trạm 5" in str(o) or "Dữ liệu" in str(o):
                r.set_value(o)
                at.run()
                picked = True
                break
        if picked:
            break
    report["checks"]["station_picked"] = picked

    labels = [getattr(t, "label", "") for t in at.text_input]
    locked = "Mật khẩu giáo viên:" in labels
    report["checks"]["initially_locked"] = locked

    if locked:
        next(t for t in at.text_input if t.label == "Mật khẩu giáo viên:").set_value(candidate)
        unlock = [
            b
            for b in at.button
            if "Mở khóa Trạm 5" in (b.label or "") or (b.label or "").strip() == "🔓 Mở khóa"
        ]
        assert unlock, "missing unlock button"
        unlock[0].click().run()

    auth = bool(at.session_state.get("teacher_authenticated") or at.session_state.get("tab4_authenticated"))
    report["checks"]["authenticated"] = auth
    assert auth, "Trạm 5 unlock failed"

    pwd_after = [t for t in at.text_input if "Mật khẩu giáo viên:" in (t.label or "")]
    report["checks"]["password_field_gone"] = len(pwd_after) == 0

    lock_btns = [b for b in at.button if "Khóa Trạm 5" in (b.label or "")]
    report["checks"]["has_lock_btn"] = len(lock_btns) >= 1

    texts = " ".join(
        str(getattr(x, "value", x))
        for x in list(at.markdown) + list(at.caption) + list(at.info) + list(at.subheader)
    )
    report["checks"]["has_health"] = "Sức khỏe hệ thống" in texts or any(
        "Sức khỏe hệ thống" in str(getattr(e, "label", "")) for e in at.expander
    )
    report["checks"]["has_logs_section"] = "Nhật ký" in texts
    report["checks"]["has_research_export"] = "nghiên cứu" in texts.lower() or "ẩn danh" in texts.lower()
    report["checks"]["has_who5_block"] = "WHO-5" in texts or "Trạm 4" in texts or "ngữ liệu" in texts.lower()

    # Expanders present
    exp_labels = [str(getattr(e, "label", "")) for e in at.expander]
    report["checks"]["expanders"] = exp_labels[:12]

    # Download buttons (may be empty if no logs)
    dl = [str(getattr(d, "label", "")) for d in at.download_button]
    report["checks"]["download_buttons"] = dl[:10]

    # Soft seed: ensure page still stable after auth
    report["checks"]["post_auth_exc"] = [e.message for e in at.exception][:3]
    assert not list(at.exception)

    # Lock again
    if lock_btns:
        lock_btns[0].click().run()
        re_locked = "Mật khẩu giáo viên:" in [getattr(t, "label", "") for t in at.text_input]
        report["checks"]["re_lock_ok"] = re_locked
    else:
        report["checks"]["re_lock_ok"] = False

    report["ok"] = all(
        [
            report["checks"]["authenticated"],
            report["checks"]["password_field_gone"],
            report["checks"]["has_lock_btn"],
            report["checks"].get("re_lock_ok", False),
        ]
    )
    out = evidence / "tram5_data_smoke.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("SMOKE_TRAM5_DATA", "OK" if report["ok"] else "FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
