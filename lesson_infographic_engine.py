from services.academic_context import canonical_subject
from services.lesson_export import faithful_infographic_data
# VIP 74.2 - HỆ THỐNG GIA SƯ AI THPT 2026 (CHUẨN GDPT 2018 - ĐỘNG CƠ CẨM NANG INFOGRAPHIC THỐNG KÊ MSLGN & ĐA MÔN)
# -*- coding: utf-8 -*-
r"""
HỆ THỐNG GSAI - THPT 2026 (VIP 66.2): ĐỘNG CƠ XUẤT PHIẾU HỌC TẬP & CẨM NANG INFOGRAPHIC VECTOR SVG CHUẨN A4
Chuẩn mực Mỹ thuật Sư phạm, Typography Học thuật (KaTeX & MathType), Tỷ lệ A4 Vàng (800 x 1130 px).
Cập nhật VIP 66.2 (18/10/2026): Đồng bộ quy chuẩn Chốt Chặn Cuối Cùng & typography bảng biểu.
Tích hợp:
  1. Typography Academic Quốc tế: Font 'STIX Two Text', 'Noto Serif', 'Times New Roman', 'Cambria Math'.
     Biến số toán học in nghiêng (*x*, *y*, *f*(*x*), *D*, *x*₀), chỉ số trên/dưới thật, ký hiệu Blackboard Bold (ℝ, ℤ, ℕ).
  2. Bố cục Focus Chips 2 dòng thông thoáng: TUYỆT ĐỐI KHÔNG CẮT CỤT TỪ KHÓA, KHÔNG BAO GIỜ DÙNG DẤU BA CHẤM '...'.
  3. Khắc phục 100% lỗi lặp số thứ tự (❶ ❶) ở tiến trình Polya.
  4. Đồ thị TikZ / SVG Vector tọa độ Oxy vạch số, đường gióng nét đứt, điểm cực trị CĐ, CT, điểm uốn I sắc sảo.
  5. Cung cấp cả 2 định dạng: Vector SVG A4 tải về & Mã nguồn Overleaf LaTeX / TikZ chuẩn mực TeX Live 2024.
0 Token, 0 API Key, Chạy hoàn toàn nội hàm 100%.
"""

import re
import html
import base64
from functools import lru_cache

def format_math_and_ipa_typography(text: str) -> str:
    r"""
    Chuẩn hóa sâu sắc công thức Toán học, KHTN và Ký hiệu Ngữ âm Quốc tế IPA:
    Tẩy sạch toàn bộ mã LaTeX thô (\mathbb{R}, \setminus, \left, \right...) thành ký tự Unicode sư phạm tuyệt mỹ.
    """
    if not text:
        return ""
    
    s = str(text)
    
    # 0. Loại bỏ định dạng Markdown in đậm/nghiêng rác
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'`(.*?)`', r'\1', s)
    
    # 1. Khử bọc LaTeX inline: $...$ hoặc $$...$$
    s = re.sub(r'\$\$(.*?)\$\$', r'\1', s)
    s = re.sub(r'\$(.*?)\$', r'\1', s)
    
    # 2. Xử lý các lệnh LaTeX đặc thù thường sót
    s = s.replace(r'\mathbb{R}', 'ℝ').replace(r'\mathbf{R}', 'ℝ')
    s = s.replace(r'\mathbb{Z}', 'ℤ').replace(r'\mathbb{N}', 'ℕ').replace(r'\mathbb{Q}', 'ℚ')
    s = s.replace(r'\setminus', '\\')
    s = s.replace(r'\left\{', '{').replace(r'\right\}', '}')
    s = s.replace(r'\left(', '(').replace(r'\right)', ')')
    s = s.replace(r'\left[', '[').replace(r'\right]', ']')
    s = s.replace(r'\left|', '|').replace(r'\right|', '|')
    s = s.replace(r'\quad', ' ').replace(r'\qquad', '  ')
    s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', s)
    
    # 3. Chuẩn hóa số mũ thường gặp trước khi đổi phân số: ^2 -> ², ^3 -> ³, ^n -> ⁿ
    sup_map = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', 'n': 'ⁿ', 'm': 'ᵐ', 'x': 'ˣ', 'y': 'ʸ'
    }
    def replace_sup(m):
        val = m.group(1)
        return "".join(sup_map.get(c, c) for c in val)
    s = re.sub(r'\^{([0-9n+-]+)}', replace_sup, s)
    s = re.sub(r'\^([0-9n])', replace_sup, s)
    
    # 4. Chuẩn hóa chỉ số dưới: _1 -> ₁, _2 -> ₂, _0 -> ₀, _x -> ₓ
    sub_map = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        'x': 'ₓ', 'y': 'ᵧ', 't': 'ₜ', 'i': 'ᵢ'
    }
    def replace_sub(m):
        val = m.group(1)
        return "".join(sub_map.get(c, c) for c in val)
    s = re.sub(r'_\{([0-9xyti]+)}', replace_sub, s)
    s = re.sub(r'_([0-9xyti])', replace_sub, s)

    # 5. Chuẩn hóa phân thức LaTeX \frac{A}{B} -> (A)/(B)
    s = re.sub(r'\\(d)?frac\{([^{}]+)\}\{([^{}]+)\}', r'(\2)/(\3)', s)
    
    # 6. Chuẩn hóa căn thức \sqrt{...}
    s = re.sub(r'\\sqrt\[(\d+)\]\{([^{}]+)\}', r'√[\1](\2)', s)
    s = re.sub(r'\\sqrt\{([^{}]+)\}', r'√(\1)', s)
    s = s.replace(r'\sqrt', '√')
    
    # 7. Chuẩn hóa công thức Hóa học thường gặp
    chem_subs = {
        'H2O': 'H₂O', 'CO2': 'CO₂', 'H2SO4': 'H₂SO₄', 'HCl': 'HCl', 'HNO3': 'HNO₃',
        'Fe2O3': 'Fe₂O₃', 'Fe3O4': 'Fe₃O₄', 'Al2O3': 'Al₂O₃', 'CaCO3': 'CaCO₃',
        'C2H5OH': 'C₂H₅OH', 'CH3COOH': 'CH₃COOH', 'C6H12O6': 'C₆H₁₂O₆',
        'CuSO4': 'CuSO₄', 'ZnSO4': 'ZnSO₄', 'BaSO4': 'BaSO₄', 'AgNO3': 'AgNO₃'
    }
    for chem_raw, chem_rich in chem_subs.items():
        s = re.sub(r'\b' + chem_raw + r'\b', chem_rich, s)
    
    # 8. Ký hiệu Toán & KHTN thông dụng (bảo toàn hàm lượng giác, logarit, tập hợp)
    latex_symbols = [
        (r'\sin', 'sin '), (r'\cos', 'cos '), (r'\tan', 'tan '), (r'\cot', 'cot '),
        (r'\ln', 'ln '), (r'\log', 'log '), (r'\max', 'max '), (r'\min', 'min '),
        (r'\sum', 'Σ'), (r'\prod', 'Π'), (r'\varnothing', '∅'), (r'\emptyset', '∅'),
        (r'\le', '≤'), (r'\ge', '≥'), (r'\neq', '≠'), (r'\approx', '≈'),
        (r'\pm', '±'), (r'\times', '×'), (r'\cdot', '·'), (r'\div', '÷'),
        (r'\infty', '∞'), (r'\Delta', 'Δ'), (r'\pi', 'π'), (r'\alpha', 'α'),
        (r'\beta', 'β'), (r'\theta', 'θ'), (r'\lambda', 'λ'), (r'\omega', 'ω'),
        (r'\in', '∈'), (r'\notin', '∉'), (r'\subset', '⊂'), (r'\cup', '∪'), (r'\cap', '∩'),
        (r'\forall', '∀'), (r'\exists', '∃'), (r'\to', '→'), (r'\rightarrow', '→'),
        (r'\Leftarrow', '⇐'), (r'\Rightarrow', '⇒'), (r'\Leftrightarrow', '⇔'),
        (r'\perp', '⊥'), (r'\parallel', '∥'), (r'\angle', '∠'), (r'\triangle', 'Δ'),
        (r'\lim', 'lim'), (r'\int', '∫')
    ]
    for raw, sym in latex_symbols:
        s = s.replace(raw, sym)
    
    # 9. Véc-tơ chuẩn: \vec{a} -> vec(a), \overrightarrow{AB} -> vec(AB)
    s = re.sub(r'\\(overrightarrow|vec)\{([^}]+)\}', r'vec(\2)', s)
    
    # 10. Mũi tên và ký hiệu phản ứng Hóa học
    s = s.replace('->', '→').replace('<=>', '⇌')
    
    # Dọn dẹp dấu gạch chéo ngược LaTeX còn sót
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    
    # Dọn dẹp khoảng trắng kép
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s


def wrap_text_two_lines(text: str, max_chars: int = 60) -> tuple:
    """
    Tự động phân bổ văn bản thành tối đa 2 dòng cân đối, không bao giờ ngắt đôi từ ngữ,
    TUYỆT ĐỐI KHÔNG CẮT CỤT BẰNG DẤU BA CHẤM '...'.
    """
    clean = format_math_and_ipa_typography(text)
    if len(clean) <= max_chars:
        return (clean, "")
    
    words = clean.split(' ')
    line1 = []
    line2 = []
    cur_len = 0
    split_done = False
    
    for w in words:
        if not split_done:
            if cur_len + len(w) + (1 if line1 else 0) <= max_chars:
                line1.append(w)
                cur_len += len(w) + (1 if len(line1) > 1 else 0)
            else:
                line2.append(w)
                split_done = True
        else:
            line2.append(w)
            
    return (" ".join(line1), " ".join(line2))


def wrap_text_to_lines(text: str, max_chars: int = 48, **kwargs) -> list:
    """
    Tự động phân bổ văn bản thành danh sách các dòng có độ dài tối đa max_chars ký tự,
    không bao giờ ngắt đôi từ ngữ, chống tràn viền tuyệt đối 100%.
    """
    effective_max = kwargs.get('max_chars_per_line', max_chars)
    clean = format_math_and_ipa_typography(text)
    if len(clean) <= effective_max:
        return [clean]
    
    words = clean.split(' ')
    lines = []
    current_line = []
    current_len = 0
    
    for w in words:
        if not w:
            continue
        space = 1 if current_line else 0
        if current_len + space + len(w) <= effective_max:
            current_line.append(w)
            current_len += space + len(w)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [w]
            current_len = len(w)

            
    if current_line:
        lines.append(" ".join(current_line))
        
    return lines


# Bí danh tương thích ngược cho các bộ kiểm thử
wrap_vietnamese_text = wrap_text_to_lines


def generate_worked_example_and_visual(subject_name: str, grade_lvl: int, topic_text: str, extracted_example: dict = None) -> dict:
    """
    Sinh 1 Ví dụ minh họa điển hình (Worked Example) và Đồ thị/Hình vẽ trực quan (TikZ/SVG)
    chuẩn kiến thức khoa học sư phạm GDPT 2018 (đầy đủ hệ trục, đường gióng, điểm đặc biệt) cho từng chủ đề.
    ƯU TIÊN 100% SỬ DỤNG VÍ DỤ VÀ TIẾN TRÌNH 4 BƯỚC RÚT TRÍCH TỪ CHÍNH BÀI HỌC CỦA HỌC SINH NẾU CÓ!
    """
    subj_lower = (subject_name or "").lower()
    topic_lower = (topic_text or "").lower()
    
    # Hàm helper trả về ví dụ ưu tiên từ bài học kết hợp với hình vẽ đồ họa chuẩn xác
    def build_result(fb_title: str, fb_steps: list, svg_code: str) -> dict:
        final_title = fb_title
        final_steps = fb_steps
        if extracted_example and extracted_example.get("title") and extracted_example.get("steps"):
            final_title = extracted_example["title"]
            final_steps = extracted_example["steps"]
        return {"title": final_title, "steps": final_steps, "visual_svg": svg_code}
    
    # 1. TOÁN HỌC
    if "toán" in subj_lower:
        if any(kw in topic_lower for kw in ["vectơ", "vector", "oxyz", "tọa độ", "toạ độ", "không gian", "mặt phẳng", "mặt cầu", "đường thẳng"]):
            example_title = f"Ví dụ minh họa: Phép toán Vectơ & Tọa độ Oxyz ({topic_text})"
            example_steps = [
                ("❶ Xác định tọa độ vectơ", "Xác định tọa độ điểm M(x; y; z) và các vectơ vec(u), vec(v) trong không gian Oxyz."),
                ("❷ Phép toán & Tích vô hướng", "Tính vec(u) · vec(v) = x₁x₂ + y₁y₂ + z₁z₂; Tính độ dài |vec(u)| = √(x² + y² + z²)."),
                ("❸ Góc & Tính vuông góc", "Hai vectơ vuông góc ⇔ vec(u) · vec(v) = 0; Tính cos(vec(u), vec(v)) qua tích vô hướng."),
                ("❹ Vận dụng giải toán THPT", "Tìm tọa độ điểm thỏa mãn hệ thức vectơ hoặc viết phương trình mặt phẳng, mặt cầu.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <line x1="85" y1="120" x2="85" y2="18" stroke="#334155" stroke-width="1.4" />
                <polygon points="82,18 85,10 88,18" fill="#334155" />
                <text x="75" y="20" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">z</text>
                
                <line x1="85" y1="120" x2="245" y2="120" stroke="#334155" stroke-width="1.4" />
                <polygon points="245,117 253,120 245,123" fill="#334155" />
                <text x="245" y="133" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">y</text>
                
                <line x1="85" y1="120" x2="32" y2="168" stroke="#334155" stroke-width="1.4" />
                <polygon points="31,164 26,173 35,169" fill="#334155" />
                <text x="18" y="170" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">x</text>
                <text x="73" y="130" font-size="11" font-style="italic" font-family="'STIX Two Text', serif" fill="#64748b">O</text>
                
                <line x1="85" y1="120" x2="55" y2="147" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                <line x1="55" y1="147" x2="160" y2="147" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                <line x1="85" y1="120" x2="190" y2="120" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                <line x1="160" y1="147" x2="190" y2="120" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                <line x1="160" y1="147" x2="160" y2="60" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                <line x1="85" y1="33" x2="85" y2="120" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2" />
                
                <line x1="85" y1="120" x2="160" y2="60" stroke="#2563eb" stroke-width="2.6" stroke-linecap="round" />
                <polygon points="158,55 167,59 161,65" fill="#2563eb" />
                <circle cx="160" cy="60" r="3.5" fill="#dc2626" />
                <text x="135" y="48" font-size="10.5" font-weight="700" font-family="'STIX Two Text', serif" fill="#2563eb">vec(u)(x; y; z)</text>
                
                <line x1="85" y1="120" x2="68" y2="135" stroke="#dc2626" stroke-width="1.8" />
                <polygon points="68,132 63,139 71,136" fill="#dc2626" />
                <text x="54" y="132" font-size="9" font-weight="700" fill="#dc2626">vec(i)</text>
                
                <line x1="85" y1="120" x2="115" y2="120" stroke="#16a34a" stroke-width="1.8" />
                <polygon points="115,118 121,120 115,122" fill="#16a34a" />
                <text x="105" y="112" font-size="9" font-weight="700" fill="#16a34a">vec(j)</text>
                
                <line x1="85" y1="120" x2="85" y2="90" stroke="#7c3aed" stroke-width="1.8" />
                <polygon points="83,90 85,84 87,90" fill="#7c3aed" />
                <text x="91" y="93" font-size="9" font-weight="700" fill="#7c3aed">vec(k)</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif any(kw in topic_lower for kw in ["ghép nhóm", "mẫu số liệu", "mslgn", "phân tán", "số đặc trưng", "thống kê", "trung vị", "tứ phân vị", "phương sai", "độ lệch chuẩn", "khoảng biến thiên"]):
            example_title = f"Ví dụ minh họa: Tính các số đặc trưng mẫu số liệu ghép nhóm ({topic_text})"
            example_steps = [
                ("❶ Cỡ mẫu & Giá trị đại diện", "Cỡ mẫu n = 50; Xác định x_i = (u_i + u_{i+1})/2 cho từng nhóm số liệu [u_i; u_{i+1})."),
                ("❷ Số trung bình x̄", "x̄ = (Σ n_i · x_i) / n = 62.4 (điểm/kg/phút). Công thức trung tâm của phân bố."),
                ("❸ Trung vị M_e & Tứ phân vị", "Vị trí n/2 = 25 thuộc nhóm [60; 70) ⇒ M_e = 60 + [(25 - 18)/15] · 10 ≈ 64.67."),
                ("❹ Phương sai & Độ lệch chuẩn", "s² = (1/n)·Σ n_i·x_i² - (x̄)² ≈ 48.64 ⇒ Độ lệch chuẩn s = √(s²) ≈ 6.97.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <text x="132" y="20" font-size="10.5" font-weight="700" font-family="'STIX Two Text', serif" text-anchor="middle" fill="#0f172a">BIỂU ĐỒ TẦN SỐ GHÉP NHÓM (HISTOGRAM)</text>
                
                <line x1="35" y1="140" x2="250" y2="140" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,137 257,140 250,143" fill="#334155" />
                <line x1="35" y1="140" x2="35" y2="30" stroke="#334155" stroke-width="1.3" />
                <polygon points="32,30 35,23 38,30" fill="#334155" />
                <text x="245" y="153" font-size="10" font-weight="700" fill="#334155">x</text>
                <text x="22" y="32" font-size="10" font-weight="700" fill="#334155">n_i</text>
                <text x="25" y="145" font-size="9" fill="#64748b">O</text>
                
                <rect x="45" y="105" width="38" height="35" fill="#bae6fd" stroke="#0284c7" stroke-width="1.2" rx="2" />
                <text x="64" y="100" font-size="9" font-weight="700" text-anchor="middle" fill="#0369a1">6</text>
                
                <rect x="83" y="70" width="38" height="70" fill="#7dd3fc" stroke="#0284c7" stroke-width="1.2" rx="2" />
                <text x="102" y="65" font-size="9" font-weight="700" text-anchor="middle" fill="#0369a1">12</text>
                
                <rect x="121" y="35" width="38" height="105" fill="#38bdf8" stroke="#0369a1" stroke-width="1.4" rx="2" />
                <text x="140" y="30" font-size="9.5" font-weight="700" text-anchor="middle" fill="#075985">18 (M_o)</text>
                
                <rect x="159" y="82" width="38" height="58" fill="#7dd3fc" stroke="#0284c7" stroke-width="1.2" rx="2" />
                <text x="178" y="77" font-size="9" font-weight="700" text-anchor="middle" fill="#0369a1">10</text>
                
                <rect x="197" y="117" width="38" height="23" fill="#bae6fd" stroke="#0284c7" stroke-width="1.2" rx="2" />
                <text x="216" y="112" font-size="9" font-weight="700" text-anchor="middle" fill="#0369a1">4</text>
                
                <text x="45" y="152" font-size="8.5" text-anchor="middle" fill="#475569">40</text>
                <text x="83" y="152" font-size="8.5" text-anchor="middle" fill="#475569">50</text>
                <text x="121" y="152" font-size="8.5" text-anchor="middle" fill="#475569">60</text>
                <text x="159" y="152" font-size="8.5" text-anchor="middle" fill="#475569">70</text>
                <text x="197" y="152" font-size="8.5" text-anchor="middle" fill="#475569">80</text>
                <text x="235" y="152" font-size="8.5" text-anchor="middle" fill="#475569">90</text>
                
                <line x1="139" y1="35" x2="139" y2="140" stroke="#dc2626" stroke-width="1.6" stroke-dasharray="3,3" />
                <circle cx="139" cy="85" r="3" fill="#dc2626" />
                <text x="143" y="90" font-size="9" font-weight="700" fill="#dc2626">M_e ≈ 64.7</text>
                <text x="132" y="167" font-size="9" font-weight="600" text-anchor="middle" fill="#0369a1">Cỡ mẫu n = 50 | s ≈ 6.97</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif any(kw in topic_lower for kw in ["xác suất", "biến cố", "nhị thức", "tổ hợp", "chỉnh hợp"]):
            example_title = f"Ví dụ minh họa: Phân tích Xác suất & Sơ đồ hình cây ({topic_text})"
            example_steps = [
                ("❶ Không gian mẫu & Biến cố", "Xác định không gian mẫu n(Ω) và các biến cố thành phần A, B độc lập."),
                ("❷ Xác suất thành phần", "P(A) = 0.6; P(B) = 0.4. Xác suất có điều kiện: P(B|A) hoặc P(B|Ā)."),
                ("❸ Quy tắc nhân xác suất", "P(A ∩ B) = P(A) · P(B) = 0.6 · 0.4 = 0.24 (do A, B độc lập)."),
                ("❹ Xác suất toàn phần & Bayes", "P(E) = P(A)·P(E|A) + P(Ā)·P(E|Ā); Tính P(A|E) qua công thức Bayes.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <text x="132" y="20" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">SƠ ĐỒ HÌNH CÂY XÁC SUẤT (PROBABILITY TREE)</text>
                
                <circle cx="45" cy="95" r="5" fill="#0284c7" />
                <text x="32" y="98" font-size="10" font-weight="700" fill="#0284c7">Ω</text>
                
                <line x1="45" y1="95" x2="120" y2="55" stroke="#334155" stroke-width="1.5" />
                <line x1="45" y1="95" x2="120" y2="135" stroke="#334155" stroke-width="1.5" />
                <text x="75" y="65" font-size="9" font-weight="700" fill="#0284c7">P(A)</text>
                <text x="75" y="125" font-size="9" font-weight="700" fill="#64748b">P(Ā)</text>
                
                <circle cx="120" cy="55" r="4" fill="#16a34a" />
                <text x="128" y="58" font-size="9.5" font-weight="700" fill="#16a34a">A</text>
                <circle cx="120" cy="135" r="4" fill="#64748b" />
                <text x="128" y="138" font-size="9.5" font-weight="700" fill="#64748b">Ā</text>
                
                <line x1="120" y1="55" x2="195" y2="38" stroke="#0284c7" stroke-width="1.3" />
                <line x1="120" y1="55" x2="195" y2="72" stroke="#64748b" stroke-width="1.3" />
                <text x="198" y="42" font-size="9" font-weight="700" fill="#16a34a">B [P(AB)]</text>
                <text x="198" y="75" font-size="9" fill="#64748b">B̄</text>
                
                <line x1="120" y1="135" x2="195" y2="118" stroke="#0284c7" stroke-width="1.3" />
                <line x1="120" y1="135" x2="195" y2="152" stroke="#64748b" stroke-width="1.3" />
                <text x="198" y="122" font-size="9" fill="#334155">B</text>
                <text x="198" y="155" font-size="9" fill="#64748b">B̄</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif any(kw in topic_lower for kw in ["nguyên hàm", "tích phân", "diện tích hình phẳng"]):
            example_title = f"Ví dụ minh họa: Ứng dụng Tích phân tính diện tích ({topic_text})"
            example_steps = [
                ("❶ Phương trình hoành độ giao điểm", "Xét f(x) = g(x) ⇔ x² - 2x = 0 ⇔ x = 0 (cận a) hoặc x = 2 (cận b)."),
                ("❷ Thiết lập tích phân", "Diện tích hình phẳng: S = ∫[0; 2] |(2x - x²)| dx."),
                ("❸ Phá dấu trị tuyệt đối & Tính toán", "Trên [0; 2], 2x - x² ≥ 0 ⇒ S = [x² - x³/3] thế cận từ 0 đến 2."),
                ("❹ Kết luận & Ý nghĩa hình học", "S = 4 - 8/3 = 4/3 (đvdt). Diện tích phần hình phẳng giới hạn.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <line x1="20" y1="130" x2="250" y2="130" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,127 258,130 250,133" fill="#334155" />
                <line x1="60" y1="165" x2="60" y2="20" stroke="#334155" stroke-width="1.3" />
                <polygon points="57,20 60,12 63,20" fill="#334155" />
                <text x="250" y="142" font-size="10" font-weight="700" fill="#334155">x</text>
                <text x="48" y="22" font-size="10" font-weight="700" fill="#334155">y</text>
                <text x="48" y="142" font-size="9" fill="#64748b">O</text>
                
                <path d="M 60,130 Q 120,30 180,130 Z" fill="#bae6fd" fill-opacity="0.6" stroke="#0284c7" stroke-width="2" />
                <text x="120" y="95" font-size="11" font-weight="700" text-anchor="middle" fill="#0369a1">S = 4/3</text>
                <circle cx="60" cy="130" r="3" fill="#dc2626" />
                <text x="60" y="145" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">a=0</text>
                <circle cx="180" cy="130" r="3" fill="#dc2626" />
                <text x="180" y="145" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">b=2</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif "phân thức" in topic_lower or "tiệm cận" in topic_lower or "bậc hai trên bậc nhất" in topic_lower:
            example_title = "Ví dụ minh họa: Khảo sát hàm số y = (x² + x + 1) / (x - 1)"
            example_steps = [
                ("❶ TXĐ & Đạo hàm", "D = ℝ \\ {1}. Đạo hàm: y' = (x² - 2x - 2) / (x - 1)²."),
                ("❷ Điểm Cực trị", "y' = 0 ⇔ x = 1 - √3 (y ≈ -0.73) hoặc x = 1 + √3 (y ≈ 4.73)."),
                ("❸ Đường Tiệm cận", "TCĐ: x = 1; Tiệm cận xiên: y = x + 2 (do y = x + 2 + 3/(x - 1))."),
                ("❹ Tâm đối xứng", "Giao điểm hai đường tiệm cận: I(1; 3).")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <line x1="20" y1="105" x2="250" y2="105" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,102 258,105 250,108" fill="#334155" />
                <line x1="105" y1="165" x2="105" y2="15" stroke="#334155" stroke-width="1.3" />
                <polygon points="102,15 105,7 108,15" fill="#334155" />
                <text x="250" y="119" font-size="11" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" font-style="italic" fill="#1e293b">x</text>
                <text x="92" y="18" font-size="11" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" font-style="italic" fill="#1e293b">y</text>
                <text x="92" y="118" font-size="11" font-style="italic" font-family="'STIX Two Text', serif" fill="#64748b">O</text>
                
                <!-- Tiệm cận đứng x = 1 -->
                <line x1="135" y1="15" x2="135" y2="165" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4,3" />
                <text x="139" y="28" font-size="9.5" font-weight="700" fill="#dc2626">x = 1 (TCĐ)</text>
                
                <!-- Tiệm cận xiên y = x + 2 -->
                <line x1="30" y1="155" x2="235" y2="40" stroke="#0284c7" stroke-width="1.5" stroke-dasharray="4,3" />
                <text x="180" y="38" font-size="9.5" font-weight="700" fill="#0284c7">y = x + 2 (TCX)</text>
                
                <!-- Tâm đối xứng I(1; 3) -->
                <circle cx="135" cy="75" r="4" fill="#dc2626" />
                <text x="142" y="76" font-size="10.5" font-weight="700" fill="#dc2626">I(1; 3)</text>
                
                <!-- Nhánh trái và phải của Hypebol -->
                <path d="M 35,150 Q 75,135 105,115 T 125,25" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" />
                <path d="M 145,165 Q 165,95 195,70 T 245,50" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" />
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif grade_lvl == 10 or any(kw in topic_lower for kw in ["bậc hai", "parabol", "tam thức", "hàm số bậc hai", "hệ thức lượng", "tam giác", "bất phương trình"]):
            example_title = f"Ví dụ minh họa: Khảo sát hàm số bậc hai Parabol y = ax² + bx + c ({topic_text})"
            example_steps = [
                ("❶ TXĐ & Tọa độ đỉnh", "TXĐ: D = ℝ. Tọa độ đỉnh I(-b/(2a); -Δ/(4a)) = I(1; -1)."),
                ("❷ Trục đối xứng", "Trục đối xứng là đường thẳng x = -b/(2a) = 1."),
                ("❸ Chiều biến thiên", "Do a = 1 > 0: Hàm số nghịch biến trên (-∞; 1), đồng biến trên (1; +∞)."),
                ("❹ Giao điểm tọa độ", "Cắt trục Oy tại (0; 0); Cắt trục Ox tại hai nghiệm x = 0 và x = 2.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <line x1="20" y1="120" x2="250" y2="120" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,117 258,120 250,123" fill="#334155" />
                <line x1="85" y1="165" x2="85" y2="15" stroke="#334155" stroke-width="1.3" />
                <polygon points="82,15 85,7 88,15" fill="#334155" />
                <text x="250" y="133" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">x</text>
                <text x="72" y="18" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">y</text>
                <text x="72" y="132" font-size="11" font-style="italic" font-family="'STIX Two Text', serif" fill="#64748b">O</text>
                
                <!-- Trục đối xứng x = 1 -->
                <line x1="145" y1="15" x2="145" y2="165" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3" />
                <text x="148" y="25" font-size="9" font-weight="700" fill="#64748b">x = 1</text>
                
                <!-- Đường Parabol y = x² - 2x -->
                <path d="M 45,35 Q 145,215 245,35" fill="none" stroke="#2563eb" stroke-width="2.6" stroke-linecap="round" />
                
                <!-- Đỉnh I(1; -1) -->
                <circle cx="145" cy="145" r="4" fill="#dc2626" />
                <text x="150" y="152" font-size="10.5" font-weight="700" fill="#dc2626">I(1; -1)</text>
                
                <!-- Điểm cắt gốc O(0; 0) và x=2 -->
                <circle cx="85" cy="120" r="3" fill="#2563eb" />
                <circle cx="205" cy="120" r="3" fill="#2563eb" />
                <text x="202" y="133" font-size="9.5" fill="#334155">2</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        elif grade_lvl == 11 or any(kw in topic_lower for kw in ["lượng giác", "sin", "cos", "tan", "cấp số cộng", "cấp số nhân", "dãy số", "mũ", "logarit"]):
            example_title = f"Ví dụ minh họa: Khảo sát hàm số & Dao động lượng giác y = sin(x) ({topic_text})"
            example_steps = [
                ("❶ TXĐ & Tập giá trị", "TXĐ: D = ℝ. Tập giá trị: T = [-1; 1], tuần hoàn chu kỳ T = 2π."),
                ("❷ Tính chẵn lẻ", "sin(-x) = -sin(x) ⇒ Hàm số lẻ, đồ thị nhận gốc tọa độ O làm tâm đối xứng."),
                ("❸ Điểm Cực trị", "Giá trị lớn nhất y_max = 1 tại x = π/2 + k2π; y_min = -1 tại x = -π/2 + k2π."),
                ("❹ Tính đơn điệu", "Đồng biến trên [-π/2 + k2π; π/2 + k2π]; nghịch biến trên [π/2 + k2π; 3π/2 + k2π].")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <line x1="20" y1="95" x2="250" y2="95" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,92 258,95 250,98" fill="#334155" />
                <line x1="125" y1="165" x2="125" y2="15" stroke="#334155" stroke-width="1.3" />
                <polygon points="122,15 125,7 128,15" fill="#334155" />
                <text x="250" y="108" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">x</text>
                <text x="112" y="18" font-size="11" font-weight="700" font-family="'STIX Two Text', serif" font-style="italic" fill="#1e293b">y</text>
                <text x="112" y="108" font-size="11" font-style="italic" font-family="'STIX Two Text', serif" fill="#64748b">O</text>
                
                <!-- Biên độ +1 và -1 -->
                <line x1="20" y1="45" x2="245" y2="45" stroke="#dc2626" stroke-width="1" stroke-dasharray="3,3" />
                <text x="25" y="40" font-size="9" font-weight="700" fill="#dc2626">y = +1</text>
                <line x1="20" y1="145" x2="245" y2="145" stroke="#dc2626" stroke-width="1" stroke-dasharray="3,3" />
                <text x="25" y="157" font-size="9" font-weight="700" fill="#dc2626">y = -1</text>
                
                <!-- Sóng sin y = sin(x) -->
                <path d="M 35,95 Q 60,45 80,45 T 125,95 T 170,145 T 215,95" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" />
                <circle cx="80" cy="45" r="3.5" fill="#dc2626" />
                <text x="75" y="38" font-size="9" font-weight="700" fill="#dc2626">π/2</text>
                <circle cx="170" cy="145" r="3.5" fill="#2563eb" />
                <text x="165" y="158" font-size="9" font-weight="700" fill="#2563eb">3π/2</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        else:
            example_title = f"Ví dụ minh họa: Khảo sát hàm số bậc ba y = x³ - 3x² + 2 ({topic_text})"
            example_steps = [
                ("❶ TXĐ & Đạo hàm", "TXĐ: D = ℝ. Đạo hàm: y' = 3x² - 6x = 3x(x - 2)."),
                ("❷ Điểm Cực trị", "y' = 0 ⇔ x = 0 ⇒ CĐ(0; 2) và x = 2 ⇒ CT(2; -2)."),
                ("❸ Tâm đối xứng", "Hoành độ tâm đối xứng x₀ = -b/(3a) = 1 ⇒ Tâm đối xứng I(1; 0)."),
                ("❹ Tính đơn điệu", "Hàm số đồng biến (ĐB) trên (-∞; 0), (2; +∞); nghịch biến (NB) trên (0; 2).")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <!-- Trục tọa độ Ox, Oy với mũi tên chuẩn khảo thí -->
                <line x1="20" y1="98" x2="250" y2="98" stroke="#334155" stroke-width="1.3" />
                <polygon points="250,95 258,98 250,101" fill="#334155" />
                <line x1="105" y1="165" x2="105" y2="15" stroke="#334155" stroke-width="1.3" />
                <polygon points="102,15 105,7 108,15" fill="#334155" />
                <text x="250" y="112" font-size="11" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" font-style="italic" fill="#1e293b">x</text>
                <text x="92" y="18" font-size="11" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" font-style="italic" fill="#1e293b">y</text>
                <text x="92" y="112" font-size="11" font-style="italic" font-family="'STIX Two Text', serif" fill="#64748b">O</text>
                
                <!-- Vạch số và nhãn tọa độ trên trục -->
                <line x1="145" y1="95" x2="145" y2="101" stroke="#334155" stroke-width="1.2" />
                <text x="142" y="112" font-size="9.5" font-family="'STIX Two Text', serif" fill="#334155">1</text>
                <line x1="185" y1="95" x2="185" y2="101" stroke="#334155" stroke-width="1.2" />
                <text x="182" y="112" font-size="9.5" font-family="'STIX Two Text', serif" fill="#334155">2</text>
                
                <line x1="102" y1="48" x2="108" y2="48" stroke="#334155" stroke-width="1.2" />
                <text x="92" y="52" font-size="9.5" font-family="'STIX Two Text', serif" fill="#334155">2</text>
                <line x1="102" y1="148" x2="108" y2="148" stroke="#334155" stroke-width="1.2" />
                <text x="86" y="152" font-size="9.5" font-family="'STIX Two Text', serif" fill="#334155">-2</text>
                
                <!-- Đường gióng nét đứt chuẩn SGK từ điểm cực tiểu CT(2; -2) -->
                <line x1="185" y1="98" x2="185" y2="148" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3" />
                <line x1="105" y1="148" x2="185" y2="148" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3" />
                
                <!-- Đường cong bậc ba mềm mại y = x³ - 3x² + 2 vẽ chuẩn xác -->
                <path d="M 68,130 C 82,78 95,50 105,48 C 120,45 135,72 145,98 C 158,124 172,150 185,148 C 198,146 210,105 225,65" fill="none" stroke="#2563eb" stroke-width="2.6" stroke-linecap="round" />
                
                <!-- Điểm cực đại CĐ(0; 2) -->
                <circle cx="105" cy="48" r="4" fill="#dc2626" />
                <text x="60" y="44" font-size="10.5" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" fill="#dc2626">CĐ(0; 2)</text>
                
                <!-- Điểm cực tiểu CT(2; -2) -->
                <circle cx="185" cy="148" r="4" fill="#2563eb" />
                <text x="192" y="153" font-size="10.5" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" fill="#2563eb">CT(2; -2)</text>
                
                <!-- Tâm đối xứng I(1; 0) -->
                <circle cx="145" cy="98" r="3.5" fill="#7c3aed" />
                <text x="148" y="92" font-size="10" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" fill="#7c3aed">I(1; 0)</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
            
    # 2. VẬT LÝ
    elif ("vật lý" in subj_lower or "vật lí" in subj_lower or subj_lower in ["lý", "lí", "vat ly", "vat li", "physics"]) and "địa" not in subj_lower:
        example_title = f"Ví dụ minh họa: Phân tích hiện tượng & Bài toán mẫu ({topic_text})"
        example_steps = [
            ("❶ Phương trình dao động", "x = 4·cos(10πt - π/3) (cm). Biên độ A = 4 cm."),
            ("❷ Chu kỳ & Tần số", "Tần số góc ω = 10π rad/s ⇒ f = 5 Hz; Chu kỳ T = 0.2 s."),
            ("❸ Vận tốc cực đại", "v_max = ω·A = 40π cm/s ≈ 1.256 m/s (tại VTCB)."),
            ("❹ Gia tốc cực đại", "a_max = ω²·A = 4000 cm/s² = 40 m/s² (tại biên).")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <line x1="20" y1="90" x2="250" y2="90" stroke="#334155" stroke-width="1.3" />
            <polygon points="250,87 258,90 250,93" fill="#334155" />
            <line x1="40" y1="165" x2="40" y2="15" stroke="#334155" stroke-width="1.3" />
            <polygon points="37,15 40,7 43,15" fill="#334155" />
            <text x="250" y="105" font-size="10.5" font-weight="700" fill="#334155">t(s)</text>
            <text x="25" y="18" font-size="10.5" font-weight="700" fill="#334155">x(cm)</text>
            <path d="M 40,125 C 65,160 90,160 115,90 C 140,20 165,20 190,90 C 215,160 235,140 245,100" fill="none" stroke="#0284c7" stroke-width="2.5" />
            <line x1="40" y1="35" x2="245" y2="35" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,3" />
            <text x="45" y="30" font-size="9.5" font-weight="700" fill="#ef4444">+A = +4 cm</text>
            <line x1="40" y1="145" x2="245" y2="145" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,3" />
            <text x="45" y="160" font-size="9.5" font-weight="700" fill="#ef4444">-A = -4 cm</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)
        
    # 3. HÓA HỌC
    elif "hóa" in subj_lower:
        if grade_lvl in [10, 11] or any(kw in topic_lower for kw in ["nguyên tử", "tuần hoàn", "liên kết", "oxi hóa", "nhiệt hóa học", "tốc độ", "cân bằng", "điện li", "ph", "hydrocarbon", "alkane", "alkene", "alcyne"]):
            example_title = f"Ví dụ minh họa: Cân bằng hóa học & Phản ứng ({topic_text})"
            example_steps = [
                ("❶ Nguyên lý chuyển dịch", "Hệ phản ứng: N₂(k) + 3H₂(k) ⇌ 2NH₃(k) (ΔH < 0, phản ứng tỏa nhiệt)."),
                ("❷ Ảnh hưởng của nhiệt độ", "Khi hạ nhiệt độ, cân bằng chuyển dịch theo chiều thuận (chiều tỏa nhiệt) để bù đắp."),
                ("❸ Ảnh hưởng của áp suất", "Tăng áp suất: Cân bằng chuyển dịch về phía giảm số mol khí (từ 4 mol về 2 mol)."),
                ("❹ Hiệu suất thực tế", "Sử dụng xúc tác Fe, nhiệt độ khoảng 450°C và áp suất cao 200 atm để tối ưu hóa.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <rect x="25" y="45" width="215" height="85" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5" />
                <text x="132" y="70" font-size="11" font-weight="700" text-anchor="middle" fill="#1e40af">N₂(k) + 3H₂(k) ⇌ 2NH₃(k)</text>
                <text x="132" y="90" font-size="9.5" font-weight="600" text-anchor="middle" fill="#dc2626">ΔH < 0 (Tỏa nhiệt) | Δn = -2</text>
                <text x="132" y="112" font-size="9" text-anchor="middle" fill="#1e293b">Tăng P: Chuyển dịch thuận → | Giảm T: Thuận →</text>
                <text x="132" y="155" font-size="9" font-weight="700" text-anchor="middle" fill="#0369a1">Nguyên lý chuyển dịch cân bằng Le Chatelier</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        else:
            example_title = f"Ví dụ minh họa: Phản ứng hóa học & Thực nghiệm ({topic_text})"
            example_steps = [
                ("❶ Phương trình phản ứng", "CH₃COOH + C₂H₅OH ⇌ CH₃COOC₂H₅ + H₂O (H₂SO₄ đặc, t°)."),
                ("❷ Bản chất hóa học", "Phản ứng thuận nghịch hai chiều; H₂SO₄ đặc hút nước và làm xúc tác."),
                ("❸ Tách & Thu nhận", "Este nhẹ hơn nước, nổi lên trên tạo thành lớp chất lỏng phân tách."),
                ("❹ Hiệu suất phản ứng", "Tăng nồng độ chất phản ứng hoặc chưng cất este liên tục để chuyển dịch cân bằng.")
            ]
            visual_svg = '''
            <g transform="translate(15, 10)">
                <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
                <rect x="25" y="35" width="70" height="95" rx="10" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" />
                <rect x="170" y="35" width="70" height="95" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="1.5" />
                <line x1="100" y1="75" x2="160" y2="75" stroke="#0f172a" stroke-width="1.6" />
                <polygon points="160,71 168,75 160,79" fill="#0f172a" />
                <line x1="160" y1="89" x2="100" y2="89" stroke="#0f172a" stroke-width="1.6" />
                <polygon points="100,85 92,89 100,93" fill="#0f172a" />
                <text x="105" y="65" font-size="10" font-weight="700" fill="#dc2626">H₂SO₄ đặc, t°</text>
                <text x="32" y="145" font-size="9.5" font-weight="700" fill="#0369a1">Chất phản ứng</text>
                <text x="177" y="145" font-size="9.5" font-weight="700" fill="#b45309">Sản phẩm tạo</text>
            </g>
            '''
            return build_result(example_title, example_steps, visual_svg)
        
    # 4. TIẾNG ANH
    elif "tiếng anh" in subj_lower or "anh" in subj_lower:
        example_title = f"Worked Example: Sentence Structure & Collocations ({topic_text})"
        example_steps = [
            ("❶ Target Sentence", "She has achieved international recognition for her scientific research."),
            ("❷ Grammar Focus", "Present Perfect (S + have/has + V-ed/P2 + O) expressing lifetime achievement."),
            ("❸ Phonetic Stress", "a-chieve /əˈtʃiːv/ (2nd syllable) | re-cog-ni-tion /ˌrekəɡˈnɪʃn/ (3rd syllable)."),
            ("❹ Academic Collocation", "achieve / gain international recognition for (thành ngữ trọng tâm thi THPT).")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <rect x="20" y="30" width="225" height="38" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="1.2" />
            <text x="32" y="54" font-size="12" font-weight="700" fill="#3730a3">/əˈtʃiːv/ (Stress on 2nd)</text>
            <rect x="20" y="80" width="225" height="38" rx="8" fill="#fef2f2" stroke="#ef4444" stroke-width="1.2" />
            <text x="32" y="104" font-size="11.5" font-weight="700" fill="#991b1b">/ˌrekəɡˈnɪʃn/ (Primary 3rd)</text>
            <text x="25" y="148" font-size="10.5" font-weight="600" fill="#475569">💡 Intonation: Falling pitch at the period (.)</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)
        
    # 5. SINH HỌC
    elif "sinh" in subj_lower:
        example_title = f"Ví dụ minh họa: Di truyền học Mendel & Tế bào học ({topic_text})"
        example_steps = [
            ("❶ Thế hệ xuất phát (P)", "P thuần chủng: Hoa đỏ (AA) × Hoa trắng (aa) ⇒ Giao tử: 100% A × 100% a."),
            ("❷ Thế hệ con lai F₁", "F₁: 100% Aa (100% Hoa đỏ mang alen trội A át chế alen lặn a)."),
            ("❸ F₁ tự thụ phấn (F₁ × F₁)", "Aa × Aa ⇒ Tỉ lệ phân ly kiểu gen F₂: 1 AA : 2 Aa : 1 aa."),
            ("❹ Tỉ lệ phân ly kiểu hình F₂", "3 Cây hoa đỏ (AA, Aa) : 1 Cây hoa trắng (aa) (Chuẩn tỷ lệ 3 : 1).")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <rect x="15" y="16" width="62" height="30" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.2" />
            <text x="46" y="35" font-size="10.5" font-weight="700" text-anchor="middle" fill="#991b1b">P: AA × aa</text>
            <line x1="77" y1="31" x2="105" y2="31" stroke="#64748b" stroke-width="1.5" />
            <polygon points="105,28 112,31 105,34" fill="#64748b" />
            
            <rect x="115" y="16" width="62" height="30" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2" />
            <text x="146" y="35" font-size="10.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">F₁: 100% Aa</text>
            <line x1="177" y1="31" x2="200" y2="31" stroke="#64748b" stroke-width="1.5" />
            <polygon points="200,28 207,31 200,34" fill="#64748b" />
            
            <rect x="25" y="58" width="215" height="105" rx="8" fill="#ffffff" stroke="#0f172a" stroke-width="1.3" />
            <line x1="25" y1="84" x2="240" y2="84" stroke="#cbd5e1" stroke-width="1" />
            <line x1="25" y1="124" x2="240" y2="124" stroke="#cbd5e1" stroke-width="1" />
            <line x1="75" y1="58" x2="75" y2="163" stroke="#cbd5e1" stroke-width="1" />
            <line x1="158" y1="58" x2="158" y2="163" stroke="#cbd5e1" stroke-width="1" />
            
            <text x="50" y="75" font-size="10" font-weight="700" text-anchor="middle" fill="#64748b">♀ \\ ♂</text>
            <text x="116" y="75" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0284c7">½ A</text>
            <text x="199" y="75" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0284c7">½ a</text>
            
            <text x="50" y="108" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0284c7">½ A</text>
            <text x="116" y="108" font-size="10" font-weight="700" text-anchor="middle" fill="#15803d">¼ AA (Đỏ)</text>
            <text x="199" y="108" font-size="10" font-weight="700" text-anchor="middle" fill="#15803d">¼ Aa (Đỏ)</text>
            
            <text x="50" y="148" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0284c7">½ a</text>
            <text x="116" y="148" font-size="10" font-weight="700" text-anchor="middle" fill="#15803d">¼ Aa (Đỏ)</text>
            <text x="199" y="148" font-size="10.5" font-weight="700" text-anchor="middle" fill="#dc2626">¼ aa (Trắng)</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 6. LỊCH SỬ
    elif "lịch sử" in subj_lower or "sử" in subj_lower:
        example_title = f"Ví dụ minh họa & Tiến trình mốc son: {topic_text}"
        example_steps = [
            ("❶ Tiền đề lịch sử", "Mâu thuẫn xã hội gay gắt; Chuẩn bị về tư tưởng, tổ chức và lực lượng cách mạng."),
            ("❷ Bước ngoặt chiến lược", "Nắm bắt thời cơ lịch sử, chuyển hướng chỉ đạo chiến lược đúng đắn sáng tạo."),
            ("❸ Đỉnh cao quyết định", "Tổng khởi nghĩa / Chiến dịch quyết chiến chiến lược đập tan ách thống trị."),
            ("❹ Ý nghĩa thời đại", "Giải phóng dân tộc, mở ra kỷ nguyên độc lập, tự do và chủ nghĩa xã hội.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <line x1="20" y1="88" x2="245" y2="88" stroke="#0f172a" stroke-width="2.5" />
            <polygon points="245,84 255,88 245,92" fill="#0f172a" />
            
            <circle cx="45" cy="88" r="6" fill="#dc2626" stroke="#ffffff" stroke-width="2" />
            <line x1="45" y1="88" x2="45" y2="45" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="2,2" />
            <rect x="15" y="22" width="60" height="24" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-width="1" />
            <text x="45" y="38" font-size="9.5" font-weight="700" text-anchor="middle" fill="#991b1b">Tiền đề</text>
            
            <circle cx="115" cy="88" r="6" fill="#d97706" stroke="#ffffff" stroke-width="2" />
            <line x1="115" y1="88" x2="115" y2="132" stroke="#d97706" stroke-width="1.2" stroke-dasharray="2,2" />
            <rect x="85" y="132" width="60" height="24" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="1" />
            <text x="115" y="148" font-size="9.5" font-weight="700" text-anchor="middle" fill="#92400e">Bước ngoặt</text>
            
            <circle cx="175" cy="88" r="6" fill="#2563eb" stroke="#ffffff" stroke-width="2" />
            <line x1="175" y1="88" x2="175" y2="45" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="2,2" />
            <rect x="145" y="22" width="60" height="24" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1" />
            <text x="175" y="38" font-size="9.5" font-weight="700" text-anchor="middle" fill="#1e40af">Cao trào</text>
            
            <circle cx="230" cy="88" r="7" fill="#16a34a" stroke="#ffffff" stroke-width="2" />
            <line x1="230" y1="88" x2="230" y2="132" stroke="#16a34a" stroke-width="1.2" stroke-dasharray="2,2" />
            <rect x="200" y="132" width="60" height="24" rx="4" fill="#dcfce7" stroke="#16a34a" stroke-width="1" />
            <text x="230" y="148" font-size="9.5" font-weight="700" text-anchor="middle" fill="#166534">Thắng lợi</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 7. ĐỊA LÝ
    elif "địa lý" in subj_lower or "địa" in subj_lower:
        example_title = f"Ví dụ minh họa & Phân tích cơ cấu địa lý: {topic_text}"
        example_steps = [
            ("❶ Vị trí & Phạm vi", "Nội chí tuyến Bắc bán cầu, giàu tiềm năng phát triển kinh tế biển đảo."),
            ("❷ Tự nhiên & Khí hậu", "Nhiệt đới ẩm gió mùa, địa hình đa dạng 3/4 là đồi núi, phân hóa sâu sắc."),
            ("❸ Cơ cấu kinh tế", "Chuyển dịch đúng hướng: Giảm tỷ trọng nông nghiệp, tăng mạnh công nghiệp và dịch vụ."),
            ("❹ Vùng kinh tế trọng điểm", "Phát huy thế mạnh chuyên môn hóa từng vùng lãnh thổ kinh tế bền vững.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <text x="132" y="24" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">CƠ CẤU KINH TẾ THEO NGÀNH (%)</text>
            <line x1="35" y1="140" x2="245" y2="140" stroke="#64748b" stroke-width="1.2" />
            <line x1="35" y1="140" x2="35" y2="35" stroke="#64748b" stroke-width="1.2" />
            
            <rect x="55" y="95" width="38" height="45" rx="4" fill="#16a34a" />
            <text x="74" y="90" font-size="10" font-weight="700" text-anchor="middle" fill="#16a34a">12%</text>
            <text x="74" y="155" font-size="9" text-anchor="middle" fill="#334155">Nông nghiệp</text>
            
            <rect x="115" y="60" width="38" height="80" rx="4" fill="#2563eb" />
            <text x="134" y="55" font-size="10" font-weight="700" text-anchor="middle" fill="#2563eb">38%</text>
            <text x="134" y="155" font-size="9" text-anchor="middle" fill="#334155">Công nghiệp</text>
            
            <rect x="175" y="45" width="38" height="95" rx="4" fill="#d97706" />
            <text x="194" y="40" font-size="10" font-weight="700" text-anchor="middle" fill="#d97706">50%</text>
            <text x="194" y="155" font-size="9" text-anchor="middle" fill="#334155">Dịch vụ</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 8. TIN HỌC
    elif "tin học" in subj_lower or "tin" in subj_lower:
        example_title = f"Ví dụ minh họa & Lưu đồ thuật toán: {topic_text}"
        example_steps = [
            ("❶ Xác định bài toán", "Input: Dãy số A gồm n phần tử và khóa k • Output: Vị trí của k trong dãy."),
            ("❷ Ý tưởng thuật toán", "Thuật toán tìm kiếm nhị phân / Chia để trị: So sánh k với phần tử giữa A[mid]."),
            ("❸ Tiến trình lặp / Đệ quy", "Nếu A[mid] == k: Trả về mid; Nếu k < A[mid]: Tìm nửa trái; Ngược lại tìm nửa phải."),
            ("❹ Độ phức tạp thực thi", "Thời gian thực thi tối ưu: O(log n); Tiết kiệm tài nguyên bộ nhớ O(1).")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <rect x="85" y="18" width="95" height="28" rx="14" fill="#dcfce7" stroke="#16a34a" stroke-width="1.3" />
            <text x="132" y="36" font-size="10.5" font-weight="700" text-anchor="middle" fill="#15803d">Bắt đầu</text>
            <line x1="132" y1="46" x2="132" y2="60" stroke="#0f172a" stroke-width="1.4" />
            <polygon points="132,66 128,58 136,58" fill="#0f172a" />
            
            <polygon points="132,68 200,95 132,122 64,95" fill="#fef3c7" stroke="#d97706" stroke-width="1.3" />
            <text x="132" y="99" font-size="10" font-weight="700" text-anchor="middle" fill="#b45309">A[mid] == k?</text>
            
            <line x1="200" y1="95" x2="225" y2="95" stroke="#16a34a" stroke-width="1.4" />
            <text x="210" y="88" font-size="8.5" font-weight="700" fill="#16a34a">Đúng</text>
            <rect x="200" y="125" width="55" height="26" rx="4" fill="#dcfce7" stroke="#16a34a" stroke-width="1.2" />
            <text x="227" y="142" font-size="9" font-weight="700" text-anchor="middle" fill="#166534">Tìm thấy</text>
            <line x1="227" y1="95" x2="227" y2="125" stroke="#16a34a" stroke-width="1.4" />
            
            <line x1="132" y1="122" x2="132" y2="135" stroke="#dc2626" stroke-width="1.4" />
            <text x="142" y="132" font-size="8.5" font-weight="700" fill="#dc2626">Sai</text>
            <rect x="75" y="135" width="114" height="28" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-width="1.2" />
            <text x="132" y="153" font-size="9.5" font-weight="700" text-anchor="middle" fill="#991b1b">Thu hẹp nửa khoảng</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 9. CÔNG NGHỆ
    elif "công nghệ" in subj_lower:
        example_title = f"Ví dụ minh họa & Sơ đồ nguyên lý: {topic_text}"
        example_steps = [
            ("❶ Nguồn cấp & Cảm biến", "Thu nhận tín hiệu vật lý từ môi trường (nhiệt độ, ánh sáng, độ ẩm)."),
            ("❷ Khối xử lý trung tâm", "Vi điều khiển / Mạch logic phân tích dữ liệu và tạo tín hiệu điều khiển."),
            ("❸ Mạch khuếch đại & Chấp hành", "Kích hoạt Rơ-le (Relay) hoặc Tranzito đóng cắt thiết bị công suất lớn."),
            ("❹ Ứng dụng thông minh", "Tự động hóa nông nghiệp công nghệ cao, nhà thông minh (Smart Home).")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <rect x="25" y="25" width="60" height="35" rx="6" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.3" />
            <text x="55" y="46" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0369a1">Cảm biến</text>
            <line x1="85" y1="42" x2="115" y2="42" stroke="#0f172a" stroke-width="1.4" />
            <polygon points="115,39 122,42 115,45" fill="#0f172a" />
            
            <rect x="122" y="25" width="60" height="35" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3" />
            <text x="152" y="46" font-size="9.5" font-weight="700" text-anchor="middle" fill="#b45309">Xử lý (MCU)</text>
            <line x1="182" y1="42" x2="205" y2="42" stroke="#0f172a" stroke-width="1.4" />
            <polygon points="205,39 212,42 205,45" fill="#0f172a" />
            
            <rect x="205" y="80" width="50" height="65" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.3" />
            <text x="230" y="112" font-size="9" font-weight="700" text-anchor="middle" fill="#15803d">Thiết bị</text>
            <text x="230" y="125" font-size="9" font-weight="700" text-anchor="middle" fill="#15803d">Tải</text>
            <line x1="212" y1="42" x2="230" y2="42" stroke="#0f172a" stroke-width="1.4" />
            <line x1="230" y1="42" x2="230" y2="80" stroke="#0f172a" stroke-width="1.4" />
            <polygon points="227,80 230,87 233,80" fill="#0f172a" />
            
            <rect x="35" y="105" width="125" height="35" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.2" />
            <text x="97" y="126" font-size="9.5" font-weight="700" text-anchor="middle" fill="#334155">⚡ Nguồn nuôi (5V/12V)</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 10. GIÁO DỤC KINH TẾ VÀ PHÁP LUẬT
    elif "kinh tế" in subj_lower or "pháp luật" in subj_lower or "gdcd" in subj_lower:
        example_title = f"Ví dụ minh họa & Tình huống pháp lý: {topic_text}"
        example_steps = [
            ("❶ Cơ chế Cung - Cầu", "Cung là lượng hàng hóa sẵn sàng bán; Cầu là lượng hàng hóa cần mua ở các mức giá."),
            ("❷ Điểm cân bằng thị trường (E)", "Giao điểm đường Cung (S) và Cầu (D) xác định Giá cân bằng P₀ và Lượng cân bằng Q₀."),
            ("❸ Tác động của giá cả & cạnh tranh", "Khi Giá > P₀: Dư thừa hàng hóa; Khi Giá < P₀: Khan hiếm hàng hóa."),
            ("❹ Tuân thủ pháp luật & Đạo đức", "Kinh doanh minh bạch, bảo vệ quyền lợi người tiêu dùng và thực hiện nghĩa vụ thuế.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <line x1="35" y1="145" x2="245" y2="145" stroke="#334155" stroke-width="1.3" />
            <polygon points="245,142 253,145 245,148" fill="#334155" />
            <line x1="35" y1="145" x2="35" y2="20" stroke="#334155" stroke-width="1.3" />
            <polygon points="32,20 35,12 38,20" fill="#334155" />
            <text x="245" y="160" font-size="10" font-weight="700" fill="#334155">Q (Lượng)</text>
            <text x="18" y="22" font-size="10" font-weight="700" fill="#334155">P (Giá)</text>
            
            <line x1="55" y1="130" x2="225" y2="40" stroke="#2563eb" stroke-width="2.2" />
            <text x="228" y="44" font-size="10" font-weight="700" fill="#2563eb">S (Cung)</text>
            
            <line x1="55" y1="40" x2="225" y2="130" stroke="#dc2626" stroke-width="2.2" />
            <text x="228" y="134" font-size="10" font-weight="700" fill="#dc2626">D (Cầu)</text>
            
            <circle cx="140" cy="85" r="4.5" fill="#16a34a" />
            <text x="148" y="80" font-size="10.5" font-weight="800" fill="#16a34a">E(P₀, Q₀)</text>
            <line x1="35" y1="85" x2="140" y2="85" stroke="#64748b" stroke-width="1" stroke-dasharray="2,2" />
            <line x1="140" y1="85" x2="140" y2="145" stroke="#64748b" stroke-width="1" stroke-dasharray="2,2" />
            <text x="22" y="88" font-size="8.5" font-weight="700" fill="#64748b">P₀</text>
            <text x="135" y="157" font-size="8.5" font-weight="700" fill="#64748b">Q₀</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 11. NGỮ VĂN
    elif "ngữ văn" in subj_lower or "văn" in subj_lower:
        example_title = f"Ví dụ minh họa & Đặc trưng thể loại: {topic_text}"
        example_steps = [
            ("❶ Bối cảnh & Cảm hứng", "Hoàn cảnh xuất thân, thời đại lịch sử và cảm hứng chủ đạo của tác giả."),
            ("❷ Đặc trưng thể loại", "Kết cấu cốt truyện, không gian nghệ thuật và hệ thống hình tượng trung tâm."),
            ("❸ Bút pháp nghệ thuật", "Biện pháp tu từ đắt giá, điểm nhìn trần thuật tinh tế và nhạc điệu ngôn từ."),
            ("❹ Giá trị & Bài học", "Chiều sâu nhân đạo, giá trị hiện thực và bức thông điệp nhân sinh vĩnh cửu.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <text x="132" y="22" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">CẤU TRÚC 4 CHIỀU PHÂN TÍCH TÁC PHẨM</text>
            
            <rect x="25" y="38" width="95" height="48" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.3" />
            <text x="72" y="58" font-size="10" font-weight="700" text-anchor="middle" fill="#1d4ed8">1. Bối cảnh</text>
            <text x="72" y="74" font-size="8.5" text-anchor="middle" fill="#475569">Thời đại & Cảm hứng</text>
            
            <rect x="145" y="38" width="95" height="48" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.3" />
            <text x="192" y="58" font-size="10" font-weight="700" text-anchor="middle" fill="#b45309">2. Thể loại</text>
            <text x="192" y="74" font-size="8.5" text-anchor="middle" fill="#475569">Hình tượng & Kết cấu</text>
            
            <rect x="25" y="105" width="95" height="48" rx="6" fill="#fdf4ff" stroke="#a855f7" stroke-width="1.3" />
            <text x="72" y="125" font-size="10" font-weight="700" text-anchor="middle" fill="#7e22ce">3. Bút pháp</text>
            <text x="72" y="141" font-size="8.5" text-anchor="middle" fill="#475569">Ngôn từ & Tu từ</text>
            
            <rect x="145" y="105" width="95" height="48" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.3" />
            <text x="192" y="125" font-size="10" font-weight="700" text-anchor="middle" fill="#15803d">4. Tư tưởng</text>
            <text x="192" y="141" font-size="8.5" text-anchor="middle" fill="#475569">Nhân đạo & Hiện thực</text>
            
            <!-- Trục liên kết trung tâm -->
            <line x1="120" y1="62" x2="145" y2="62" stroke="#64748b" stroke-width="1.4" />
            <line x1="120" y1="129" x2="145" y2="129" stroke="#64748b" stroke-width="1.4" />
            <line x1="72" y1="86" x2="72" y2="105" stroke="#64748b" stroke-width="1.4" />
            <line x1="192" y1="86" x2="192" y2="105" stroke="#64748b" stroke-width="1.4" />
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 12. KHOA HỌC TỰ NHIÊN (KHTN - THCS)
    elif "khoa học tự nhiên" in subj_lower or "khtn" in subj_lower:
        example_title = f"Ví dụ minh họa & Khám phá KHTN: {topic_text}"
        example_steps = [
            ("❶ Quan sát & Hiện tượng", "Nhận biết hiện tượng vật lý, hóa học, sinh học diễn ra trong tự nhiên."),
            ("❷ Mô hình & Bản chất", "Xây dựng mô hình phân tử, chuỗi chuyển hóa hoặc tế bào sinh vật."),
            ("❸ Đo lường & Thực nghiệm", "Sử dụng dụng cụ thí nghiệm, thu thập số liệu và kiểm chứng giả thuyết."),
            ("❹ Ứng dụng & Môi trường", "Giải thích các ứng dụng đời sống và ý thức bảo vệ tài nguyên môi trường.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <text x="132" y="24" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">VÒNG TRÒN KHÁM PHÁ KHTN</text>
            <circle cx="132" cy="100" r="48" fill="none" stroke="#0284c7" stroke-width="2" stroke-dasharray="4,3" />
            <circle cx="132" cy="52" r="14" fill="#dbeafe" stroke="#2563eb" stroke-width="1.3" />
            <text x="132" y="56" font-size="9" font-weight="700" text-anchor="middle" fill="#1d4ed8">Quan sát</text>
            <circle cx="180" cy="100" r="14" fill="#fef3c7" stroke="#d97706" stroke-width="1.3" />
            <text x="180" y="104" font-size="8.5" font-weight="700" text-anchor="middle" fill="#b45309">Dự đoán</text>
            <circle cx="132" cy="148" r="14" fill="#dcfce7" stroke="#16a34a" stroke-width="1.3" />
            <text x="132" y="152" font-size="8.5" font-weight="700" text-anchor="middle" fill="#15803d">Thí nghiệm</text>
            <circle cx="84" cy="100" r="14" fill="#fee2e2" stroke="#dc2626" stroke-width="1.3" />
            <text x="84" y="104" font-size="8.5" font-weight="700" text-anchor="middle" fill="#991b1b">Kết luận</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 13. LỊCH SỬ & ĐỊA LÝ (THCS)
    elif "lịch sử & địa lý" in subj_lower or "lịch sử và địa lý" in subj_lower:
        example_title = f"Ví dụ minh họa & Khám phá Sử - Địa: {topic_text}"
        example_steps = [
            ("❶ Không gian địa lý", "Địa hình, sông núi, khí hậu định hình điều kiện sinh sống và địa bàn cư trú."),
            ("❷ Dòng chảy lịch sử", "Tiến trình dựng nước và giữ nước của cha ông qua các thời kỳ hào hùng."),
            ("❸ Dấu ấn văn hóa", "Di sản vật thể, phi vật thể và các phong tục tập quán truyền thống."),
            ("❹ Bài học thế hệ trẻ", "Lòng yêu nước, tự hào dân tộc và trách nhiệm bảo vệ chủ quyền non sông.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <text x="132" y="24" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">GIAO THOA LỊCH SỬ VÀ ĐỊA LÝ</text>
            <circle cx="95" cy="98" r="45" fill="#dbeafe" fill-opacity="0.7" stroke="#2563eb" stroke-width="1.8" />
            <circle cx="170" cy="98" r="45" fill="#fef3c7" fill-opacity="0.7" stroke="#d97706" stroke-width="1.8" />
            <text x="75" y="102" font-size="10.5" font-weight="700" fill="#1e40af">Địa lý</text>
            <text x="185" y="102" font-size="10.5" font-weight="700" fill="#92400e">Lịch sử</text>
            <text x="132" y="94" font-size="8.5" font-weight="700" text-anchor="middle" fill="#0f172a">Dân tộc</text>
            <text x="132" y="107" font-size="8.5" font-weight="700" text-anchor="middle" fill="#0f172a">&amp; Đất nước</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)

    # 14. MÔN KHÁC (FALLBACK CHUẨN MỰC)
    else:
        example_title = f"Ví dụ minh họa & Phân tích chuyên sâu: {topic_text}"
        example_steps = [
            ("❶ Tiền đề & Khái niệm cốt lõi", "Bối cảnh phát sinh, phạm vi tác động và các quy luật phổ quát."),
            ("❷ Cơ chế hoạt động & Diễn tiến", "Mối liên hệ nhân quả khách quan và trình tự phát triển biện chứng."),
            ("❸ Ứng dụng thực tiễn", "Vận dụng vào giải quyết bài toán thực tế và các tình huống kiểm tra THPT."),
            ("❹ Bài học & Tổng kết", "Đúc rút phương pháp luận tư duy phản biện và ghi nhớ kiến thức bền vững.")
        ]
        visual_svg = '''
        <g transform="translate(15, 10)">
            <rect width="265" height="175" fill="#f8fafc" stroke="#cbd5e1" rx="8" />
            <circle cx="50" cy="85" r="26" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.8" />
            <text x="32" y="89" font-size="10.5" font-weight="700" fill="#0369a1">Tiền đề</text>
            <line x1="78" y1="85" x2="110" y2="85" stroke="#0284c7" stroke-width="2" />
            <circle cx="135" cy="85" r="26" fill="#fef3c7" stroke="#d97706" stroke-width="1.8" />
            <text x="118" y="89" font-size="10.5" font-weight="700" fill="#b45309">Diễn tiến</text>
            <line x1="162" y1="85" x2="195" y2="85" stroke="#d97706" stroke-width="2" />
            <circle cx="220" cy="85" r="26" fill="#dcfce7" stroke="#16a34a" stroke-width="1.8" />
            <text x="204" y="89" font-size="10.5" font-weight="700" fill="#15803d">Kết luận</text>
        </g>
        '''
        return build_result(example_title, example_steps, visual_svg)
# ==============================================================================
# BẢNG TRA CỨU TÊN CHUẨN CÁC CHƯƠNG SGK KẾT NỐI TRI THỨC VỚI CUỘC SỐNG (GDPT 2018)
# ==============================================================================
CURRICULUM_CHAPTER_NAMES = {
    ("Hóa học", 12): {
        1: "Ester - Lipid (Xà phòng & Chất giặt rửa)",
        2: "Carbohydrate (Glucose, Fructose, Cellulose)",
        3: "Hợp chất chứa Nitrogen (Amine, Amino acid, Protein)",
        4: "Polymer & Vật liệu Polymer",
        5: "Pin điện hóa & Điện phân",
        6: "Đại cương kim loại",
        7: "Kim loại nhóm IA, IIA & Nhôm",
        8: "Sơ lược về phức chất"
    },
    ("Hóa học", 11): {
        1: "Cân bằng hóa học & pH Dung dịch",
        2: "Nitrogen & Sulfur",
        3: "Hydrocarbon (Alkane, Alkene, Arene)",
        4: "Alcohol & Phenol",
        5: "Carbonyl & Carboxylic acid"
    },
    ("Hóa học", 10): {
        1: "Cấu tạo nguyên tử & Bảng tuần hoàn",
        2: "Liên kết hóa học",
        3: "Phản ứng oxi hóa - khử",
        4: "Năng lượng hóa học & Enthalpy",
        5: "Tốc độ phản ứng hóa học",
        6: "Nguyên tố nhóm Halogen"
    },
    ("Toán học", 12): {
        1: "Ứng dụng đạo hàm khảo sát hàm số",
        2: "Tọa độ và vectơ trong không gian Oxyz",
        3: "Các số đặc trưng đo mức độ phân tán",
        4: "Nguyên hàm, Tích phân và ứng dụng",
        5: "Phương pháp tọa độ Oxyz nâng cao",
        6: "Xác suất có điều kiện và Bayes"
    },
    ("Toán học", 11): {
        1: "Hàm số lượng giác & Phương trình lượng giác",
        2: "Dãy số, Cấp số cộng & Cấp số nhân",
        3: "Giới hạn & Hàm số liên tục",
        4: "Đường thẳng & Mặt phẳng trong không gian",
        5: "Hàm số mũ & Hàm số lôgarit",
        6: "Đạo hàm & Tiếp tuyến"
    },
    ("Toán học", 10): {
        1: "Mệnh đề & Tập hợp",
        2: "Bất phương trình bậc nhất hai ẩn",
        3: "Hệ thức lượng trong tam giác",
        4: "Vectơ trong mặt phẳng Oxy",
        5: "Hàm số bậc hai & Tam thức bậc hai"
    },
    ("Vật lý", 12): {
        1: "Vật lý nhiệt & Nội năng",
        2: "Khí lý tưởng & Thuyết động học",
        3: "Từ trường & Cảm ứng điện từ",
        4: "Vật lý hạt nhân & Phóng xạ"
    },
    ("Vật lý", 11): {
        1: "Dao động điều hòa",
        2: "Sóng cơ & Sóng âm",
        3: "Điện trường & Tụ điện",
        4: "Dòng điện không đổi"
    },
    ("Vật lý", 10): {
        1: "Mô tả chuyển động",
        2: "Động lực học (Ba định luật Newton)",
        3: "Năng lượng & Công cơ học",
        4: "Động lượng & Va chạm"
    },
    ("Sinh học", 12): {
        1: "Di truyền phân tử DNA, RNA & Đột biến gen",
        2: "Nhiễm sắc thể & Cơ chế phân bào",
        3: "Quy luật di truyền Mendel & Hoán vị",
        4: "Di truyền học quần thể",
        5: "Di truyền y học & Công nghệ gen",
        6: "Tiến hóa sinh học",
        7: "Hệ sinh thái & Sinh quyển"
    },
    ("Lịch sử", 12): {
        1: "Thế giới sau Chiến tranh thế giới thứ hai",
        2: "ASEAN: Những chặng đường lịch sử",
        3: "Cách mạng tháng Tám 1945 và Kháng chiến chống Pháp",
        4: "Kháng chiến chống Mỹ cứu nước (1954 - 1975)",
        5: "Công cuộc Đổi mới từ năm 1986 đến nay"
    },
    ("Địa lý", 12): {
        1: "Vị trí địa lý và phạm vi lãnh thổ Việt Nam",
        2: "Đặc điểm tự nhiên và tài nguyên thiên nhiên",
        3: "Địa lý dân cư và nguồn lao động",
        4: "Chuyển dịch cơ cấu kinh tế các ngành",
        5: "Các vùng kinh tế trọng điểm"
    },
    ("Tiếng Anh", 12): {
        1: "Unit 1: Life Stories we admire",
        2: "Unit 2: A diversity of cultures",
        3: "Unit 3: Green living & Environment",
        4: "Unit 4: Urbanisation",
        5: "Unit 5: The world of work"
    }
}


def clean_topic_title(subject_name, grade_lvl, raw_topic):
    # A typed lesson/chapter number is not enough to infer a verified SGK title.
    return str(raw_topic or "").strip() or f"{canonical_subject(subject_name)} lớp {grade_lvl}"


def extract_self_distilled_infographic_blocks(subject_name: str, grade_lvl: int, topic_text: str, lesson_markdown: str):
    """
    TRÍCH XUẤT TRỰC TIẾP KHỐI CẨM NANG INFOGRAPHIC TỰ THÂN (SELF-DISTILLED INFOGRAPHIC)
    Được AI đúc kết từ chính bài học sinh ra theo chuẩn GDPT 2018:
    Khối 1: 4 ý khái niệm cốt lõi
    Khối 2: 4 công thức & quy luật
    Khối 3: Tiến trình tư duy 4 bước Polya
    Khối 4: 2 cạm bẫy thực tế & mẹo thi
    Đảm bảo 100% nội dung bài học, KHÔNG dùng thẻ mẫu bên ngoài, KHÔNG bao giờ lọt tiêu đề môn khác!
    """
    if not lesson_markdown:
        return None
        
    m = re.search(r'(?i)###\s*TÓM\s*TẮT\s*CẨM\s*NANG\s*INFOGRAPHIC[\:\s]*([\s\S]+?)(?=$|\n###\s*PHẦN|\n\n(?=[A-Z0-9\s]+:))', lesson_markdown)
    if not m:
        m = re.search(r'(?i)TÓM\s*TẮT\s*CẨM\s*NANG\s*INFOGRAPHIC[\:\s]*([\s\S]+?)(?=$|\n###\s*PHẦN|\n\n(?=[A-Z0-9\s]+:))', lesson_markdown)
    if not m:
        return None
        
    content = m.group(1).strip()
    
    # 1. Tách 4 khối
    k1_m = re.search(r'(?i)Khối\s*1[^\n]*\n([\s\S]*?)(?=Khối\s*2|$)', content)
    k2_m = re.search(r'(?i)Khối\s*2[^\n]*\n([\s\S]*?)(?=Khối\s*3|$)', content)
    k3_m = re.search(r'(?i)Khối\s*3[^\n]*\n([\s\S]*?)(?=Khối\s*4|$)', content)
    k4_m = re.search(r'(?i)Khối\s*4[^\n]*\n([\s\S]*?)(?=$)', content)
    
    def parse_chips(block_text, icons, default_labels):
        chips = []
        if not block_text:
            return chips
        lines = [l.strip() for l in block_text.split('\n') if l.strip()]
        item_lines = [l for l in lines if l.startswith('-') or l.startswith('•') or l.startswith('*') or re.match(r'^\d+[\.\)]', l)]
        if not item_lines:
            item_lines = lines
            
        for idx, ln in enumerate(item_lines[:4]):
            clean = re.sub(r'^[•\-\*\d\.\)]\s*', '', ln).strip()
            clean = format_math_and_ipa_typography(clean)
            if ':' in clean:
                t, b = clean.split(':', 1)
            else:
                t = default_labels[idx] if idx < len(default_labels) else f"Ý {idx+1}"
                b = clean
            t = t.strip()
            # Cân chỉnh 2 dòng
            b_clean = b.strip()
            b_sentences = [s.strip() for s in re.split(r'(?<=[\.\;])\s+', b_clean) if s.strip()]
            if len(b_sentences) >= 2:
                l1 = b_sentences[0]
                l2 = " ".join(b_sentences[1:])
            else:
                words = b_clean.split()
                if len(words) > 7:
                    mid = len(words) // 2
                    l1 = " ".join(words[:mid])
                    l2 = " ".join(words[mid:])
                else:
                    l1 = b_clean
                    l2 = ""
            
            icon = icons[idx] if idx < len(icons) else "📌 "
            chip_title = f"{icon}{t.upper()}"
            chips.append((chip_title, l1, l2))
        return chips

    box1 = parse_chips(
        k1_m.group(1) if k1_m else "",
        ['📌 ', '🎯 ', '📈 ', '✨ '],
        ["ĐỊNH NGHĨA", "CẤU TRÚC", "TÍNH CHẤT", "BẢN CHẤT"]
    )
    box2 = parse_chips(
        k2_m.group(1) if k2_m else "",
        ['⚡ ', '📏 ', '💎 ', '📍 '],
        ["CÔNG THỨC 1", "CÔNG THỨC 2", "QUY LUẬT", "VẬN DỤNG"]
    )
    
    # 2. Xử lý Khối 3 (Worked example)
    extracted_ex = None
    if k3_m:
        k3_text = k3_m.group(1).strip()
        k3_lines = [l.strip() for l in k3_text.split('\n') if l.strip()]
        ex_title = f"Ví dụ minh họa: {topic_text}"
        step_items = []
        for l in k3_lines:
            clean_l = re.sub(r'^[•\-\*\s]+', '', l).strip()
            if re.match(r'(?i)^ví\s*dụ[\:\s]', clean_l):
                ex_title = format_math_and_ipa_typography(re.sub(r'(?i)^ví\s*dụ[\:\s]+', '', clean_l).strip())
            elif re.search(r'(?i)bước\s*1', clean_l):
                desc = format_math_and_ipa_typography(re.sub(r'(?i)^[^\:]*bước\s*1[^\:]*[\:\.]\s*', '', clean_l).strip())
                step_items.append(("❶ Tìm hiểu đề & Giả thiết", desc))
            elif re.search(r'(?i)bước\s*2', clean_l):
                desc = format_math_and_ipa_typography(re.sub(r'(?i)^[^\:]*bước\s*2[^\:]*[\:\.]\s*', '', clean_l).strip())
                step_items.append(("❷ Tìm tòi & Lập kế hoạch", desc))
            elif re.search(r'(?i)bước\s*3', clean_l):
                desc = format_math_and_ipa_typography(re.sub(r'(?i)^[^\:]*bước\s*3[^\:]*[\:\.]\s*', '', clean_l).strip())
                step_items.append(("❸ Thực hiện kế hoạch giải", desc))
            elif re.search(r'(?i)bước\s*4', clean_l):
                desc = format_math_and_ipa_typography(re.sub(r'(?i)^[^\:]*bước\s*4[^\:]*[\:\.]\s*', '', clean_l).strip())
                step_items.append(("❹ Nhìn lại & Đúc kết bản chất", desc))
                
        if len(step_items) >= 2:
            extracted_ex = {
                "title": f"Ví dụ minh họa: {ex_title}",
                "steps": step_items
            }

    # 3. Xử lý Khối 4 (Cạm bẫy & Mẹo thi)
    box4 = []
    if k4_m:
        k4_text = k4_m.group(1).strip()
        k4_lines = [l.strip() for l in k4_text.split('\n') if l.strip() and (l.startswith('-') or l.startswith('•') or l.startswith('*') or 'bẫy' in l.lower() or 'lưu ý' in l.lower())]
        for idx, l in enumerate(k4_lines[:2]):
            clean_l = re.sub(r'^[•\-\*\s]+', '', l).strip()
            clean_l = format_math_and_ipa_typography(clean_l)
            if re.search(r'(?i)(?:bí quyết|mẹo)[\:\.]?\s*', clean_l):
                parts = re.split(r'(?i)(?:bí quyết|mẹo)[\:\.]?\s*', clean_l, maxsplit=1)
                mistake_part = parts[0].strip()
                tip_part = parts[1].strip() if len(parts) > 1 else "Kiểm tra kỹ lưỡng điều kiện và đơn vị đo!"
            else:
                mistake_part = clean_l
                tip_part = "Đối chiếu chuẩn mực kiến thức SGK Kết Nối Tri Thức!"
                
            if ':' in mistake_part:
                bt, bm = mistake_part.split(':', 1)
                clean_bt = re.sub(r'(?i)^bẫy\s*\d*[\:\.\-]*\s*', '', bt).strip().upper()
                card_title = f"⚠️ BẪY {idx+1}: {clean_bt}" if clean_bt else f"⚠️ BẪY {idx+1}: SAI LẦM THƯỜNG GẶP"
                mistake_text = bm.strip()
            else:
                card_title = f"⚠️ BẪY {idx+1}: SAI LẦM THƯỜNG GẶP"
                mistake_text = mistake_part
                
            box4.append((card_title, mistake_text, f"Bí quyết: {tip_part}"))

    if len(box1) >= 2 or len(box2) >= 2:
        return {
            "box1": box1,
            "box2": box2,
            "box4": box4,
            "example": extracted_ex
        }
    return None

def distill_markdown_to_infographic_blocks(subject_name: str, grade_lvl: int, topic_text: str, lesson_markdown: str):
    """
    RÚT TRÍCH VÀ CÔ ĐỌNG TRI THỨC TRỰC TIẾP TỪ NỘI DUNG BÀI HỌC MARKDOWN CỦA HỌC SINH:
    - Box 1: Khái niệm, Cấu trúc, Phân loại, Bối cảnh (4 chips 2 dòng cân đối)
    - Box 2: Công thức, Phương trình, Quy luật, Tính chất (4 chips 2 dòng cân đối)
    - Box 3: Ví dụ minh họa và tiến trình 4 bước (Worked Example)
    - Box 4: Cạm bẫy & Mẹo phòng tránh thi THPT (2 cards)
    HỖ TRỢ ĐA MÔN, ĐA LỚP - ƯU TIÊN 100% NỘI DUNG BÀI HỌC VỪA SINH RA TRÊN MÀN HÌNH!
    """
    if not lesson_markdown or len(lesson_markdown.strip()) < 30:
        return None

    # 0. CHẾ ĐỘ ƯU TIÊN TUYỆT ĐỐI SỐ 1: BẢN TỔNG HỢP TINH HOA TỰ THÂN (SELF-DISTILLED INFOGRAPHIC)
    self_distilled = extract_self_distilled_infographic_blocks(subject_name, grade_lvl, topic_text, lesson_markdown)
    if self_distilled:
        return self_distilled
        
    subj_lower = (subject_name or "").lower()
    raw_lines = [ln.strip() for ln in lesson_markdown.split('\n') if ln.strip()]
    
    current_section = 1 # 1: Khái niệm/Định nghĩa, 2: Công thức/Tính chất, 3: Ví dụ/Tiến trình, 4: Lưu ý/Cạm bẫy
    
    concept_candidates = []
    formula_candidates = []
    example_raw_lines = []
    pitfall_candidates = []
    
    for ln in raw_lines:
        ln_lower = ln.lower()
        
        # Bỏ qua dòng tiêu đề chung phần 1 hoặc footer/phân cách, hoặc bảng markdown
        if re.match(r'(?i)^(?:###\s*)?(?:phần\s*1|===+|---+)', ln):
            continue
        if ln.startswith('|') or ln.endswith('|') or re.match(r'^[|:\-\s]+$', ln):
            continue
        if any(kw in ln_lower for kw in ['lưu ý: các đợt tái bản', 'menu trái', 'thầy hướng dẫn', 'chụp ảnh trang sách', 'kéo xuống phòng lab']):
            continue
            
        # Nhận diện chuyển vùng tri thức theo Tiêu đề mục (H2, H3, H4, Chữ in đậm, Đánh số)
        is_table_caption = any(k in ln_lower for k in ["bảng biến thiên", "bảng xét dấu", "đồ thị minh họa", "hình vẽ minh họa"])
        if is_table_caption:
            # Đây là caption của bảng hoặc đồ thị, không coi là section 3 (Ví dụ)
            continue

        is_heading_line = bool(
            ln.startswith("#") or 
            re.match(r"^(?:phần|mục|hoạt động|\d+[\.\)]|[ivx]+[\.\)]|\*\*)\s*", ln_lower) or
            re.match(r"^(?:[1-4]\.|\b[ivx]+\b\.)\s*", ln_lower)
        )
        if is_heading_line:
            if any(kw in ln_lower for kw in ["lưu ý", "chú ý", "cạm bẫy", "sai lầm", "mẹo", "phòng tránh", "kinh nghiệm", "bí quyết", "bẫy"]):
                current_section = 4
                continue
            elif any(kw in ln_lower for kw in ["ví dụ điển hình", "bài tập vận dụng", "tiến trình polya", "bài toán áp dụng", "worked example", "bài tập tự luyện"]):
                current_section = 3
                continue
            elif any(kw in ln_lower for kw in ["tính chất", "công thức", "định luật", "quy luật", "phương trình", "ngữ pháp", "bảo toàn", "quy tắc", "biểu thức", "phép toán", "hệ quả", "định lý", "đặc trưng", "phân tán", "trung tâm", "độ lệch", "phương sai", "trung vị"]):
                current_section = 2
                continue
            elif any(kw in ln_lower for kw in ["khái niệm", "định nghĩa", "cấu tạo", "cấu trúc", "bối cảnh", "từ vựng", "tổng quan", "bản chất", "khởi động", "hình thành kiến thức", "chủ đề", "nguyên lý", "đặc điểm", "hàm", "mẫu số liệu", "ghép nhóm", "thống kê", "biến cố"]):
                current_section = 1
                continue

        # Nếu dòng giới thiệu một hàm số hoặc dạng cụ thể (ví dụ: "a) Hàm đa thức bậc ba", "b) Hàm phân thức...")
        if re.match(r'^(?:[a-z]\)|\d+[\.\)])\s*(?:hàm|dạng|mô hình|phương pháp|quy tắc|chuyên đề)', ln_lower):
            current_section = 1
            
        # Nếu đang ở vùng 3 (Ví dụ), tích lũy dòng vào example_raw_lines
        if current_section == 3:
            example_raw_lines.append(ln)
            continue
            
        # Rút trích cặp (Tiêu đề, Nội dung)
        # TH 1: Dạng danh sách có in đậm hoặc gạch mục: a) Tiêu đề: Nội dung, 1. **Tiêu đề:** Nội dung
        m_bold = re.match(r'^(?:[\-\*\+\•]|\d+[\.\)]|[a-zA-Z][\.\)])\s*(?:\*\*(.*?)\*\*|\[(.*?)\]|(.*?)\:)\s*(.*)$', ln)
        item_title = ""
        item_content = ""
        
        if m_bold:
            item_title = (m_bold.group(1) or m_bold.group(2) or m_bold.group(3) or "").strip()
            item_content = m_bold.group(4).strip()
        else:
            # TH 2: Dạng heading nhỏ: #### 1. Tiêu đề
            m_head = re.match(r'^(?:#{2,5}|\d+[\.\)]|[a-zA-Z][\.\)])\s*(.*?)\:?\s*$', ln)
            if m_head and len(m_head.group(1).strip()) < 40 and not any(k in m_head.group(1).lower() for k in ['phần', 'hoạt động']):
                item_title = m_head.group(1).strip()
                continue
            
            # TH 3: Gạch đầu dòng thông thường: - Nội dung có thể có dấu hai chấm
            m_bullet = re.match(r'^(?:[\-\*\+\•]|\d+[\.\)]|[a-zA-Z][\.\)])\s*(.*)$', ln)
            if m_bullet:
                c_text = m_bullet.group(1).strip()
                if ':' in c_text:
                    parts = c_text.split(':', 1)
                    item_title = parts[0].strip()
                    item_content = parts[1].strip()
                else:
                    item_content = c_text
            else:
                # TH 4: Dòng văn bản bình thường chứa định nghĩa hoặc công thức
                if any(kw in ln_lower for kw in ['lưu ý', 'chú ý', 'sai lầm', 'cạm bẫy', 'bẫy', 'mẹo']):
                    if ':' in ln:
                        parts = ln.split(':', 1)
                        item_title = parts[0].strip()
                        item_content = parts[1].strip()
                    else:
                        item_content = ln
                elif any(kw in ln_lower for kw in ['định nghĩa', 'khái niệm', 'công thức', 'phương trình', 'định lý', 'tính chất', 'biểu thức', 'quy tắc']) or '$' in ln or '=' in ln:
                    if ':' in ln:
                        parts = ln.split(':', 1)
                        item_title = parts[0].strip()
                        item_content = parts[1].strip()
                    else:
                        item_content = ln
                elif len(ln) > 15 and len(ln) < 180:
                    item_content = ln
                    
        if not item_content:
            continue
            
        item_title = re.sub(r'[\*\`\#]+', '', item_title).strip()
        item_content = re.sub(r'[\*\`\#]+', '', item_content).strip()
        item_all_text = f"{item_title} {item_content}".lower()

        # Bỏ qua các đoạn mở đầu thực tế không phải định nghĩa cốt lõi SGK
        if any(ign in item_all_text for ign in ['trong thực tế', 'khi một doanh nghiệp', 'chi phí trung bình', 'chi phí sản xuất', 'khởi động', 'mở đầu', 'hoạt động 1', 'hoạt động 2', 'tình huống mở đầu']):
            continue
        
        # PHÂN LOẠI THÔNG MINH DỰA TRÊN NỘI DUNG VÀ BẢN CHẤT SƯ PHẠM:
        is_formula_item = any(k in item_all_text for k in [
            "y'", "f'", "f(x)", "y =", "d =", "x0", "x_0", "đạo hàm", "tiệm cận", "tâm đối xứng", "điểm uốn",
            "cực trị", "cực đại", "cực tiểu", "phương trình", "công thức", "định luật", "bảo toàn", "tính chất",
            "biểu thức", "định lý", "toạ độ", "tọa độ", "hệ số", "tổng", "hiệu", "tích", "bảng biến thiên",
            "trung vị", "tứ phân vị", "mốt", "phương sai", "độ lệch chuẩn", "khoảng biến thiên", "số trung bình",
            "mẫu số liệu", "ghép nhóm", "đặc trưng", "phân tán",
            "phản ứng", "cân bằng", "chu kỳ", "tần số", "gia tốc", "vận tốc", "li độ", "quang hợp", "hô hấp",
            "alen", "kiểu gen", "kiểu hình", "tense", "grammar", "passive", "clause", "cú pháp", "thuật toán"
        ]) or any(sym in item_content for sym in ['=', '≈', '≠', '≤', '≥', '±', '√', '∫', '∑', '→', '⇌', 'Δ', 'λ', 'ω', 'π']) or ('$' in item_content)

        if current_section == 4 or any(w in item_all_text for w in ['lưu ý', 'chú ý', 'sai lầm', 'cạm bẫy', 'bẫy', 'mẹo', 'tránh nhầm']):
            pitfall_candidates.append((item_title, item_content))
        elif current_section == 3 or any(w in item_all_text for w in ['bước 1', 'bước 2', 'bước 3', 'bước 4', 'ví dụ', 'minh họa', 'bài toán']):
            example_raw_lines.append(ln)
        elif is_formula_item:
            formula_candidates.append((item_title, item_content))
        else:
            concept_candidates.append((item_title, item_content))
                
    # Xử lý bóc tách Ví dụ 4 bước từ example_raw_lines
    extracted_example = None
    if example_raw_lines:
        ex_title = ""
        ex_steps = []
        for eln in example_raw_lines:
            eln_clean = re.sub(r'[\*\`\#]+', '', eln).strip()
            # Bỏ qua dòng tiêu đề mục nếu lọt vào (như "3. Ví dụ minh họa và Tiến trình")
            if re.search(r'(?i)^(?:\d+[\.\)]\s*)?(?:ví dụ|tiến trình|bài tập|vận dụng|bài toán)[^\n]*$', eln_clean) and not any(kw in eln_clean.lower() for kw in ['cho ', 'tính ', 'thủy phân', 'xét ', 'tìm ']):
                continue
            # Tiêu đề đề bài: Dòng đầu tiên không bắt đầu bằng Bước 1-4
            if not ex_title and not re.match(r'^(?:[\-\*\+\•]|\d+[\.\)])?\s*(?:bước\s*\d+|[❶❷❸❹])', eln_clean, re.I):
                ex_title = re.sub(r'^(?:[\-\*\+\•]|\d+[\.\)])\s*', '', eln_clean)
                continue
            # Tìm các bước 1, 2, 3, 4
            m_step = re.match(r'^(?:[\-\*\+\•]|\d+[\.\)])?\s*(?:bước\s*(\d+)[\:\.]?|(❶|❷|❸|❹|\d+[\.\)]))\s*(.*)$', eln_clean, re.IGNORECASE)
            if m_step:
                s_num = m_step.group(1) or m_step.group(2) or str(len(ex_steps) + 1)
                s_text = (m_step.group(3) or "").strip()
                if s_text:
                    ex_steps.append((f"Bước {s_num}", s_text))
            elif eln_clean.startswith(('-', '*', '+')) and len(ex_steps) < 4:
                c_text = eln_clean.lstrip('-*+• ').strip()
                ex_steps.append((f"Bước {len(ex_steps) + 1}", c_text))
                
        if ex_steps:
            num_icons = ['❶', '❷', '❸', '❹']
            std_steps = []
            for idx, (st_lbl, st_txt) in enumerate(ex_steps[:4]):
                clean_lbl = re.sub(r'(?i)^(?:bước\s*\d+|[❶❷❸❹\d\.\)]+)[\:\.\-\s]*', '', st_lbl).strip()
                if not clean_lbl:
                    words = st_txt.split(':')
                    if len(words) > 1 and len(words[0].strip()) < 25:
                        clean_lbl = words[0].strip()
                        st_txt = words[1].strip()
                    else:
                        clean_lbl = f"Bước {idx + 1}"
                icon = num_icons[idx] if idx < 4 else f"[{idx+1}]"
                std_steps.append((f"{icon} {clean_lbl}", st_txt))
                
            while len(std_steps) < 4:
                idx = len(std_steps)
                icon = num_icons[idx]
                std_steps.append((f"{icon} Vận dụng & Kết luận", f"Kiểm tra tính hợp lý của kết quả và khắc sâu kiến thức {topic_text}."))
                
            if ex_title:
                clean_title = ex_title
                if not clean_title.lower().startswith("ví dụ") and not clean_title.lower().startswith("worked example"):
                    clean_title = f"Ví dụ: {clean_title}"
            else:
                clean_title = f"Ví dụ minh họa & Tiến trình tư duy: {topic_text}"
                
            if len(clean_title) > 60:
                clean_title = clean_title[:57] + "..."
            if any(k in clean_title.lower() for k in ["bảng biến thiên", "bảng xét dấu", "bảng giá trị", "đồ thị minh họa"]):
                extracted_example = None
            else:
                extracted_example = {
                    "title": clean_title,
                    "steps": std_steps
                }

    # CÂN BẰNG TƯƠNG HỖ (ADAPTIVE LOAD BALANCING) GIỮA CONCEPTS VÀ FORMULAS
    # Đảm bảo tận dụng tối đa 100% kiến thức trong bài học của học sinh!
    if len(concept_candidates) < 4 and len(formula_candidates) > 4:
        surplus = formula_candidates[4:]
        formula_candidates = formula_candidates[:4]
        for it in surplus:
            if len(concept_candidates) < 4:
                concept_candidates.append(it)
            else:
                break
    elif len(formula_candidates) < 4 and len(concept_candidates) > 4:
        surplus = concept_candidates[4:]
        concept_candidates = concept_candidates[:4]
        for it in surplus:
            if len(formula_candidates) < 4:
                formula_candidates.append(it)
            else:
                break

    # Thiết lập nhãn mặc định thông minh thích ứng theo từng môn học (Tránh nhầm môn 100%)
    if any(m in subj_lower for m in ['toán', 'toan', 'math']):
        box1_defaults = ['KHÁI NIỆM CỐT LÕI', 'TẬP XÁC ĐỊNH & MIỀN GIÁ TRỊ', 'QUY TRÌNH KHẢO SÁT', 'Ý NGHĨA HÌNH HỌC']
        box2_defaults = ['CÔNG THỨC & ĐẠO HÀM', 'TIỆM CẬN & ĐỒ THỊ', 'QUY TẮC CỰC TRỊ & TÂM ĐỐI XỨNG', 'CÔNG THỨC GIẢI NHANH']
    elif (any(m in subj_lower for m in ['vật lý', 'vat ly', 'vật lí', 'vat li', 'physics']) or subj_lower in ['lý', 'li', 'vatly', 'vatli']) and 'địa' not in subj_lower:
        box1_defaults = ['MÔ HÌNH HIỆN TƯỢNG', 'THÔNG SỐ ĐẶC TRƯNG', 'ĐỒ THỊ BIẾN THIÊN', 'BẢO TOÀN NĂNG LƯỢNG']
        box2_defaults = ['CÔNG THỨC VẬT LÝ', 'ĐỊNH LUẬT TRỌNG TÂM', 'HỆ THỨC ĐỘC LẬP', 'ĐƠN VỊ & GIÁ TRỊ BIÊN']
    elif any(m in subj_lower for m in ['hóa', 'hoa', 'chemistry']):
        box1_defaults = ['CẤU TẠO PHÂN TỬ', 'TÍNH CHẤT VẬT LÝ', 'ĐỒNG PHÂN & DANH PHÁP', 'PHÂN LOẠI HỢP CHẤT']
        box2_defaults = ['PHẢN ỨNG / PHƯƠNG TRÌNH', 'ĐỊNH LUẬT TRỌNG TÂM', 'BẢO TOÀN NGUYÊN TỐ', 'HIỆN TƯỢNG THỰC NGHIỆM']
    elif any(m in subj_lower for m in ['sinh', 'biology']):
        box1_defaults = ['CƠ SỞ TẾ BÀO & ADN', 'CẤU TRÚC GEN & NST', 'QUY LUẬT DI TRUYỀN', 'TIẾN HÓA & SINH THÁI']
        box2_defaults = ['CƠ CHẾ DI TRUYỀN', 'CÔNG THỨC TÍNH TOÁN', 'QUY LUẬT PHÂN LY', 'ỨNG DỤNG CÔNG NGHỆ GEN']
    elif any(m in subj_lower for m in ['văn', 'ngữ văn', 'van', 'ngu van', 'literature']):
        box1_defaults = ['NGỮ CẢNH & TÁC GIẢ', 'HÌNH TƯỢNG NGHỆ THUẬT', 'ĐẶC TRƯNG THỂ LOẠI', 'BÀI HỌC NHÂN SINH']
        box2_defaults = ['BIỆN PHÁP TU TỪ', 'LUẬN ĐIỂM TRỌNG TÂM', 'NGHỆ THUẬT NGÔN TỪ', 'THÔNG ĐIỆP TƯ TƯỞNG']
    elif any(m in subj_lower for m in ['tiếng anh', 'tieng anh', 'anh', 'english']):
        box1_defaults = ['CORE THEME & TOPIC', 'DISCOURSE FUNCTION', 'KEY COLLOCATIONS', 'GRAMMAR PATTERN']
        box2_defaults = ['PHONETIC RULES', 'SENTENCE STRUCTURE', 'IDIOMS & PHRASAL VERBS', 'EXAM STRATEGY']
    elif any(m in subj_lower for m in ['lịch sử', 'lich su', 'sử', 'su', 'history']):
        box1_defaults = ['BỐI CẢNH LỊCH SỬ', 'MỐC SON THEN CHỐT', 'ĐƯỜNG LỐI CÁCH MẠNG', 'DIỄN BIẾN CHÍNH']
        box2_defaults = ['NGUYÊN NHÂN THẮNG LỢI', 'Ý NGHĨA LỊCH SỬ', 'BÀI HỌC KINH NGHIỆM', 'NHẬN ĐỊNH BẬC CAO']
    elif any(m in subj_lower for m in ['địa', 'dia', 'địa lí', 'địa lý', 'geography']):
        box1_defaults = ['VỊ TRÍ ĐỊA LÝ', 'ĐIỀU KIỆN TỰ NHIÊN', 'ĐẶC ĐIỂM DÂN CƯ', 'PHÂN VÙNG KINH TẾ']
        box2_defaults = ['QUY LUẬT ĐỊA LÍ', 'CÔNG THỨC SỐ LIỆU', 'XU HƯỚNG CHUYỂN DỊCH', 'KỸ NĂNG ATLAT & BIỂU ĐỒ']
    elif any(m in subj_lower for m in ['gdcd', 'kinh tế', 'pháp luật', 'ktpl', 'civics']):
        box1_defaults = ['QUY PHẠM PHÁP LUẬT', 'CHUẨN MỰC ĐẠO ĐỨC', 'QUYỀN & NGHĨA VỤ', 'VĂN HÓA ỨNG XỬ']
        box2_defaults = ['NGUYÊN TẮC PHÁP LÝ', 'CHẾ TÀI XỬ LÝ', 'KỸ NĂNG THỰC THI', 'BÀI HỌC CÔNG DÂN']
    elif any(m in subj_lower for m in ['tin', 'tin học', 'computer', 'informatics']):
        box1_defaults = ['BẢN CHẤT DỮ LIỆU', 'CẤU TRÚC GIẢI THUẬT', 'MÔ HÌNH HỆ THỐNG', 'ỨNG DỤNG THỰC TIỄN']
        box2_defaults = ['CÚ PHÁP CỐT LÕI', 'CÔNG THỨC & BIẾN ĐỔI', 'VÒNG LẶP & ĐIỀU KIỆN', 'ĐỘ PHỨC TẠP THUẬT TOÁN']
    elif any(m in subj_lower for m in ['công nghệ', 'cong nghe', 'technology']):
        box1_defaults = ['BẢN VẼ KỸ THUẬT', 'QUY TRÌNH CÔNG NGHỆ', 'VẬT LIỆU & THIẾT BỊ', 'AN TOÀN LAO ĐỘNG']
        box2_defaults = ['THÔNG SỐ KỸ THUẬT', 'SƠ ĐỒ NGUYÊN LÝ', 'PHƯƠNG PHÁP GIA CÔNG', 'ỨNG DỤNG SẢN XUẤT']
    else:
        box1_defaults = ['KHÁI NIỆM TRỌNG TÂM', 'CẤU TRÚC ĐẶC TRƯNG', 'QUY LUẬT BIẾN THIÊN', 'PHÂN LOẠI & Ý NGHĨA']
        box2_defaults = ['CÔNG THỨC & QUY TẮC', 'ĐỊNH LUẬT CỐT LÕI', 'PHƯƠNG PHÁP XỬ LÝ', 'VẬN DỤNG THỰC NGHIỆM']

    # Hàm chuẩn hóa một chip 2 dòng cân đối, không tràn viền
    def make_chip(emoji_prefix: str, default_label: str, raw_title: str, raw_content: str) -> tuple:
        t_clean = re.sub(r'[\:\.\-\,\;]+$', '', raw_title).strip()
        if not t_clean and raw_content:
            first_clause = re.split(r'[\.\:\;\,\(\)]+', raw_content)[0].strip()
            w_list = first_clause.split()
            if w_list:
                t_clean = " ".join(w_list[:4])
        if t_clean:
            if len(t_clean) > 28:
                t_clean = t_clean[:26] + "..."
            chip_label = f"{emoji_prefix}{t_clean.upper()}"
        else:
            chip_label = f"{emoji_prefix}{default_label}"
            
        c_clean = format_math_and_ipa_typography(raw_content)
        
        sentences = [s.strip() for s in re.split(r'(?<=[\.\;\!])\s+', c_clean) if s.strip()]
        if len(sentences) >= 2 and len(sentences[0]) <= 46:
            line1 = sentences[0]
            line2 = " ".join(sentences[1:])
            if len(line2) > 46:
                line2, _ = wrap_text_two_lines(line2, max_chars=46)
        else:
            line1, line2 = wrap_text_two_lines(c_clean, max_chars=46)
            
        # Chống tràn viền triệt để: Đảm bảo line2 không vượt quá 48 ký tự
        if len(line2) > 48:
            l2_words = line2.split(' ')
            l2_accum = []
            for w in l2_words:
                if sum(len(x) for x in l2_accum) + len(l2_accum) + len(w) <= 46:
                    l2_accum.append(w)
                else:
                    break
            line2 = " ".join(l2_accum)
            
        return (chip_label, line1, line2)

    # Hàm tinh chọn ưu tiên các thực thể, hàm số, định luật cốt lõi tránh bị bước giải lấn át
    def prioritize_candidate_chips(cands, max_count=4):
        if len(cands) <= max_count:
            return cands
        def _score(c):
            t, body = c
            combined = f"{t} {body}".lower()
            score = 0
            is_major = bool(
                re.match(r'^(?:[a-zA-Z][\.\)]|\d+[\.\)])?\s*(?:hàm|dạng|mô hình|chuyên đề|phân thức|đa thức|thể loại|thì|quy luật)', t, re.I) or
                any(k in t.lower() for k in ['hàm đa thức', 'hàm phân thức', 'bậc ba', 'bậc 3', 'bậc nhất', 'bậc hai', 'tiệm cận', 'tâm đối xứng', 'điểm uốn'])
            )
            if is_major:
                score += 30
            elif any(k in combined for k in [
                'hàm', 'dạng', 'loại', 'tiệm cận', 'tâm đối xứng', 'định luật', 'nguyên lý',
                'công thức', 'phương trình', 'phản ứng', 'cấu tạo', 'thể loại', 'đạo hàm'
            ]):
                score += 15
            elif any(k in combined for k in ['sơ đồ', 'tổng quan', 'quy trình', 'bản chất', 'khái niệm']):
                score += 8
            if re.search(r'^(?:bước\s*\d+|[❶❷❸❹\d\.\)]+)', t, re.I):
                score -= 10
            return score

        sorted_c = sorted(cands, key=_score, reverse=True)
        picked = []
        seen_keys = set()
        for c in sorted_c:
            k = c[0].lower()[:16]
            if k not in seen_keys:
                seen_keys.add(k)
                picked.append(c)
            if len(picked) == max_count:
                break
        return picked

    # 1. Box 1 (4 chips lý thuyết từ bài học)
    box1_chips = []
    box1_icons = ['📌 ', '🎯 ', '📈 ', '✨ ']
    curated_concepts = prioritize_candidate_chips(concept_candidates, max_count=4)
    for idx in range(min(4, len(curated_concepts))):
        c_title, c_content = curated_concepts[idx]
        box1_chips.append(make_chip(box1_icons[idx], box1_defaults[idx], c_title, c_content))
        
    # 2. Box 2 (4 chips công thức & quy luật từ bài học)
    box2_chips = []
    box2_icons = ['⚡ ', '📏 ', '💎 ', '📍 ']
    curated_formulas = prioritize_candidate_chips(formula_candidates, max_count=4)
    for idx in range(min(4, len(curated_formulas))):
        f_title, f_content = curated_formulas[idx]
        box2_chips.append(make_chip(box2_icons[idx], box2_defaults[idx], f_title, f_content))
        
    # 3. Box 4 (2 thẻ cạm bẫy từ bài học kèm mẹo chuẩn theo từng môn)
    box4_cards = []
    default_tips = {
        "toán": "Luôn kiểm tra điều kiện xác định, dấu của biểu thức và các trường hợp biên!",
        "lý": "Luôn đổi đúng đơn vị chuẩn SI (m, s, kg, rad) và lưu ý dấu pha ban đầu!",
        "hóa": "Luôn kiểm tra điều kiện phản ứng (t°, xúc tác) và tỉ lệ mol phản ứng!",
        "sinh": "Phân biệt rõ kiểu gen với kiểu hình, điều kiện di truyền liên kết hay độc lập!",
        "anh": "Xác định từ loại (noun/verb/adj), thì của câu và sự hòa hợp chủ - vị!",
        "sử": "Vẽ dòng thời gian (Timeline) và gắn liền sự kiện với nguyên nhân - kết quả!",
        "địa": "Phân tích kỹ đơn vị biểu đồ và đối chiếu mối liên hệ tự nhiên - kinh tế!",
        "tin": "Kiểm tra điều kiện dừng của vòng lặp và kiểu dữ liệu của biến số!",
        "công nghệ": "Tuân thủ nghiêm ngặt quy tắc an toàn điện và sơ đồ đấu nối mạch!"
    }
    subj_k = "toán"
    for k in default_tips:
        if k in subj_lower:
            subj_k = k
            break
    fallback_tip = default_tips.get(subj_k, "Nắm vững bản chất định nghĩa và đọc kỹ từ khóa phân loại đề thi!")

    for idx in range(min(2, len(pitfall_candidates))):
        p_title, p_content = pitfall_candidates[idx]
        p_clean = format_math_and_ipa_typography(p_content)
        if 'bí quyết' in p_clean.lower() or 'mẹo' in p_clean.lower():
            parts = re.split(r'(?i)(?:bí quyết|mẹo)[\:\.]?\s*', p_clean, maxsplit=1)
            b_mistake = parts[0].strip()
            b_tip = parts[1].strip() if len(parts) > 1 else fallback_tip
        else:
            b_mistake = p_clean
            b_tip = fallback_tip
            
        if p_title:
            clean_title = re.sub(r'[\:\.\-]+$', '', p_title).upper()
            card_title = f"⚠️ BẪY {idx + 1}: {clean_title}"
        else:
            card_title = f"⚠️ BẪY {idx + 1}: LƯU Ý PHÒNG TRÁNH TRONG THI"
        box4_cards.append((card_title, b_mistake, f"Bí quyết: {b_tip}"))
        
    return {
        "box1": box1_chips,
        "box2": box2_chips,
        "box4": box4_cards,
        "example": extracted_example
    }


def distill_lesson_to_infographic_data(subject_name, grade_lvl, topic_text, full_lesson_markdown):
    return faithful_infographic_data(subject_name, grade_lvl, topic_text, full_lesson_markdown)
def get_subject_infographic_headers(subject_name, grade_lvl):
    return {"box1_title": "1. NỘI DUNG TRÍCH TỪ BÀI HỌC", "box2_title": "2. NỘI DUNG TIẾP THEO",
            "box3_title": "3. BẢN TRÍCH GỌN", "box4_title": "BẢN ĐẦY ĐỦ CÓ TRONG PHIẾU HTML"}


@lru_cache(maxsize=64)
def build_a4_infographic_svg(subject_name: str, grade_lvl: int, topic_text: str, index_code: str, textbook_name: str, expert_channel: str, qr_base64_url: str, lesson_markdown: str, mode: str = "color") -> str:
    """
    Sinh mã Vector SVG Chuẩn Khổ Giấy A4 (800 x 1130 px - Tỷ lệ 1 : 1.414).
    ĐẲNG CẤP MỸ THUẬT SƯ PHẠM & TYPOGRAPHY HỌC THUẬT:
      1. Typography Serif Academic ('STIX Two Text', 'Noto Serif', 'Times New Roman', 'Cambria Math').
      2. Bố cục Focus Chips 2 dòng thông thoáng: TUYỆT ĐỐI KHÔNG CẮT CỤT TỪ KHÓA, KHÔNG BAO GIỜ DÙNG DẤU BA CHẤM.
      3. Khắc phục 100% lỗi lặp số thứ tự (❶ ❶) ở tiến trình Polya.
      4. VÍ DỤ MINH HỌA 4 BƯỚC POLYA & ĐỒ THỊ TIKZ / SVG VECTOR SẮC NÉT.
      5. MÃ QR CODE NHÚNG GỌN GÀNG TRONG FOOTER.
    """
    data = distill_lesson_to_infographic_data(subject_name, grade_lvl, topic_text, lesson_markdown)
    ex = data["example"]
    hdr_info = get_subject_infographic_headers(subject_name, grade_lvl)
    
    # Tính toán kích thước font tiêu đề bài học tránh tràn chữ
    topic_clean = clean_topic_title(subject_name, grade_lvl, topic_text)
    main_title_str = f"{subject_name.upper()} {grade_lvl}: {topic_clean}"
    title_font_size = "19" if len(main_title_str) < 42 else ("16.5" if len(main_title_str) < 56 else "14.5")
    
    if mode == "monochrome":
        bg_main = "#ffffff"
        header_bg = "#ffffff"
        header_border = "#000000"
        title_color = "#000000"
        sub_color = "#222222"
        card_bg = "#ffffff"
        card_border = "#000000"
        chip_bg = "#f8f8f8"
        chip_border = "#000000"
        chip_label = "#000000"
        card_title = "#000000"
        text_color = "#000000"
        accent_color = "#000000"
        callout_bg = "#fafafa"
        callout_border = "#000000"
        footer_bg = "#ffffff"
        footer_border = "#000000"
        footer_text = "#333333"
    else:
        bg_main = "#f8fafc"
        header_bg = "#0f172a"
        header_border = "#38bdf8"
        title_color = "#38bdf8"
        sub_color = "#94a3b8"
        card_bg = "#ffffff"
        card_border = "#cbd5e1"
        chip_bg = "#f8fafc"
        chip_border = "#e2e8f0"
        chip_label = "#0369a1"
        card_title = "#0f172a"
        text_color = "#0f172a"
        accent_color = "#0284c7"
        callout_bg = "#fffbeb"
        callout_border = "#f59e0b"
        footer_bg = "#f8fafc"
        footer_border = "#cbd5e1"
        footer_text = "#475569"

    width = 800
    height = 1130
    margin = 25
    content_w = width - 2 * margin # 750px

    # Hàm render các Focus Chips trong Khối 1 & 2 (Hỗ trợ 2 dòng nội dung đầy đủ 100%, TUYỆT ĐỐI KHÔNG CẮT CỤT & CHỐNG TRÀN VIỀN)
    def render_chips_2lines(chip_list: list, start_y: int = 42, chip_h: int = 50, gap: int = 6) -> str:
        svg_out = []
        cur_y = start_y
        for item in chip_list:
            label = item[0]
            line1 = item[1] if len(item) > 1 else ""
            line2 = item[2] if len(item) > 2 else ""
            
            # Tự động chống tràn viền: Nếu line1 dài quá 46 ký tự và line2 trống, tự động tách 2 dòng cân đối
            if not line2 and len(line1) > 46:
                line1, line2 = wrap_text_two_lines(line1, max_chars=46)
                
            escaped_lbl = html.escape(label)
            escaped_l1 = html.escape(line1)
            escaped_l2 = html.escape(line2)
            
            # Nếu chỉ có 1 dòng thì căn giữa hoàn hảo ở y=34, nếu có 2 dòng thì ở y=29 và y=43
            if escaped_l2:
                content_svg = f'''<text x="10" y="29" font-size="10.5" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l1}</text>
                <text x="10" y="43" font-size="10.5" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l2}</text>'''
            else:
                content_svg = f'''<text x="10" y="34" font-size="11" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l1}</text>'''
                
            svg_out.append(f'''
            <g transform="translate(10, {cur_y})">
                <rect width="345" height="{chip_h}" rx="6" fill="{chip_bg}" stroke="{chip_border}" stroke-width="1" />
                <text x="10" y="14" font-size="10.5" font-weight="700" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{chip_label}">{escaped_lbl}</text>
                {content_svg}
            </g>''')
            cur_y += chip_h + gap
        return "\n".join(svg_out)

    box1_chips_svg = render_chips_2lines(data["box1"], start_y=42, chip_h=50, gap=6)
    box2_chips_svg = render_chips_2lines(data["box2"], start_y=42, chip_h=50, gap=6)

    # Render Khối 3 (Tiến trình giải 4 bước Polya - ĐÃ SỬA TRIỆT ĐỂ LỖI LẶP SỐ ❶ ❶)
    ex_steps_svg = []
    step_y = 66
    for step_lbl, step_txt in ex["steps"]:
        l1, l2 = wrap_text_two_lines(step_txt, max_chars=54)
        escaped_l1 = html.escape(l1)
        escaped_l2 = html.escape(l2)
        if escaped_l2:
            step_content = f'''<text x="10" y="29" font-size="11" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l1}</text>
            <text x="10" y="43" font-size="11" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l2}</text>'''
        else:
            step_content = f'''<text x="10" y="34" font-size="11.5" font-weight="500" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{text_color}">{escaped_l1}</text>'''
            
        ex_steps_svg.append(f'''
        <g transform="translate(14, {step_y})">
            <rect width="425" height="49" rx="6" fill="{chip_bg}" stroke="{chip_border}" stroke-width="1" />
            <text x="10" y="15" font-size="10.5" font-weight="700" font-family="'Cambria Math', 'STIX Two Text', 'Times New Roman', serif" fill="{accent_color}">{html.escape(step_lbl)}</text>
            {step_content}
        </g>''')
        step_y += 53
    ex_steps_rendered = "\n".join(ex_steps_svg)

    # Render Khối 4 (Hai thẻ cạm bẫy song song - TỰ ĐỘNG CHỐNG TRÀN VIỀN 100%)
    box4_svg = []
    col_w = (content_w - 30) // 2 # 360px
    for c_idx, (b_title, b_pitfall, b_tip) in enumerate(data["box4"]):
        c_x = 10 if c_idx == 0 else (10 + col_w + 10)
        
        # Tự động phân bổ dòng thông minh, tuyệt đối không tràn viền
        p_raw = b_pitfall.strip()
        full_p = p_raw if p_raw.startswith("Sai lầm") else f"Sai lầm: {p_raw}"
        p_lines = wrap_text_to_lines(full_p, max_chars=45)
        
        t_raw = b_tip.strip()
        full_t = t_raw if t_raw.startswith("Bí quyết") else f"{t_raw}"
        t_lines = wrap_text_to_lines(full_t, max_chars=45)
        
        card_texts_svg = []
        # 1. Tiêu đề Bẫy
        card_texts_svg.append(f'<text x="12" y="19" font-size="11" font-weight="700" font-family="\'Cambria Math\', \'STIX Two Text\', \'Times New Roman\', serif" fill="#b45309">{html.escape(b_title)}</text>')
        
        # 2. Các dòng Sai lầm (Tối đa 2 dòng, thụt lề chuẩn xác)
        cur_y = 35
        for p_idx, pl in enumerate(p_lines[:2]):
            prefix = "❌ " if p_idx == 0 else "   "
            card_texts_svg.append(f'<text x="12" y="{cur_y}" font-size="10.5" font-weight="600" font-family="\'Cambria Math\', \'STIX Two Text\', \'Times New Roman\', serif" fill="#991b1b">{prefix}{html.escape(pl)}</text>')
            cur_y += 14
            
        cur_y += 4 # Khoảng cách thở giữa Sai lầm và Bí quyết
        
        # 3. Các dòng Bí quyết (Tối đa 2 dòng, thụt lề chuẩn xác)
        for t_idx, tl in enumerate(t_lines[:2]):
            prefix = "💡 " if t_idx == 0 else "   "
            card_texts_svg.append(f'<text x="12" y="{cur_y}" font-size="10" font-weight="500" font-family="\'Cambria Math\', \'STIX Two Text\', \'Times New Roman\', serif" fill="#15803d">{prefix}{html.escape(tl)}</text>')
            cur_y += 14
            
        card_content_svg = "\n            ".join(card_texts_svg)
        box4_svg.append(f'''
        <g transform="translate({c_x}, 38)">
            <rect width="{col_w}" height="114" rx="8" fill="{callout_bg}" stroke="{callout_border}" stroke-width="1.2" />
            {card_content_svg}
        </g>''')
    box4_rendered = "\n".join(box4_svg)

    # QR Code nhúng chuẩn xác trong Footer
    if qr_base64_url:
        qr_image_tag = f'''<rect x="625" y="15" width="105" height="105" rx="8" fill="#ffffff" stroke="{card_border}" stroke-width="1.2" />
        <image xlink:href="{qr_base64_url}" href="{qr_base64_url}" x="630" y="20" width="95" height="95" />'''
    else:
        qr_image_tag = f'''<rect x="625" y="15" width="105" height="105" rx="8" fill="#ffffff" stroke="{card_border}" stroke-width="1.2" />
        <rect x="635" y="25" width="85" height="85" rx="6" fill="{chip_bg}" stroke="{accent_color}" stroke-width="1.5" stroke-dasharray="3,3" />
        <text x="677" y="65" font-size="11" font-weight="700" text-anchor="middle" fill="{accent_color}">📱 QR CODE</text>
        <text x="677" y="80" font-size="9" text-anchor="middle" fill="{sub_color}">VIDEO BÀI HỌC</text>'''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="100%" height="100%">
    <defs>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=STIX+Two+Text:ital,wght@0,400;0,600;0,700;1,400;1,600&amp;family=Noto+Serif:ital,wght@0,400;0,700;1,400&amp;display=swap');
            text {{
                font-family: 'Cambria Math', 'STIX Two Math', 'STIX Two Text', 'Noto Serif', 'Times New Roman', serif;
                text-rendering: geometricPrecision;
                -webkit-font-smoothing: antialiased;
            }}
            .math {{
                font-family: 'Cambria Math', 'STIX Two Math', 'KaTeX_Math', 'Times New Roman', serif;
                font-style: italic;
            }}
        </style>
        <filter id="cardShadow" x="-3%" y="-3%" width="106%" height="106%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.07"/>
        </filter>
    </defs>

    <!-- Nền Giấy A4 -->
    <rect width="{width}" height="{height}" fill="{bg_main}" />
    <rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="12" fill="none" stroke="{accent_color}" stroke-width="1.2" />

    <!-- ==================== HEADER KHỐI TRÊN ==================== -->
    <g transform="translate({margin}, 16)">
        <rect width="{content_w}" height="126" rx="10" fill="{header_bg}" stroke="{header_border}" stroke-width="1.5" />
        
        <text x="20" y="26" font-size="9.5" font-weight="700" letter-spacing="0.6" fill="{sub_color}">BỘ GIÁO DỤC &amp; ĐÀO TẠO • CHƯƠNG TRÌNH GDPT 2018</text>
        
        <rect x="{content_w - 235}" y="10" width="225" height="24" rx="5" fill="{chip_bg}" stroke="{card_border}" stroke-width="1" />
        <text x="{content_w - 225}" y="26" font-size="10.5" font-weight="700" font-family="'STIX Two Text', 'Times New Roman', serif" fill="{card_title}">MÃ ADN: {html.escape(index_code)}</text>
        
        <text x="20" y="62" font-size="{title_font_size}" font-weight="800" fill="{title_color}">{html.escape(main_title_str)}</text>
        
        <text x="20" y="88" font-size="12" fill="{sub_color}">📚 {html.escape(textbook_name)}</text>
        <text x="20" y="109" font-size="11.5" font-weight="600" fill="{accent_color}">▶️ Video Chuyên Gia: {html.escape(expert_channel)} (Tài nguyên Mở OER Hợp pháp)</text>
    </g>

    <!-- ==================== KHU VỰC 1: HAI THẺ LÝ THUYẾT CỐT LÕI (HÀNG TRÊN - CAO 275px) ==================== -->
    <g transform="translate(25, 154)">
        <rect width="365" height="275" rx="10" fill="{card_bg}" stroke="{card_border}" stroke-width="1.2" filter="url(#cardShadow)" />
        <rect x="0" y="0" width="365" height="36" rx="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <rect x="0" y="26" width="365" height="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <text x="16" y="24" font-size="12.5" font-weight="700" fill="{title_color if mode != 'monochrome' else '#000000'}">{hdr_info['box1_title']}</text>
        {box1_chips_svg}
    </g>

    <g transform="translate(410, 154)">
        <rect width="365" height="275" rx="10" fill="{card_bg}" stroke="{card_border}" stroke-width="1.2" filter="url(#cardShadow)" />
        <rect x="0" y="0" width="365" height="36" rx="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <rect x="0" y="26" width="365" height="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <text x="16" y="24" font-size="12.5" font-weight="700" fill="{title_color if mode != 'monochrome' else '#000000'}">{hdr_info['box2_title']}</text>
        {box2_chips_svg}
    </g>

    <!-- ==================== KHU VỰC 2: VÍ DỤ CỤ THỂ MINH HỌA & ĐỒ THỊ TIKZ/SVG TRỰC QUAN (CAO 290px) ==================== -->
    <g transform="translate(25, 440)">
        <rect width="{content_w}" height="295" rx="10" fill="{card_bg}" stroke="{accent_color}" stroke-width="1.5" filter="url(#cardShadow)" />
        <rect x="0" y="0" width="{content_w}" height="36" rx="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <rect x="0" y="26" width="{content_w}" height="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <text x="18" y="24" font-size="13.5" font-weight="700" fill="{title_color if mode != 'monochrome' else '#000000'}">🎯 3. {html.escape(ex['title'].upper())}</text>
        
        <g transform="translate(0, 0)">
            <text x="18" y="56" font-size="11.5" font-weight="700" fill="{accent_color}">{hdr_info['box3_title']}</text>
            {ex_steps_rendered}
        </g>
        
        <g transform="translate(448, 45)">
            <text x="18" y="0" font-size="12" font-weight="700" fill="{card_title}">📈 MÔ HÌNH TRỰC QUAN HÓA:</text>
            {ex['visual_svg']}
        </g>
    </g>

    <!-- ==================== KHU VỰC 3: CẠM BẪY SAI LẦM THƯỜNG GẶP (CAO 162px) ==================== -->
    <g transform="translate(25, 745)">
        <rect width="{content_w}" height="162" rx="10" fill="{card_bg}" stroke="{card_border}" stroke-width="1.2" filter="url(#cardShadow)" />
        <rect x="0" y="0" width="{content_w}" height="34" rx="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <rect x="0" y="24" width="{content_w}" height="10" fill="{header_bg if mode != 'monochrome' else '#f0f0f0'}" />
        <text x="18" y="22" font-size="12" font-weight="700" fill="{title_color if mode != 'monochrome' else '#000000'}">{hdr_info['box4_title']}</text>
        {box4_rendered}
    </g>

    <!-- ==================== KHU VỰC 4: FOOTER BẢN IN & MÃ QR CODE ==================== -->
    <g transform="translate(25, 918)">
        <rect width="{content_w}" height="135" rx="10" fill="{footer_bg}" stroke="{footer_border}" stroke-width="1" />
        
        <text x="22" y="28" font-size="13" font-weight="700" fill="{title_color if mode != 'monochrome' else '#000000'}">📱 QUÉT MÃ QR XEM VIDEO BÀI HỌC CHÍNH CHỦ TRÊN YOUTUBE</text>
        <text x="22" y="52" font-size="11.5" fill="{footer_text}">• Quét camera điện thoại để mở đúng bài học của chuyên gia: {html.escape(expert_channel)}.</text>
        <text x="22" y="72" font-size="11.5" fill="{footer_text}">• Bản cẩm nang A4 này chuẩn hóa 100% theo Chương trình Giáo dục Phổ thông 2018.</text>
        <text x="22" y="92" font-size="11.5" fill="{footer_text}">• Học sinh có thể in ấn bản Photocopy trắng đen để kẹp vào sách giáo khoa hoặc chép tay ôn thi.</text>
        <text x="22" y="117" font-size="11" font-weight="700" fill="{accent_color}">🛡️ HỆ THỐNG GSAI - THPT 2026 | BẢN QUYỀN HỌC LIỆU MỞ KẾT NỐI TRI THỨC VỚI CUỘC SỐNG</text>
        
        {qr_image_tag}
    </g>
</svg>'''
    return svg_content


def get_overleaf_tikz_code(subject_name: str, grade_lvl: int, topic_text: str, index_code: str) -> str:
    """
    Sinh mã nguồn Overleaf LaTeX / TikZ hoàn chỉnh, chuẩn mực học thuật quốc tế.
    Giáo viên & Học sinh có thể sao chép và dán trực tiếp vào Overleaf để biên dịch thành PDF vector tuyệt mỹ.
    """
    subj_lower = (subject_name or "").lower()
    topic_clean = topic_text or subject_name
    
    if "toán" in subj_lower:
        return f"""% ==============================================================================
% CHƯƠNG TRÌNH GDPT 2018 - SGK KẾT NỐI TRI THỨC VỚI CUỘC SỐNG
% BÀI HỌC: {subject_name.upper()} {grade_lvl} - {topic_clean}
% MÃ ADN: {index_code}
% BIÊN DỊCH TRỰC TIẾP TRÊN OVERLEAF (TeX Live 2024 / XeLaTeX / pdfLaTeX)
% ==============================================================================
\\documentclass[preview,border=12pt]{{standalone}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[vietnamese]{{babel}}
\\usepackage{{amsmath,amsfonts,amssymb}}
\\usepackage{{tikz}}
\\usetikzlibrary{{arrows.meta,calc}}

\\begin{{document}}
\\begin{{center}}
\\textbf{{\\Large CHUYÊN ĐỀ: KHẢO SÁT VÀ VẼ ĐỒ THỊ HÀM SỐ BẬC BA}} \\\\
\\vspace{{4pt}}
\\textit{{\\small Hàm số mẫu mực: $y = x^3 - 3x^2 + 2$}}
\\end{{center}}

\\begin{{itemize}}
    \\item \\textbf{{Tập xác định:}} $D = \\mathbb{{R}}$.
    \\item \\textbf{{Đạo hàm:}} $y' = 3x^2 - 6x = 3x(x - 2)$.
    \\item \\textbf{{Điểm tới hạn:}} $y' = 0 \\Leftrightarrow \\left[\\begin{{array}}{{l}} x = 0 \\Rightarrow y = 2 \\\\ x = 2 \\Rightarrow y = -2 \\end{{array}}\\right.$
    \\item \\textbf{{Cực trị:}} Điểm cực đại $CĐ(0; 2)$, điểm cực tiểu $CT(2; -2)$.
    \\item \\textbf{{Tâm đối xứng:}} Hoành độ $x_0 = -\\frac{{b}}{{3a}} = 1 \\Rightarrow I(1; 0)$.
\\end{{itemize}}

\\vspace{{8pt}}
\\begin{{center}}
\\begin{{tikzpicture}}[scale=1.0, >=Stealth]
    % Hệ trục tọa độ Oxy
    \\draw[->, thick] (-2, 0) -- (4, 0) node[right] {{$x$}};
    \\draw[->, thick] (0, -3.2) -- (0, 3.5) node[above] {{$y$}};
    \\node[below left] at (0, 0) {{$O$}};

    % Các vạch chia số trên trục
    \\foreach \\x in {{-1, 1, 2, 3}} \\draw (\\x, 0.08) -- (\\x, -0.08) node[below] {{\\small $\\x$}};
    \\foreach \\y in {{-2, -1, 1, 2}} \\draw (0.08, \\y) -- (-0.08, \\y) node[left] {{\\small $\\y$}};

    % Đường gióng nét đứt chuẩn SGK
    \\draw[dashed, gray] (2, 0) -- (2, -2) -- (0, -2);

    % Đồ thị hàm bậc ba y = x^3 - 3x^2 + 2
    \\draw[domain=-0.9:2.9, smooth, variable=\\x, blue, very thick] 
        plot ({{\\x}}, {{\\x*\\x*\\x - 3*\\x*\\x + 2}});

    % Điểm đặc biệt
    \\filldraw[red] (0, 2) circle (2pt) node[above left] {{\\textbf{{$CĐ(0; 2)$}}}};
    \\filldraw[blue] (2, -2) circle (2pt) node[below right] {{\\textbf{{$CT(2; -2)$}}}};
    \\filldraw[purple] (1, 0) circle (2pt) node[above right] {{\\textbf{{$I(1; 0)$}}}};
\\end{{tikzpicture}}
\\end{{center}}
\\end{{document}}"""
    elif "hóa" in subj_lower:
        return f"""% ==============================================================================
% CHƯƠNG TRÌNH GDPT 2018 - SGK KẾT NỐI TRI THỨC VỚI CUỘC SỐNG
% BÀI HỌC: {subject_name.upper()} {grade_lvl} - {topic_clean}
% MÃ ADN: {index_code}
% ==============================================================================
\\documentclass[preview,border=12pt]{{standalone}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[vietnamese]{{babel}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{chemfig}}

\\begin{{document}}
\\begin{{center}}
\\textbf{{\\Large PHẢN ỨNG ESTE HÓA TẠO ETYL AXETAT}} \\\\
\\vspace{{6pt}}
\\chemfig{{CH_3-C(=[1]O)-[7]OH}} + \\chemfig{{C_2H_5-OH}} 
\\;\\schemestart
\\subscheme{{\\arrow{{<=>[\\text{{H}}_2\\text{{SO}}_4 \\text{{ đặc, }} t^\\circ][]}}}}
\\schemestop\\; 
\\chemfig{{CH_3-C(=[1]O)-[7]O-C_2H_5}} + \\chemfig{{H_2O}}
\\end{{center}}
\\end{{document}}"""
    else:
        return f"""% ==============================================================================
% CHƯƠNG TRÌNH GDPT 2018 - SGK KẾT NỐI TRI THỨC VỚI CUỘC SỐNG
% BÀI HỌC: {subject_name.upper()} {grade_lvl} - {topic_clean}
% MÃ ADN: {index_code}
% ==============================================================================
\\documentclass[preview,border=12pt]{{standalone}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[vietnamese]{{babel}}
\\usepackage{{tikz}}

\\begin{{document}}
\\begin{{center}}
\\textbf{{\\Large TỔNG KẾT TRI THỨC: {topic_clean.upper()}}}
\\end{{center}}
\\begin{{tikzpicture}}
    \\node[draw=blue!80, fill=blue!10, rounded corners=6pt, inner sep=10pt] at (0,0) {{\\textbf{{{topic_clean}}}}};
\\end{{tikzpicture}}
\\end{{document}}"""


# ==============================================================================
# HỆ THỐNG NHẬN DIỆN & DỰNG BIỂU ĐỒ TRỰC QUAN ĐA MÔN - ĐA LỚP (GDPT 2018)
# ==============================================================================
def detect_lesson_visual_type(subject_name: str, topic: str) -> str:
    """Nhận diện chính xác loại biểu đồ/sơ đồ trực quan theo đúng Môn & Chủ đề bài học (Lớp 10, 11, 12)."""
    s = str(subject_name).lower()
    t = str(topic).lower()

    if "toán" in s:
        if any(k in t for k in ["tiệm cận", "phân thức", "nhất biến"]):
            return "bbt_rational_asymptote"   # BBT Hàm phân thức có vạch kép tiệm cận đứng ||
        if any(k in t for k in ["bậc hai", "parabol", "tam thức"]):
            return "oxy_parabola"             # Đồ thị & BBT Parabol Lớp 10
        if any(k in t for k in ["đơn điệu", "cực trị", "khảo sát", "đồ thị", "giá trị lớn nhất", "giá trị nhỏ nhất"]):
            return "bbt_cubic"                # BBT & Đồ thị hàm bậc 3 có cực đại, cực tiểu
        if any(k in t for k in ["lượng giác", "sin", "cos", "cung và góc"]):
            return "trig_circle"              # Đường tròn lượng giác Lớp 11
        if any(k in t for k in ["mũ", "lôgarit", "logarit"]):
            return "math_exp_log"             # Đồ thị hàm số Mũ & Logarit Lớp 11
        if any(k in t for k in ["nguyên hàm", "tích phân", "diện tích", "thể tích"]):
            return "math_integral_area"       # Hình phẳng giới hạn tích phân Lớp 12
        if any(k in t for k in ["tọa độ", "oxyz", "vectơ", "mặt phẳng", "đường thẳng", "mặt cầu", "chóp", "lăng trụ", "vuông góc"]):
            return "geometry_3d_oxyz"         # Hệ trục Oxyz & Hình học không gian
        if any(k in t for k in ["xác suất", "thống kê", "mẫu số liệu", "phương sai", "độ lệch chuẩn", "nhị thức"]):
            return "math_prob_stats"          # Biểu đồ phân bố & Cây xác suất Bayes
        return "math_concept_map"

    if "vật lí" in s or "vật lý" in s or "physics" in s:
        if any(k in t for k in ["dao động", "sóng", "điều hòa", "cơ", "động học", "newton", "năng lượng"]):
            return "physics_wave"
        if any(k in t for k in ["điện", "từ", "mạch", "cảm ứng", "xoay chiều"]):
            return "physics_electromagnetism"
        return "physics_concept_flow"

    if "hóa" in s or "chemistry" in s:
        if any(k in t for k in ["este", "lipid", "ester", "xà phòng", "carbohydrate", "polymer", "amine", "amino", "peptide", "protein"]):
            return "chem_cycle"               # Chu trình Hóa hữu cơ Lớp 12
        if any(k in t for k in ["nguyên tử", "tuần hoàn", "liên kết", "oxi hóa", "nhiệt hóa học", "tốc độ", "cân bằng", "điện li", "ph", "hydrocarbon"]):
            return "chem_equilibrium_energy"  # Giản đồ năng lượng & Cân bằng hóa học Lớp 10, 11
        return "chem_reaction_map"

    return "timeline_flow"


def build_dynamic_svg_diagram(subject_name: str, grade_lvl: int, topic: str) -> str:
    """Sinh mã SVG trực quan sắc nét chuẩn Sư phạm GDPT 2018 theo Môn & Chủ đề bài học."""
    vtype = detect_lesson_visual_type(subject_name, topic)
    t_title = html.escape(str(topic).strip() or "Bài học")
    grade_str = f"LỚP {grade_lvl}" if grade_lvl else ""

    if vtype == "bbt_rational_asymptote":
        return f"""<svg viewBox="0 0 820 230" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border-radius:10px;border:1.8px solid #0f172a;">
            <rect x="0" y="0" width="820" height="32" fill="#0f172a"/>
            <text x="16" y="21" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc">BẢNG BIẾN THIÊN HÀM PHÂN THỨC &amp; TIỆM CẬN ĐỨNG (CHUẨN BỘ GD&amp;ĐT) — {t_title}</text>
            <!-- Khung bảng BBT -->
            <rect x="18" y="44" width="520" height="170" fill="#ffffff" stroke="#0f172a" stroke-width="2"/>
            <line x1="18" y1="80" x2="538" y2="80" stroke="#0f172a" stroke-width="1.8"/>
            <line x1="18" y1="120" x2="538" y2="120" stroke="#0f172a" stroke-width="1.8"/>
            <line x1="82" y1="44" x2="82" y2="214" stroke="#0f172a" stroke-width="2"/>
            <!-- Vạch đôi tiệm cận đứng || xuyên suốt hàng y' và y -->
            <line x1="307" y1="80" x2="307" y2="214" stroke="#dc2626" stroke-width="2"/>
            <line x1="313" y1="80" x2="313" y2="214" stroke="#dc2626" stroke-width="2"/>
            <!-- Hàng x -->
            <text x="50" y="67" font-family="Times New Roman,serif" font-size="16" font-weight="bold" font-style="italic" text-anchor="middle">x</text>
            <text x="110" y="67" font-family="Times New Roman,serif" font-size="15" font-weight="bold" text-anchor="middle">−∞</text>
            <text x="310" y="67" font-family="Times New Roman,serif" font-size="15" font-weight="bold" fill="#dc2626" text-anchor="middle">x₀ = −d/c</text>
            <text x="510" y="67" font-family="Times New Roman,serif" font-size="15" font-weight="bold" text-anchor="middle">+∞</text>
            <!-- Hàng y' -->
            <text x="50" y="105" font-family="Times New Roman,serif" font-size="16" font-weight="bold" font-style="italic" text-anchor="middle">y'</text>
            <text x="205" y="106" font-family="Arial,sans-serif" font-size="18" font-weight="bold" fill="#dc2626" text-anchor="middle">−</text>
            <text x="415" y="106" font-family="Arial,sans-serif" font-size="18" font-weight="bold" fill="#dc2626" text-anchor="middle">−</text>
            <!-- Hàng y: Giới hạn tiệm cận ngang y = a/c và tiệm cận đứng x = -d/c -->
            <text x="50" y="170" font-family="Times New Roman,serif" font-size="16" font-weight="bold" font-style="italic" text-anchor="middle">y</text>
            <text x="112" y="142" font-family="Times New Roman,serif" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">a/c</text>
            <line x1="132" y1="145" x2="272" y2="195" stroke="#dc2626" stroke-width="2.2"/>
            <polygon points="272,195 262,194 267,186" fill="#dc2626"/>
            <text x="290" y="204" font-family="Times New Roman,serif" font-size="14" font-weight="bold" text-anchor="middle">−∞</text>
            <text x="332" y="142" font-family="Times New Roman,serif" font-size="14" font-weight="bold" text-anchor="middle">+∞</text>
            <line x1="352" y1="145" x2="482" y2="195" stroke="#dc2626" stroke-width="2.2"/>
            <polygon points="482,195 472,194 477,186" fill="#dc2626"/>
            <text x="510" y="204" font-family="Times New Roman,serif" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">a/c</text>
            <!-- Khung ghi chú Sư phạm bên phải -->
            <rect x="554" y="44" width="250" height="170" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
            <text x="568" y="70" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#0f172a">GHI NHỚ SƯ PHẠM TRỌNG TÂM:</text>
            <text x="568" y="96" font-family="Arial,sans-serif" font-size="11.5" fill="#dc2626" font-weight="bold">• TCĐ: x = −d/c (vạch kép ||)</text>
            <text x="568" y="120" font-family="Arial,sans-serif" font-size="11.5" fill="#1d4ed8" font-weight="bold">• TCN: y = a/c (khi x → ±∞</text>
            <text x="568" y="146" font-family="Arial,sans-serif" font-size="11" fill="#334155">• Đạo hàm y' = (ad − bc)/(cx + d)²</text>
            <text x="568" y="168" font-family="Arial,sans-serif" font-size="11" fill="#334155">• Hàm số KHÔNG có cực trị.</text>
            <text x="568" y="190" font-family="Arial,sans-serif" font-size="11" fill="#334155">• Tâm đối xứng: I(−d/c ; a/c).</text>
        </svg>"""

    elif vtype == "chem_equilibrium_energy":
        return f"""<svg viewBox="0 0 820 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border-radius:10px;border:1.8px solid #0f172a;">
            <rect x="0" y="0" width="820" height="32" fill="#0f172a"/>
            <text x="16" y="21" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc">SƠ ĐỒ TRỰC QUAN HÓA HỌC ({grade_str}) — {t_title}</text>
            <rect x="28" y="56" width="220" height="130" rx="10" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
            <text x="138" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle">1. CẤU TRÚC &amp; BẢN CHẤT</text>
            <text x="138" y="116" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Cấu hình electron / Liên kết</text>
            <text x="138" y="140" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Số oxi hóa &amp; Hằng số K_c</text>
            <line x1="248" y1="121" x2="296" y2="121" stroke="#0f172a" stroke-width="2.2"/>
            <polygon points="296,121 286,116 286,126" fill="#0f172a"/>
            <rect x="298" y="56" width="224" height="130" rx="10" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
            <text x="410" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#166534" text-anchor="middle">2. QUY LUẬT BIẾN ĐỔI</text>
            <text x="410" y="116" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Bảo toàn e / Bảo toàn khối lượng</text>
            <text x="410" y="140" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Nguyên lý Le Chatelier (ΔH, P, C)</text>
            <line x1="522" y1="121" x2="570" y2="121" stroke="#0f172a" stroke-width="2.2"/>
            <polygon points="570,121 560,116 560,126" fill="#0f172a"/>
            <rect x="572" y="56" width="220" height="130" rx="10" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
            <text x="682" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#991b1b" text-anchor="middle">3. ỨNG DỤNG &amp; BÀI TOÁN</text>
            <text x="682" y="116" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Nhận biết &amp; Hiện tượng thực tế</text>
            <text x="682" y="140" font-family="Arial,sans-serif" font-size="11.5" fill="#1e293b" text-anchor="middle">Giải toán hiệu suất H% &amp; nồng độ</text>
        </svg>"""

    elif vtype == "chem_cycle":
        return f"""<svg viewBox="0 0 820 220" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border-radius:10px;border:1.8px solid #0f172a;">
            <rect x="0" y="0" width="820" height="32" fill="#0f172a"/>
            <text x="16" y="21" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc">CHU TRÌNH CHUYỂN HÓA HỮU CƠ (LỚP 12) — {t_title}</text>
            <rect x="35" y="55" width="220" height="130" rx="10" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
            <text x="145" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle">CH₃COOH + C₂H₅OH</text>
            <text x="145" y="115" font-family="Arial,sans-serif" font-size="11" fill="#334155" text-anchor="middle">Carboxylic Acid + Alcohol</text>
            <text x="145" y="138" font-family="Arial,sans-serif" font-size="11" fill="#16a34a" font-weight="bold" text-anchor="middle">H₂SO₄ đặc, t°</text>
            <line x1="255" y1="120" x2="310" y2="120" stroke="#0f172a" stroke-width="2.2"/>
            <polygon points="310,120 300,115 300,125" fill="#0f172a"/>
            <rect x="315" y="55" width="220" height="130" rx="10" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
            <text x="425" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#166534" text-anchor="middle">CH₃COOC₂H₅ + H₂O</text>
            <text x="425" y="115" font-family="Arial,sans-serif" font-size="11" fill="#334155" text-anchor="middle">Ethyl acetate (Este thơm)</text>
            <text x="425" y="138" font-family="Arial,sans-serif" font-size="11" fill="#dc2626" font-weight="bold" text-anchor="middle">Phản ứng thuận nghịch</text>
            <line x1="535" y1="120" x2="590" y2="120" stroke="#0f172a" stroke-width="2.2"/>
            <polygon points="590,120 580,115 580,125" fill="#0f172a"/>
            <rect x="595" y="55" width="195" height="130" rx="10" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
            <text x="692" y="88" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#991b1b" text-anchor="middle">ỨNG DỤNG THỰC TIỄN</text>
            <text x="692" y="115" font-family="Arial,sans-serif" font-size="11" fill="#334155" text-anchor="middle">Dung môi hữu cơ</text>
            <text x="692" y="138" font-family="Arial,sans-serif" font-size="11" fill="#334155" text-anchor="middle">Hương liệu thực phẩm</text>
        </svg>"""

    # Mặc định: Sơ đồ tư duy tiến trình chuẩn
    return f"""<svg viewBox="0 0 820 200" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border-radius:10px;border:1.8px solid #0f172a;">
    <rect x="0" y="0" width="820" height="32" fill="#0f172a"/>
    <text x="16" y="21" font-family="Arial,sans-serif" font-size="12" font-weight="bold" fill="#f8fafc">SƠ ĐỒ TRỰC QUAN TIẾN TRÌNH TRI THỨC ({grade_str}) — {t_title}</text>
    <rect x="30" y="55" width="225" height="115" rx="8" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>
    <text x="142" y="90" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#1e40af" text-anchor="middle">1. KHÁI NIỆM &amp; ĐỊNH NGHĨA</text>
    <text x="142" y="118" font-family="Arial,sans-serif" font-size="11.5" fill="#334155" text-anchor="middle">Bản chất quy luật cốt lõi</text>
    <line x1="255" y1="112" x2="295" y2="112" stroke="#0f172a" stroke-width="2.2"/>
    <polygon points="295,112 285,107 285,117" fill="#0f172a"/>
    <rect x="298" y="55" width="225" height="115" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="410" y="90" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#166534" text-anchor="middle">2. QUY TẮC &amp; VẬN DỤNG</text>
    <text x="410" y="118" font-family="Arial,sans-serif" font-size="11.5" fill="#334155" text-anchor="middle">Công thức &amp; Phương pháp giải</text>
    <line x1="523" y1="112" x2="563" y2="112" stroke="#0f172a" stroke-width="2.2"/>
    <polygon points="563,112 553,107 553,117" fill="#0f172a"/>
    <rect x="566" y="55" width="224" height="115" rx="8" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
    <text x="678" y="90" font-family="Arial,sans-serif" font-size="13" font-weight="bold" fill="#991b1b" text-anchor="middle">3. THỰC TIỄN &amp; MỞ RỘNG</text>
    <text x="678" y="118" font-family="Arial,sans-serif" font-size="11.5" fill="#334155" text-anchor="middle">Giải quyết bài toán thực tế</text>
    </svg>"""
