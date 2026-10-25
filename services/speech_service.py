"""On-demand browser speech. Never fetch audio while rendering a station."""
import hashlib
import html
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def speech_script():
    return Path(__file__).resolve().parents[1].joinpath("assets/pedagogical_speech.js").read_text(encoding="utf-8")


def speech_controls(subject, grade, station):
    return '''<section id="gsai-speech-controls" aria-label="Giọng đọc học tập"
      style="border:1px solid #64748b;border-radius:10px;padding:12px;margin:8px 0;color:inherit">
      <strong>🔊 Giọng đọc học tập · Trạm 1–3</strong>
      <details><summary>Chọn giọng và cách đọc</summary>
      <p>Giọng Việt do thiết bị cung cấp; tên giọng không tự chứng minh giọng Nam Bộ.
      Anh/chị có thể nghe thử và chọn giọng phù hợp. Mặc định dùng bộ giọng của trình duyệt;
      giọng do nhà cung cấp xử lý trực tuyến có thể cần mạng.</p>
      <label>Giọng tiếng Việt <select id="gsai-voice-vi" aria-label="Giọng tiếng Việt"></select></label><br>
      <label>English voice <select id="gsai-voice-en" aria-label="English voice"></select></label><br>
      <label>Ngôn ngữ đoạn chọn <select id="gsai-speech-language" aria-label="Ngôn ngữ đoạn chọn">
      <option value="auto">Tự nhận diện Anh–Việt</option><option value="vi">Tiếng Việt</option>
      <option value="en">English</option></select></label><br>
      <label><input id="gsai-auto-read" type="checkbox" checked> Đọc khi bấm đúp hoặc tô chọn nội dung</label>
      <p><label><input id="gsai-cloud-read" type="checkbox"> Dùng giọng miễn phí trực tuyến khi máy thiếu giọng</label><br>
      Khi bật, đoạn đang đọc được gửi tới Google Translate TTS. Giọng Việt dự phòng chưa xác nhận Nam Bộ;
      cần mạng và có thể chậm hoặc tạm ngừng phục vụ. Không bật nếu không muốn gửi đoạn chọn.</p>
      <p>Từ ngắn không dấu hoặc tên riêng có thể mơ hồ; dùng lựa chọn ngôn ngữ khi cần.
      Công thức chưa hỗ trợ sẽ được báo để đối chiếu, không tự đoán cách đọc.</p>
      <button type="button" data-gsai-sample="vi">Nghe thử tiếng Việt</button>
      <button type="button" data-gsai-sample="en">Try English voice</button>
      </details>
      <button type="button" data-gsai-read-selection>▶ Đọc đoạn đang chọn</button>
      <button type="button" data-gsai-stop>■ Dừng đọc</button>
      <button type="button" id="gsai-play-audio" data-gsai-play-audio hidden>▶ Phát âm thanh đã tải</button>
      <div id="gsai-speech-status" role="status" aria-live="polite">Chọn chữ hoặc bấm Nghe để đọc; không tải âm thanh khi mở trạm.</div>
      </section>'''


def speech_bootstrap(subject, grade, station):
    """Execute trusted local JS in the page realm, with no arbitrary input as code.

    The tiny same-origin component also supports Streamlit builds whose st.html
    frontend ignores the unsafe-JavaScript flag. The controls themselves use safe HTML.
    """
    context = json.dumps({"subject": str(subject), "grade": int(grade), "station": str(station)}, ensure_ascii=False).replace("<", "\\u003c")
    script = json.dumps(speech_script(), ensure_ascii=False).replace("<", "\\u003c")
    return '''<script>(function(){try{
      const host=window.parent, page=host.document;
      const script=page.createElement('script'); script.textContent=''' + script + ''';
      page.head.appendChild(script); script.remove();
      const context=''' + context + ''';
      function attach(){if(!page.getElementById('gsai-speech-controls') || !host.GSAISpeech)return false;
        host.GSAISpeech.updateContext(context); return true;}
      if(!attach()) {const observer=new MutationObserver(()=>{if(attach())observer.disconnect();});
        observer.observe(page.body,{childList:true,subtree:true}); setTimeout(()=>observer.disconnect(),5000);}
    }catch(error){console.warn('Speech controls could not initialize in this browser.');}})();</script>'''


def speech_button(text, subject, key, label="▶ Nghe nội dung này"):
    text = str(text or "")
    if not text.strip():
        return ""
    identity = hashlib.sha256(str(key).encode()).hexdigest()[:16]
    return '<button type="button" id="gsai-read-' + identity + '" data-gsai-speech="' + html.escape(text, quote=True) + '" data-gsai-subject="' + html.escape(str(subject), quote=True) + '">' + html.escape(label) + '</button>'


def speech_preview_bridge():
    """Only the embedded lesson preview uses this bridge, not downloaded files."""
    return r'''<script>(function(){
      let last='', stamp=0;
      function read(event){try{
        const engine=window.parent.GSAISpeech, controls=window.parent.document;
        if(!engine || controls.getElementById('gsai-auto-read')?.checked===false) return;
        if(event.target.closest?.('button,input,textarea,select,pre,code')) return;
        const selected=window.getSelection(); if(!selected || selected.isCollapsed) return;
        const range=selected.getRangeAt(0), copy=range.cloneContents();
        copy.querySelectorAll('.katex').forEach(el=>{const a=el.querySelector('annotation[encoding="application/x-tex"]');if(a)el.replaceWith(document.createTextNode('$'+a.textContent+'$'));});
        const ancestor=range.commonAncestorContainer.nodeType===1?range.commonAncestorContainer:range.commonAncestorContainer.parentElement;
        const math=ancestor.closest('.katex')?.querySelector('annotation[encoding="application/x-tex"]');
        const text=(math?'$'+math.textContent+'$':copy.textContent||selected.toString()).trim();
        if(!text || text.length>8000 || (text===last && Date.now()-stamp<1000)) return;
        last=text; stamp=Date.now();
        const language=controls.getElementById('gsai-speech-language')?.value;
        engine.speak(text,language==='auto'?null:language);
      }catch(_){ /* An inaccessible frame never bypasses the browser sandbox. */ }}
      document.addEventListener('pointerup',read);
      document.addEventListener('dblclick',read);
      document.addEventListener('keyup',event=>{if(event.key==='Shift')read(event);});
    })();</script>'''
