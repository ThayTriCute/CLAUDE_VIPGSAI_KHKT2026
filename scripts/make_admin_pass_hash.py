# -*- coding: utf-8 -*-
"""In dòng ADMIN_PASS=sha256:... để dán vào .streamlit/secrets.toml.

Usage:
  python scripts/make_admin_pass_hash.py "mat-khau-cua-anh"
  python scripts/make_admin_pass_hash.py --write "mat-khau-cua-anh"
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SECRETS = ROOT / ".streamlit" / "secrets.toml"


def make_line(plain: str) -> str:
    digest = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    return f'ADMIN_PASS = "sha256:{digest}"'


def write_secrets(plain: str) -> None:
    SECRETS.parent.mkdir(parents=True, exist_ok=True)
    line = make_line(plain)
    if SECRETS.exists():
        text = SECRETS.read_text(encoding="utf-8")
        if re.search(r"^ADMIN_PASS\s*=", text, re.M):
            text = re.sub(r"^ADMIN_PASS\s*=.*$", line, text, count=1, flags=re.M)
        else:
            text = text.rstrip() + "\n" + line + "\n"
    else:
        text = line + "\n"
    SECRETS.write_text(text, encoding="utf-8")
    print(f"Wrote hashed ADMIN_PASS to {SECRETS} (value not echoed).")


def main() -> int:
    p = argparse.ArgumentParser(description="Hash ADMIN_PASS for Streamlit secrets.")
    p.add_argument("password", help="Plain teacher password (will be hashed; not stored plain).")
    p.add_argument(
        "--write",
        action="store_true",
        help=f"Update {SECRETS} in place instead of only printing the line.",
    )
    args = p.parse_args()
    plain = str(args.password or "")
    if not plain.strip():
        print("Password must not be empty.", file=sys.stderr)
        return 2
    line = make_line(plain)
    if args.write:
        write_secrets(plain)
    else:
        print(line)
        print("# Paste into .streamlit/secrets.toml then restart Streamlit.")
    # Verify round-trip without printing secrets
    from qa_runtime import admin_password_matches

    configured = line.split("=", 1)[1].strip().strip('"')
    ok = bool(admin_password_matches(plain, configured))
    print(f"VERIFY_MATCH={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
