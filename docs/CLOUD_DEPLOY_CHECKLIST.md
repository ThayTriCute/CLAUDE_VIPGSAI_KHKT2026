# Checklist đồng bộ Streamlit Cloud (Trạm 1–5)

**App:** https://gsaithptth-khkt2026.streamlit.app  
**Repo:** https://github.com/ThayTriCute/CLAUDE_VIPGSAI_KHKT2026  
**Entry:** `app.py` (alias `Home.py` / `main.py` / `streamlit_app.py`)

## 1. Secrets (Cloud → Settings → Secrets)

Không commit plaintext. Khuyến nghị hash:

```toml
ADMIN_PASS = "sha256:6f06b66f2b9cfed2fed707e6735a821612a0b7e96c8446771ced71e7c0c09a9c"
```

Preimage local đã verify: `KHKT@2026`  
Tạo lại: `python scripts/make_admin_pass_hash.py "mat-khau"`

Tuỳ chọn: `GEMINI_API_KEY`, `GOOGLE_SHEET_URL`, webhook token…

## 2. Sau mỗi lần deploy / đổi Secrets

1. **Redeploy / Restart** app (Cloud tắt file watcher — không hot-reload).
2. Trạm 5: mở khóa bằng MK đúng → phải **ở lại Trạm 5** (banner xanh).
3. Trạm 4: chat tư vấn không đòi MK.
4. Trạm 1–3: smoke Soạn bài / Socratic / bốc đề nếu có Key.

## 3. File watcher

`.streamlit/config.toml` có `fileWatcherType = "none"` → mọi thay đổi code/Secrets cần **restart** mới có hiệu lực.

## 4. Không đẩy lên Git

- `.streamlit/secrets.toml`
- `data/*.db*`, `data/admin_guard_state.json`
- API keys / PII học sinh
