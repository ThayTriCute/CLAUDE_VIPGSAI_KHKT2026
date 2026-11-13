# -*- coding: utf-8 -*-
"""Trạm 4 (UI) — Tư vấn tâm lý học đường (độc lập).

Triết lý khóa cứng: Dưỡng thiện tâm – Ươm nhân tài.
Mọi AI tư vấn phải đi qua khóa TRAM5_COUNSELING_LOCK_V1 (tên marker giữ để tương thích);
không bịa điều/khoản; không chẩn đoán lâm sàng; ưu tiên an toàn khi khủng hoảng.
Neo pháp lý: VB mới nhất đang hiệu lực VÀ/HOẶC VB cũ còn hiệu lực (kênh khả tín).

UI: Trạm 4 = tâm lý HS; Trạm 5 = dữ liệu/nghiên cứu (MK GV).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

T1_CONTEXT_REVISION = 2026111225

VN_TZ = timezone(timedelta(hours=7))
_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = _ROOT / "data" / "counseling_legal_references.json"
OWNER_HANDBOOK_PATH = _ROOT / "docs" / "AI_TRAM5_COUNSELING_LOCK.txt"
OWNER_HANDBOOK_DOC = "docs/AI_TRAM5_COUNSELING_LOCK.md"

# --- Khóa cứng bắt buộc cho AI tư vấn (Trạm 4 trên UI) ---
# Tên TRAM5_* giữ tương thích lịch sử; alias COUNSELING_* là tên đúng theo UI.
TRAM5_LOCK_MARKER = "[TRAM5_COUNSELING_LOCK_V1]"
COUNSELING_LOCK_MARKER = TRAM5_LOCK_MARKER
TRAM5_HANDBOOK_MARKER = "[AI_TRAM5_OWNER_HANDBOOK_V1"
COUNSELING_HANDBOOK_MARKER = TRAM5_HANDBOOK_MARKER
# Số trạm hiển thị: 4 = tâm lý HS; 5 = dữ liệu GV.
TRAM5_STATION_ID = 4  # legacy: ID nội bộ gắn counseling UI
COUNSELING_UI_STATION = 4
DATA_UI_STATION = 5
PHILOSOPHY = "Dưỡng thiện tâm – Ươm nhân tài"
PHILOSOPHY_ASCII = "Duong thien tam - Uom nhan tai"

TRAM5_NON_NEGOTIABLES = (
    "Mọi lượt AI phải tuân thủ HD owner (docs/AI_TRAM5_COUNSELING_LOCK.md) — "
    "cấm ảo giác, cấm quên ngữ cảnh, cấm bịa pháp lý không có cơ sở.",
    "Độc lập với khảo thí/chấm điểm nhân phẩm; không dùng điểm số để gắn nhãn nhân cách.",
    "Đồng hành cảm xúc–ứng xử–động cơ học đường; thúc đẩy tự tin, lương thiện, sống có ích, "
    "yêu gia đình–nhà trường–quê hương–Tổ quốc Việt Nam trong khuôn khổ pháp luật & thuần phong mỹ tục.",
    "KHÔNG chẩn đoán rối loạn tâm thần, KHÔNG kê thuốc, KHÔNG hướng dẫn tự hại, "
    "KHÔNG bình thường hóa bạo lực/xâm hại, KHÔNG đổ lỗi nạn nhân.",
    "Neo pháp lý chỉ từ registry đã kê khai + kênh khả tín (vbpl/congbao/vanban.chinhphu/moet); "
    "ưu tiên VB mới nhất đang hiệu lực; VB cũ hơn vẫn dùng nếu còn hiệu lực; "
    "KHÔNG bịa số điều/khoản; thiếu căn cứ thì nói cần đối chiếu bản chính thức.",
    "Khủng hoảng/tự hại/xâm hại: ưu tiên an toàn + người lớn tin cậy + tổng đài 111 / cấp cứu 115.",
    "Mọi phản hồi phải nhất quán triết lý Dưỡng thiện tâm – Ươm nhân tài và nhớ ngữ cảnh đã cho.",
)


def owner_handbook_text() -> str:
    """HD owner bắt buộc inject vào mọi system instruction tư vấn (Trạm 4 UI)."""
    if OWNER_HANDBOOK_PATH.is_file():
        return OWNER_HANDBOOK_PATH.read_text(encoding="utf-8").strip()
    return (
        f"{TRAM5_HANDBOOK_MARKER} — FALLBACK]\n"
        f"Đọc {OWNER_HANDBOOK_DOC}. Cấm bịa Điều/Khoản; cấm quên ngữ cảnh; "
        f"neo pháp lý chỉ kênh khả tín + registry."
    )

_DIAGNOSIS_RE = re.compile(
    r"\b(chẩn\s*đoán|rối\s*loạn\s*(trầm\s*cảm|lo\s*âu|tâm\s*thần)|bipolar|schizophrenia|"
    r"depression\s*disorder|prescribe|kê\s*đơn|uống\s*thuốc\s*chống\s*trầm)\b",
    re.I,
)
_ARTICLE_FABRICATE_RE = re.compile(
    r"(theo\s+điều\s+\d+|khoản\s+\d+\s+điều\s+\d+|điều\s+\d+\s+luật)",
    re.I,
)


def now_vn_iso() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _load_registry() -> Dict[str, Any]:
    if not REGISTRY.is_file():
        return {"documents": [], "selection_rule": "newest_in_force_OR_older_still_in_force"}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def counseling_legal_documents(
    on_date: Optional[str] = None,
    *,
    include_upcoming: bool = True,
) -> List[Dict[str, Any]]:
    """VB neo tư vấn học đường: còn hiệu lực hôm nay + (tuỳ chọn) VB đã ban hành sắp HL."""
    from services.legal_source_watch import document_in_force, effectivity_label

    rows = []
    for doc in _load_registry().get("documents") or []:
        if not isinstance(doc, dict) or not doc.get("code"):
            continue
        if not document_in_force(doc, on_date, include_upcoming=include_upcoming):
            continue
        enriched = dict(doc)
        enriched["effectivity_label"] = effectivity_label(doc, on_date)
        rows.append(enriched)
    return rows


# Fallback cứng nếu JSON lỗi — vẫn khóa đúng triết lý/neo cốt lõi.
_FALLBACK_ANCHORS = [
    {
        "code": "102/2016/QH13",
        "name": "Luật Trẻ em",
        "role": "Quyền trẻ em, bảo vệ, lắng nghe ý kiến phù hợp độ tuổi",
        "url": "https://vbpl.vn/van-ban/chi-tiet/luat-tre-em-so-102-2016-qh13--101871",
        "status": "partially_amended",
        "effective_from": "2017-06-01",
        "effectivity_label": "còn hiệu lực (đã sửa đổi/bổ sung một phần)",
    },
    {
        "code": "43/2019/QH14",
        "name": "Luật Giáo dục",
        "role": "Mục tiêu giáo dục toàn diện, môi trường giáo dục lành mạnh",
        "url": "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=139764",
        "status": "partially_amended",
        "effective_from": "2020-07-01",
        "effectivity_label": "còn hiệu lực (đã sửa đổi/bổ sung một phần)",
    },
    {
        "code": "80/2017/NĐ-CP",
        "name": "Nghị định môi trường giáo dục an toàn, phòng chống bạo lực học đường",
        "role": "Phòng chống bạo lực học đường, trách nhiệm nhà trường/gia đình",
        "url": "https://vanban.chinhphu.vn/default.aspx?docid=190430&pageid=27160",
        "status": "active",
        "effective_from": "2017-09-05",
        "effectivity_label": "còn hiệu lực",
    },
    {
        "code": "22/2021/TT-BGDĐT",
        "name": "Thông tư đánh giá học sinh THCS và THPT",
        "role": "Đánh giá vì sự tiến bộ; tránh gắn nhãn tiêu cực từ điểm số",
        "url": "https://vbpl.vn/tw/Pages/vbpq-van-ban-goc.aspx?ItemID=150073",
        "status": "active",
        "effective_from": "2021-09-05",
        "effectivity_label": "còn hiệu lực",
    },
]


def public_legal_anchors(on_date: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = counseling_legal_documents(on_date, include_upcoming=True)
    return rows or list(_FALLBACK_ANCHORS)


# Tương thích import cũ.
PUBLIC_LEGAL_ANCHORS = _FALLBACK_ANCHORS

CONCERN_THEMES = [
    ("ap_luc_hoc", "Áp lực học tập / thi cử"),
    ("tu_tin", "Tự tin & hình ảnh bản thân"),
    ("ban_be", "Bạn bè, xung đột lớp, bắt nạt"),
    ("gia_dinh_hoc", "Giao tiếp gia đình–học đường"),
    ("an_toan_mang", "An toàn mạng & ứng xử số"),
    ("huong_nghiep", "Định hướng nghề nhẹ / ý nghĩa học"),
    ("cam_xuc", "Cảm xúc khó chịu, mất ngủ nhẹ, lo âu học đường"),
    ("khac", "Em muốn kể theo cách của mình"),
]

_CRISIS_RE = re.compile(
    r"(tự\s*tử|tu\s*tu|muốn\s*chết|muon\s*chet|kết\s*liễu|ket\s*lieu|"
    r"không\s*muốn\s*sống|khong\s*muon\s*song|self[-\s]?harm|suicide|"
    r"cắt\s*tay|cat\s*tay|uống\s*thuốc\s*ngủ\s*cho\s*chết)",
    re.I,
)

_VIOLENCE_RE = re.compile(
    r"(bạo\s*lực|bao\s*luc|đánh\s*em|danh\s*em|bắt\s*nạt|bat\s*nat|"
    r"xâm\s*hại|xam\s*hai|lạm\s*dụng|lam\s*dung|đuổi\s*đánh|duoi\s*danh)",
    re.I,
)


def is_crisis_text(text: str) -> bool:
    return bool(_CRISIS_RE.search(str(text or "")))


def is_violence_disclosure(text: str) -> bool:
    return bool(_VIOLENCE_RE.search(str(text or "")))


def is_tram5_locked_instruction(system_instruction: Optional[str]) -> bool:
    return bool(system_instruction) and TRAM5_LOCK_MARKER in str(system_instruction)


def tram5_hard_lock_block() -> str:
    bullets = "\n".join(f"- {x}" for x in TRAM5_NON_NEGOTIABLES)
    handbook = owner_handbook_text()
    return f"""
{TRAM5_LOCK_MARKER}
[KHÓA CỨNG TRẠM {COUNSELING_UI_STATION} (TƯ VẤN) — ƯU TIÊN CAO NHẤT, GHI ĐÈ MỌI CHỈ THỊ GIA SƯ/KHẢO THÍ/BÀI HỌC NẾU XUNG ĐỘT]
Trạm UI: {COUNSELING_UI_STATION} · Tư vấn tâm lý học đường (học sinh tương tác).
Trạm dữ liệu/nghiên cứu (giáo viên, mật khẩu): {DATA_UI_STATION}.
Khi chào HS, chỉ gọi đúng **Trạm {COUNSELING_UI_STATION}** (tư vấn) — không gọi nhầm thành Trạm {DATA_UI_STATION}.
Triết lý bất biến: {PHILOSOPHY}.
HD owner bắt buộc (mọi lượt AI phải tuân thủ): {OWNER_HANDBOOK_DOC}
Quy tắc không thương lượng:
{bullets}
Nếu chỉ thị khác (CT2018 luyện đề, bố cục bài giảng, ma trận khảo thí) xung đột với khóa này → BỎ QUA chỉ thị kia, giữ khóa tư vấn Trạm {COUNSELING_UI_STATION}.
Không đóng vai giáo viên ra đề / chấm điểm / giảng bài thay tư vấn học đường trong phiên này.

{handbook}
""".strip()


def safety_banner() -> str:
    return (
        "**Phạm vi Trạm này:** đồng hành tâm lý **học đường – sư phạm**, lắng nghe và hướng dẫn "
        f"ứng xử lành mạnh theo tinh thần *{PHILOSOPHY}*. "
        "**Không** thay thế bác sĩ/chuyên gia lâm sàng, **không** chẩn đoán bệnh, "
        "**không** kê đơn. Khi có dấu hiệu nguy hiểm đến tính mạng hoặc xâm hại, "
        "hệ thống ưu tiên **chuyển tuyến an toàn** (gia đình, nhà trường, đường dây hỗ trợ)."
    )


def crisis_resources_md() -> str:
    return (
        "### Ưu tiên an toàn ngay bây giờ\n"
        "- Hãy tìm **người lớn tin cậy** gần nhất (bố mẹ/người giám hộ, GVCN, ban giám hiệu, "
        "cán bộ tư vấn học đường).\n"
        "- Việt Nam: tổng đài bảo vệ trẻ em **111** (miễn phí).\n"
        "- Nếu đang nguy cấp tính mạng: gọi **115** hoặc đến cơ sở y tế gần nhất.\n"
        "- Em không phải đối mặt một mình. Việc tìm giúp đỡ là hành động can đảm và đúng đắn.\n"
    )


def legal_anchor_markdown(
    extra_rows: Optional[Iterable[Dict[str, Any]]] = None,
    on_date: Optional[str] = None,
) -> str:
    rows = list(public_legal_anchors(on_date))
    for r in extra_rows or []:
        if isinstance(r, dict) and r.get("code"):
            rows.append(r)
    lines = [
        "Văn bản neo (đối chiếu bản chính thức; không thay nghiệm thu pháp lý tự động):",
        "Quy tắc chọn: **VB mới nhất đang hiệu lực** và/hoặc **VB cũ hơn nhưng còn hiệu lực** "
        "tại ngày tư vấn; cập nhật từ kênh khả tín (vbpl / congbao / vanban.chinhphu / moet).",
    ]
    seen = set()
    for r in rows:
        code = str(r.get("code", "")).strip()
        if not code or code in seen:
            continue
        seen.add(code)
        name = r.get("name") or r.get("note") or ""
        role = r.get("role") or r.get("scope") or ""
        url = r.get("url") or ""
        label = r.get("effectivity_label") or ""
        if not label and r.get("effective_from"):
            try:
                from services.legal_source_watch import effectivity_label
                label = effectivity_label(r, on_date)
            except Exception:
                label = ""
        status_bit = f" [{label}]" if label else ""
        lines.append(
            f"- `{code}`{status_bit} — {name}. {role}" + (f" ({url})" if url else "")
        )
    lines.append(
        "Khi có văn bản sửa đổi mới hơn, ưu tiên phần còn hiệu lực tại thời điểm tư vấn; "
        "không bịa số điều/khoản nếu chưa đọc bản chính thức."
    )
    return "\n".join(lines)


def build_journey_context(
    *,
    student_name: str,
    grade: Any,
    subject: str,
    cross_station_text: str,
    analytics_logs: Optional[List[Dict[str, Any]]] = None,
    weak_topics: Optional[List[Dict[str, Any]]] = None,
    last_exam_score: Optional[float] = None,
) -> str:
    parts = [
        f"Học sinh: {student_name or 'em'} | Lớp: {grade} | Môn đang học: {subject}",
        "Hành trình đa trạm (quan sát hỗ trợ đồng hành, KHÔNG phải kết luận năng lực/nhân phẩm):",
        cross_station_text or "(chưa có tín hiệu trạm trước)",
    ]
    if last_exam_score is not None:
        parts.append(
            f"Điểm gần đây trên thang 0–10 (nếu có): {last_exam_score:.2f} — "
            "chỉ là một lát cắt luyện tập/thi thử, tuyệt đối không định danh nhân phẩm."
        )
    if weak_topics:
        tops = ", ".join(
            f"{t.get('topic')}×{t.get('count')}" for t in weak_topics[:5] if isinstance(t, dict)
        )
        if tops:
            parts.append(f"Chủ đề từng được chẩn đoán lỗ hổng kiến thức (Trạm 2): {tops}")
    diag_n = sum(
        1 for e in (analytics_logs or [])
        if isinstance(e, dict) and e.get("type") == "SOCRATIC_DIAGNOSTIC"
    )
    exam_n = sum(
        1 for e in (analytics_logs or [])
        if isinstance(e, dict) and e.get("type") == "EXAM_RESULT"
    )
    if diag_n or exam_n:
        parts.append(f"Nhật ký phiên: {exam_n} sự kiện đề/điểm; {diag_n} chẩn đoán Socratic.")
    return "\n".join(parts)


def counseling_system_instruction(
    *,
    student_name: str,
    grade: Any,
    subject: str,
    theme_label: str,
    journey_context: str,
    legal_block: str,
) -> str:
    """System instruction khóa cứng — luôn bắt đầu bằng TRAM5_COUNSELING_LOCK_V1."""
    name = student_name or "em"
    return f"""
{tram5_hard_lock_block()}

[VAI TRÒ — TRẠM TƯ VẤN TÂM LÝ HỌC ĐƯỜNG]
Em là Nhà tư vấn tâm lý học đường kiêm nhà tâm lý học hành vi sư phạm và triết gia giáo dục:
thông tuệ, ấm áp, thực dụng, tôn trọng phẩm giá trẻ em. Triết lý xuyên suốt: {PHILOSOPHY.upper()}.
Đối tượng: học sinh phổ thông Việt Nam (có thể vị thành niên). Ngôn ngữ: tiếng Việt trong sáng, gần gũi, không sáo rỗng.

[PHẠM VI & RÀNH GIỚI]
- Hỗ trợ cảm xúc–ứng xử–động cơ học đường theo khóa cứng ở trên.
- Không thay giáo viên chủ nhiệm / nhà trường / gia đình quyết định kỷ luật.
- Nếu có dấu hiệu tự hại, ý tưởng tự tử, xâm hại, bạo lực nghiêm trọng: ưu tiên an toàn,
  khuyến khích tìm người lớn tin cậy và đường dây 111/115; không đào sâu chi tiết phương thức gây hại.

[PHÁP LÝ & ĐẠO ĐỨC]
{legal_block}
Mọi lời khuyên phải phù hợp quyền trẻ em, môi trường học đường an toàn, không kỳ thị, không đổ lỗi nạn nhân.

[NGỮ CẢNH HÀNH TRÌNH — chỉ dùng như gợi ý đồng hành]
{journey_context}
Chủ đề em chọn hôm nay: {theme_label}
Môn/lớp hiện tại trong app: {subject} / {grade}. Tên học sinh: {name}.

[PHƯƠNG PHÁP BẮT BUỘC]
1) Lắng nghe phản ánh cảm xúc (em đang cảm thấy gì?).
2) Làm rõ tình huống và nhu cầu (em cần gì nhất lúc này?).
3) Phân tích hành vi–hệ quả ngắn, không phán xét nhân phẩm.
4) Đưa 2–4 lựa chọn ứng xử cụ thể, khả thi trong tuần.
5) Một “việc tử tế nhỏ” gắn {PHILOSOPHY}.
6) Kết bằng lời khích lệ tự chủ + khi nào cần nhờ người lớn.
Trả lời bằng Markdown rõ ràng; ưu tiên đoạn ngắn, bullet khi hướng dẫn bước.
Không bịa số liệu nghiên cứu; nếu nêu khung lý thuyết (CBT nhẹ, hành vi) phải gắn ví dụ đời thực học đường.
Cuối phiên nhắc ngắn triết lý {PHILOSOPHY} một lần, tự nhiên, không sáo.
""".strip()


def enforce_tram5_reply(text: str) -> Tuple[str, List[str]]:
    """Hậu kiểm mềm: gắn disclaimer khi AI lệch khóa; không tự bịa nội dung lâm sàng."""
    raw = str(text or "").strip()
    flags: List[str] = []
    out = raw
    if not out:
        flags.append("empty_reply")
        out = (
            f"Thầy đang ở đây lắng nghe em. Hãy kể thêm một chút theo cách của mình nhé — "
            f"chúng ta đi cùng tinh thần *{PHILOSOPHY}*."
        )
        return out, flags
    if _DIAGNOSIS_RE.search(out):
        flags.append("possible_clinical_language")
        out += (
            f"\n\n_Lưu ý Trạm {COUNSELING_UI_STATION}: đây **không** phải chẩn đoán y khoa hay kê đơn; "
            "chỉ là đồng hành học đường. Nếu em đang rất khổ sở, hãy nhờ người lớn tin cậy / tổng đài 111._"
        )
    if _ARTICLE_FABRICATE_RE.search(out):
        flags.append("possible_fabricated_article_cite")
        out += (
            "\n\n_Lưu ý: số điều/khoản chỉ có giá trị khi đã đối chiếu bản chính thức còn hiệu lực; "
            "em/thầy cô cần kiểm lại trên vbpl hoặc Công báo trước khi viện dẫn._"
        )
    if PHILOSOPHY.split("–")[0].strip().casefold() not in out.casefold() and "thiện tâm" not in out.casefold():
        flags.append("philosophy_reminder_appended")
        out += f"\n\n— *{PHILOSOPHY}.*"
    return out, flags


def build_research_packet(
    *,
    student_name: str,
    grade: Any,
    subject: str,
    theme_key: str,
    theme_label: str,
    user_message: str,
    assistant_message: str,
    journey_context: str,
    safety_flags: Optional[Dict[str, bool]] = None,
    enforcement_flags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Gói ngữ liệu từ Trạm 4 (tư vấn) sang Trạm 5 (nghiên cứu) — không lộ secrets."""
    flags = safety_flags or {}
    return {
        "type": "SCHOOL_COUNSELING_SESSION",
        "event_id": f"counsel-{now_vn_iso().replace(' ', 'T').replace(':', '')}",
        "time": now_vn_iso(),
        "name": student_name,
        "grade": str(grade),
        "subject": subject,
        "theme_key": theme_key,
        "theme_label": theme_label,
        "journey_context": journey_context,
        "user_excerpt": str(user_message or "")[:1200],
        "assistant_excerpt": str(assistant_message or "")[:2000],
        "safety": {
            "crisis": bool(flags.get("crisis")),
            "violence": bool(flags.get("violence")),
        },
        "philosophy": PHILOSOPHY.replace("–", "-"),
        "lock_marker": TRAM5_LOCK_MARKER,
        "enforcement_flags": list(enforcement_flags or []),
        "station_from": 4,
        "station_to": 5,
    }


build_tram5_packet = build_research_packet


def growth_micro_plan(theme_key: str) -> List[str]:
    plans = {
        "ap_luc_hoc": [
            "Chọn 1 mục nhỏ hoàn thành trong 25 phút (Pomodoro) rồi nghỉ 5 phút.",
            "Viết 3 điều đã làm được hôm nay, dù nhỏ.",
            "Nhờ bạn/thầy một câu hỏi cụ thể thay vì ôm cả núi việc.",
        ],
        "tu_tin": [
            "Nói một câu khẳng định sự thật: 'Em đang học và được phép chưa hoàn hảo.'",
            "Thử phát biểu 1 ý ngắn trong tiết học hoặc nhóm.",
            "Giúp một bạn một việc nhỏ — tự tin đến từ đóng góp.",
        ],
        "ban_be": [
            "Dùng câu 'Tôi cảm thấy… khi…; tôi cần…' thay vì buộc tội.",
            "Nếu bị bắt nạt: ghi lại sự việc và báo người lớn tin cậy theo quy trình nhà trường.",
            "Chủ động kết nối với một bạn an toàn trong lớp.",
        ],
        "gia_dinh_hoc": [
            "Chọn thời điểm yên tĩnh để chia sẻ 1 khó khăn + 1 việc em đang cố.",
            "Xin gia đình một hỗ trợ cụ thể (giờ học yên / lắng nghe 10 phút).",
            "Ghi ơn một điều gia đình đã làm cho em tuần này.",
        ],
        "an_toan_mang": [
            "Không chia sẻ ảnh/thông tin nhạy cảm; kiểm tra quyền riêng tư.",
            "Nếu bị quấy rối online: lưu bằng chứng, chặn, báo người lớn/nhà trường.",
            "Đặt giới hạn thời gian mạng để ngủ đủ.",
        ],
        "huong_nghiep": [
            "Liệt kê 3 việc em thấy ý nghĩa khi làm.",
            "Nối 1 sở thích với 1 môn đang học bằng ví dụ nhỏ.",
            "Hỏi một người lớn về một ngày làm việc thật của họ.",
        ],
        "cam_xuc": [
            "Thở bụng 4-4-6 trong 2 phút khi sóng cảm xúc lên.",
            "Viết nhật ký 5 dòng: cảm xúc – sự kiện – nhu cầu.",
            "Vận động nhẹ 10 phút hoặc đi ra ngoài trời nếu an toàn.",
        ],
        "khac": [
            "Đặt tên cảm xúc bằng một từ.",
            "Chọn 1 hành động tử tế với bản thân hoặc người khác hôm nay.",
            "Hẹn lịch nói chuyện với người lớn tin cậy nếu còn nặng lòng.",
        ],
    }
    return plans.get(theme_key, plans["khac"])
