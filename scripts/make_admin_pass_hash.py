# -*- coding: utf-8 -*-
"""Tạo dòng ADMIN_PASS = \"sha256:<hash>\" cho .streamlit/secrets.toml (local)."""
import hashlib
import sys


def main():
    raw = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not raw:
        try:
            raw = input("Nhập mật khẩu quản trị Trạm 4: ").strip()
        except EOFError:
            raw = ""
    if not raw:
        print("Cần một mật khẩu không rỗng.")
        raise SystemExit(1)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    print("Chép đúng 1 dòng sau vào file .streamlit/secrets.toml:")
    print('ADMIN_PASS = "sha256:%s"' % digest)
    print("")
    print("Rồi lưu file và restart Streamlit (Ctrl+C rồi: streamlit run app.py).")
    print("Mật khẩu gõ trên ô Trạm 4 là mật khẩu gốc vừa nhập — không gõ chuỗi sha256.")


if __name__ == "__main__":
    main()
