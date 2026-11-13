# -*- coding: utf-8 -*-
"""UI theo trạm — tách dần khỏi app.py monolith.

Hiện tại: điều hướng/auth nằm ở `services/station_nav.py` + `services/station_auth.py`.
Các khối Trạm 1–5 vẫn render trong `app.py`; bước tiếp theo chuyển từng `render_tramN(...)`.
"""
