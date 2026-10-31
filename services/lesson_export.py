"""Deterministic lesson exports: preserve source text and typeset formulas offline."""
import base64
import hashlib
import html
import json
import re
from functools import lru_cache
from pathlib import Path

from markdown_it import MarkdownIt
from services.academic_context import academic_context

ROOT = Path(__file__).resolve().parents[1]
_TOKENS = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`|(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|\\\[[\s\S]*?\\\]|\\\([^\n]*?\\\)|(?<!\\)\$(?!\$)[^\n$]+?(?<!\\)\$)")


@lru_cache(maxsize=1)
def renderer_assets():
    vendor = ROOT / "assets/vendor/katex/dist"
    css = (vendor / "katex.min.css").read_text(encoding="utf-8")
    # Keep only the WOFF2 source, embedded; no CDN or fonts/ URL is needed.
    def font_source(match):
        block = match[0]
        font = re.search(r"url\([^)]*?fonts/([^/()]+\.woff2)\)", block)
        if not font:
            raise ValueError("KaTeX font face has no packaged WOFF2 source")
        encoded = base64.b64encode((vendor / "fonts" / font[1]).read_bytes()).decode()
        return re.sub(r"src:[^;}]+", 'src:url("data:font/woff2;base64,' + encoded + '") format("woff2")', block)
    css = re.sub(r"@font-face\{[^}]+\}", font_source, css)
    notebook = base64.b64encode((ROOT / "assets/fonts/Caveat.ttf").read_bytes()).decode()
    js = "\n".join((vendor / name).read_text(encoding="utf-8") for name in ("katex.min.js", "contrib/mhchem.min.js"))
    license_text = (ROOT / "assets/fonts/Caveat-OFL.txt").read_text(encoding="utf-8") + "\n" + (ROOT / "assets/vendor/katex/LICENSE").read_text(encoding="utf-8")
    css += "\n/* " + license_text.replace("*/", "* /") + " */"
    return css, notebook, js.replace("</script", r"<\/script")


def lesson_body_html(lesson):
    """Protect math/code separately; never convert formulas to approximate Unicode."""
    replacements = {}
    nonce = hashlib.sha256(lesson.encode()).hexdigest()[:12]

    def protect(match):
        raw = match[0]
        if raw.startswith(("`", "~~~")):
            return raw
        display = raw.startswith(("$$", r"\["))
        width = 2 if raw.startswith(("$$", r"\[", r"\(")) else 1
        tex = raw[width:-width]
        token = f"GSAIMATH{nonce}N{len(replacements)}END"
        replacements[token] = ('<span class="lesson-math" data-display="' + str(display).lower() +
                               '" data-tex="' + html.escape(tex, quote=True) + '">' + html.escape(raw) + '</span>')
        return token

    protected = _TOKENS.sub(protect, lesson)
    outside_code = re.sub(r"```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`", "", protected)
    naked_math = re.search(r"\\(?:frac|dfrac|sqrt|begin|ce|pu|omega|alpha|int|sum|vec)\b", outside_code)
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    # Remote images are not evidence of the selected lesson. Preserve their alt
    # description, without loading arbitrary image hosts from generated text.
    md.renderer.rules["image"] = lambda tokens, idx, options, env: html.escape(tokens[idx].content)
    body = md.render(protected)
    for token, value in replacements.items():
        body = body.replace(token, value)
    if naked_math:
        body = '<p class="notice" data-source-issue="math-delimiter">Có lệnh công thức chưa nằm trong dấu phân cách toán học; cần sửa nội dung trước khi in.</p>' + body
    return body


def build_lesson_html(subject, grade, topic, lesson, style="handwritten"):
    subject, grade = academic_context(subject, grade)
    if not isinstance(lesson, str) or not lesson.strip():
        raise ValueError("Chưa có nội dung bài học để xuất.")
    if len(lesson) > 250000:
        raise ValueError("Bài học quá dài để xuất trong một lượt.")
    if style not in {"handwritten", "color", "monochrome"}:
        raise ValueError("Kiểu bản in không hợp lệ.")
    css, font, js = renderer_assets()
    digest = hashlib.sha256(lesson.encode()).hexdigest()
    metadata = json.dumps({"subject": subject, "grade": grade, "topic": topic, "source_sha256": digest}, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(str(topic or subject))
    body = lesson_body_html(lesson)
    return r'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + title + r'''</title>
<style>''' + css + r'''
@font-face{font-family:GSAIHand;src:url(data:font/ttf;base64,''' + font + r''') format('truetype');font-weight:100 900;font-display:swap}
*{box-sizing:border-box}body{margin:0;background:#e8e3d8;color:#182c73;font-family:Georgia,'Times New Roman',serif}
.toolbar{padding:12px;background:#fff;position:sticky;top:0;z-index:5;font:14px system-ui;color:#334155}.toolbar button{padding:8px 18px;margin-right:12px;cursor:pointer}
.paper{max-width:820px;margin:20px auto;padding:32px 35px 40px 66px;background:#f5eedc;min-height:1120px;overflow-wrap:anywhere;position:relative}
.handwritten .paper{padding:30px 34px 40px 76px;background-color:#f5eedc;background-image:linear-gradient(#aea18a30 1px,transparent 1px),linear-gradient(90deg,#aea18a30 1px,transparent 1px),linear-gradient(90deg,#e1d3b9,transparent 10%,#fff5 55%,transparent);background-size:24px 24px,24px 24px,100% 100%;box-shadow:0 6px 24px #36280c26;border-radius:2px}
.handwritten .paper:before{content:"";position:absolute;top:0;bottom:0;left:0;width:37px;background:radial-gradient(ellipse 8px 7px at 27px 24px,#332e27 65%,#b0a18a 72%,transparent 82%) 0 0/37px 48px repeat-y;pointer-events:none}
.handwritten .paper:after{content:"";position:absolute;top:0;bottom:0;left:-5px;width:36px;background:repeating-linear-gradient(180deg,transparent 0 18px,#222 18px 21px,#8a8983 21px 24px,#252521 24px 28px,transparent 28px 48px);border-radius:5px;pointer-events:none}
.handwritten article{font:26px/1.48 GSAIHand,cursive;font-weight:500;font-synthesis:none}.handwritten h1,.handwritten h2,.handwritten h3,.handwritten h4{font-family:GSAIHand,cursive}
.notebook-header{display:none}.handwritten .notebook-header{display:grid;grid-template-columns:minmax(140px,1fr) minmax(0,2fr);gap:18px;align-items:start;border-bottom:2px solid #a72b36;padding-bottom:15px;margin-bottom:24px;font:24px/1.2 GSAIHand,cursive}
.notebook-identity{text-align:center;padding-top:3px}.notebook-identity strong{display:block;font-weight:600}.notebook-identity span{display:inline-block;border-bottom:1px solid #a72b36;padding-bottom:6px;margin-top:6px;font-size:20px}.notebook-heading h1{margin:0 0 7px;font-size:30px;text-align:center}.notebook-heading .context{font:24px/1.25 GSAIHand,cursive;margin:0;color:#182c73}
.handwritten>.toolbar{border-bottom:1px solid #d6c6aa}.handwritten .plain-header{display:none}.handwritten article h1,.handwritten article h2,.handwritten article h3,.handwritten article h4{color:#a82332;font-weight:650;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:5px;text-align:left;margin:22px 0 12px}.handwritten article h1{font-size:1.25em}.handwritten article h2{font-size:1.15em}.handwritten article h3,.handwritten article h4{font-size:1.07em}
.handwritten article strong{font-weight:650}.handwritten article li::marker{color:#a82332;font-weight:650}.handwritten article blockquote{margin:16px 0;padding:1px 0 1px 18px;border-left:2px solid #a82332}.handwritten article table{background:#fff3}.handwritten article th{color:#a82332}.handwritten .source-note{font:18px/1.35 GSAIHand,cursive;color:#655842}
.handwritten .katex{font-size:.88em}.handwritten .katex-display{margin:.6em 0}.handwritten .lesson-end{display:flex;align-items:center;gap:12px;color:#a82332;font:23px GSAIHand,cursive;justify-content:center;margin:24px 0 14px}.lesson-end{display:none}.lesson-end:before,.lesson-end:after{content:"";border-top:1px dashed currentColor;flex:1;max-width:160px}
h1{font-size:30px;line-height:1.2;color:#b51e35;text-align:center;margin:10px 0 20px}h2,h3,h4{color:#b51e35;line-height:1.25;break-after:avoid}h2{font-size:1.2em}h3{font-size:1.1em}
.context{text-align:center;font:15px system-ui;margin-bottom:20px;color:#334155}.source-note{font:13px system-ui;border-top:1px solid #bcae94;padding-top:12px;margin-top:24px;color:#475569}
article{font-size:17px;line-height:1.6}article p{margin:0 0 .75em}article li{margin:.25em 0}article table{border-collapse:collapse;width:100%;font-size:.85em}td,th{border:1px solid #9e998e;padding:6px;vertical-align:top}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#ffffff80;padding:10px;font:14px/1.4 monospace}code{font-family:monospace;font-size:.8em}.katex{font-size:1.02em}.katex-display{overflow-x:auto;overflow-y:hidden;margin:.7em 0}
.formula-error{outline:2px solid #b91c1c;color:#991b1b;white-space:pre-wrap;font-family:monospace}.monochrome,.monochrome h1,.monochrome h2,.monochrome h3,.monochrome h4{color:#111}.monochrome .paper{background:#fff}
.color .paper{background:#fff}.color h2{border-left:4px solid #0891b2;padding-left:10px}.notice{color:#b91c1c}
@media(max-width:600px){.paper{margin:10px 8px;padding:20px}.handwritten .paper{padding:24px 18px 28px 48px}.handwritten article{font-size:22px}.handwritten .notebook-header{grid-template-columns:1fr;gap:14px}.notebook-identity span{margin-top:2px}.notebook-heading h1{font-size:28px}}
@page{size:A4;margin:10mm}@media print{body{background:#fff}.toolbar{display:none}.paper{margin:0;max-width:none;min-height:0;padding:10mm 7mm 10mm 12mm;box-shadow:none}.handwritten .paper{padding:5mm 5mm 7mm 16mm;box-shadow:none;print-color-adjust:exact;-webkit-print-color-adjust:exact;box-decoration-break:clone;-webkit-box-decoration-break:clone}.handwritten .notebook-header{grid-template-columns:minmax(120px,1fr) minmax(0,2fr);break-inside:avoid}.handwritten article{font-size:23px}.handwritten .source-note{font-size:16px}article{orphans:3;widows:3}p,li{break-inside:avoid}pre{break-inside:auto}thead{display:table-header-group}tr{break-inside:avoid}.katex-display{overflow:visible}a{color:inherit;text-decoration:none}}
</style></head><body class="''' + style + r'''">
<div class="toolbar"><button id="print" disabled>In / Lưu PDF</button><span id="render-status">Đang dựng công thức…</span></div>
<main class="paper"><header class="notebook-header"><div class="notebook-identity"><strong>SỔ TAY HỌC TẬP</strong><span>KẾT NỐI TRI THỨC</span></div><div class="notebook-heading"><h1>''' + title + r'''</h1><div class="context">''' + html.escape(subject) + f" · Lớp {grade}" + r'''</div></div></header>
<header class="plain-header"><h1>''' + title + r'''</h1><div class="context">''' + html.escape(subject) + f" · Lớp {grade}" + r'''</div></header>
<article id="lesson">''' + body + r'''</article>
<div class="lesson-end" aria-hidden="true">Hết bài</div>
<p class="source-note">Bản trình bày giữ nội dung bài học AI, không bổ sung công thức hoặc ví dụ mẫu. Cần giáo viên duyệt tính đúng đắn học thuật trước khi sử dụng chính thức. Nội dung dài được in thành nhiều trang.</p></main>
<script type="application/json" id="lesson-context">''' + metadata + r'''</script>
<script>''' + js + r'''</script><script>
(async function(){let errors=document.querySelectorAll('[data-source-issue]').length;const status=document.getElementById('render-status');
for(const el of document.querySelectorAll('.lesson-math')){try{katex.render(el.dataset.tex,el,{displayMode:el.dataset.display==='true',throwOnError:true,trust:false,strict:'warn',maxExpand:1000,maxSize:20});}catch(error){errors++;el.textContent=el.dataset.tex;el.classList.add('formula-error');el.title='Công thức chưa dựng được; cần kiểm tra cú pháp.';}}
// Variation tables: keep source values, draw continuous interval arrows.
for(const table of document.querySelectorAll('article table')){
 const rows=Array.from(table.rows);
 const plain=cell=>{const c=cell.cloneNode(true);for(const m of c.querySelectorAll('.lesson-math'))m.replaceWith(m.dataset.tex);return c.textContent.trim().replace(/\\(?:infty)/g,'∞').replace(/[$ {}]/g,'').replace(/−/g,'-');};
 if(rows.length!==3)continue;
 const data=rows.map(r=>Array.from(r.cells).map(plain));
 if(data[0][0]!=='x'||!/^y[′']$/.test(data[1][0])||data[2][0]!=='y')continue;
 if(!data.every(r=>r.length===data[0].length)||data.some(r=>r.some(v=>v.includes('||'))))continue;
 const points=[];for(let i=1;i<data[0].length;i++)if(data[0][i])points.push(i);
 if(points.length<2||points.length>8)continue;
 const dirs=[];for(let k=0;k<points.length-1;k++){const a=points[k],b=points[k+1];const sign=data[1].slice(a+1,b).join('');const arrow=data[2].slice(a+1,b).join('');dirs.push(arrow.includes('↗')||sign==='+'?'up':arrow.includes('↘')||sign==='-'?'down':null);}
 if(dirs.some(d=>!d)||dirs.some((d,k)=>{const a=data[2][points[k]],b=data[2][points[k+1]];const num=v=>v==='-∞'?-Infinity:v==='+∞'||v==='∞'?Infinity:Number(v.replace(',','.'));return d==='up'?num(a)>=num(b):num(a)<=num(b);})||points.some(i=>!/^[-+]?([0-9]+([.,][0-9]+)?|∞)$/.test(data[2][i])))continue;
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
 svg.setAttribute('viewBox','0 0 820 220');svg.setAttribute('role','img');svg.setAttribute('aria-label',table.innerText);svg.style.cssText='display:block;width:100%;height:auto;background:white;color:#111;break-inside:avoid;font:20px Times New Roman,serif';
 const add=(tag,attrs,text)=>{const el=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;svg.append(el);return el;};
 add('rect',{x:1,y:1,width:818,height:218,fill:'white',stroke:'#111','stroke-width':2});
 for(const y of [52,100])add('line',{x1:1,y1:y,x2:819,y2:y,stroke:'#111','stroke-width':1.5});
 add('line',{x1:82,y1:1,x2:82,y2:219,stroke:'#111','stroke-width':1.5});
 const label=(x,y,t)=>add('text',{x,y,fill:'#111','text-anchor':'middle','dominant-baseline':'middle'},t.replace(/-/g,'−'));
 label(42,28,'x');label(42,77,'y′');label(42,160,'y');
 const xs=points.map((_,k)=>130+k*640/(points.length-1));
 const ys=points.map((i,k)=>{const v=data[2][i];if(v.includes('∞'))return v.startsWith('-')?196:124;return (dirs[k]==='down'||dirs[k-1]==='up')?145:178;});
 points.forEach((i,k)=>{label(xs[k],28,data[0][i]);label(xs[k],77,data[1][i]);label(xs[k],ys[k],data[2][i]);});
 dirs.forEach((d,k)=>{label((xs[k]+xs[k+1])/2,77,data[1].slice(points[k]+1,points[k+1]).join(''));const x1=xs[k]+25,x2=xs[k+1]-25,y1=ys[k],y2=ys[k+1];add('line',{x1,y1,x2,y2,stroke:'#111','stroke-width':2});const a=Math.atan2(y2-y1,x2-x1);add('path',{d:`M ${x2-9*Math.cos(a-.45)} ${y2-9*Math.sin(a-.45)} L ${x2} ${y2} L ${x2-9*Math.cos(a+.45)} ${y2-9*Math.sin(a+.45)}`,fill:'none',stroke:'#111','stroke-width':2});});
 table.replaceWith(svg);
}
await document.fonts.ready;status.textContent=errors?'Có '+errors+' công thức cần kiểm tra; chưa cho in.':'Đã dựng công thức. Có thể in hoặc lưu PDF.';status.className=errors?'notice':'';
const print=document.getElementById('print');print.disabled=errors>0;print.onclick=()=>window.print();document.documentElement.dataset.renderErrors=String(errors);document.documentElement.dataset.renderReady='true';
})();</script></body></html>'''


def handwritten_prompt(subject, grade, topic, lesson):
    subject, grade = academic_context(subject, grade)
    return json.dumps({"purpose": "STYLE REFERENCE ONLY — use deterministic HTML/PDF for authoritative text and formulas",
                       "subject": subject, "grade": grade, "title": topic, "content": lesson,
                       "style": {"paper": "cream graph paper #F5EEDC", "binding": "black spiral on the left",
                                 "body_ink": "#182C73", "heading_ink": "#B51E35",
                                 "handwriting": "legible Vietnamese cursive, slight right slant, complete diacritics",
                                 "layout": "notebook page; two-part header; red underlined section headings; blue body; black spiral loops and punched holes on left; fine square grid",
                                 "reference_scope": "Use the supplied notebook image for visual style only; no exam year, ministry identity, questions, or official certification"},
                       "rules": ["Use only the supplied lesson content and context", "Never invent or alter formulas, facts, examples or figures",
                                 "Preserve chemical, physical, mathematical and language notation for this subject",
                                 "Use multiple pages instead of cutting or shrinking content", "Do not copy any subject matter or identity from a style reference"]}, ensure_ascii=False, indent=2)


def faithful_infographic_data(subject, grade, topic, lesson):
    academic_context(subject, grade)
    if not lesson or not lesson.strip():
        raise ValueError("Không có nội dung bài học để trích xuất infographic.")
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    title, rows = str(topic or subject), []
    tokens = md.parse(lesson)
    for index, token in enumerate(tokens):
        if token.type == "inline" and index and tokens[index - 1].type == "heading_open":
            title = token.content
        elif token.type == "inline" and token.content.strip():
            rows.append((title, token.content, ""))
    # Legacy SVG is explicitly a short excerpt. Full, exact, multi-page content
    # is available in build_lesson_html; never pad excerpt slots with facts.
    return {"box1": rows[:4], "box2": rows[4:8], "box4": [],
            "example": {"title": "Nội dung trích từ bài học", "steps": [], "visual_svg": ""},
            "source_sha256": hashlib.sha256(lesson.encode()).hexdigest(), "is_excerpt": True}
