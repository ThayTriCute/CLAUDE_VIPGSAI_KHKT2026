"""Optional free Vietnamese fallback, requested only with explicit UI opt-in."""
import base64
from pathlib import Path
import re
import time

import requests
import streamlit as st

_RELAY_JS = Path(__file__).resolve().parents[1].joinpath("assets/speech_audio_relay.js").read_text(encoding="utf-8")


def valid_request(value, context):
    return (isinstance(value, dict) and value.get("consent") is True
            and value.get("context") == context and value.get("lang") in {"vi", "en"}
            and isinstance(value.get("text"), str) and 0 < len(value["text"]) <= 500
            and isinstance(value.get("id"), str) and bool(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value["id"])))


@st.cache_data(ttl=1800, max_entries=16, show_spinner=False)
def free_speech_audio(text, lang):
    if lang not in {"vi", "en"} or not isinstance(text, str) or not 0 < len(text) <= 500:
        raise ValueError("Đoạn đọc dự phòng phải có 1–500 ký tự và đúng ngôn ngữ.")
    chunks, current = [], ""
    for word in re.findall(r"\S+\s*", text):
        if len(word) > 180:
            raise ValueError("Từ hoặc mã quá dài để đọc dự phòng; hãy chọn đoạn khác.")
        if current and len(current + word) > 180:
            chunks.append(current.strip())
            current = ""
        current += word
    if current.strip():
        chunks.append(current.strip())
    if not chunks:
        raise ValueError("Chưa có nội dung để đọc.")
    audio = []
    # No partial-success concatenation: any failed chunk rejects the whole request.
    for chunk in chunks:
        response = requests.get("https://translate.googleapis.com/translate_tts",
                                params={"ie": "UTF-8", "tl": lang, "client": "gtx", "q": chunk},
                                headers={"User-Agent": "Mozilla/5.0"}, timeout=(3, 5))
        response.raise_for_status()
        if not response.headers.get("Content-Type", "").lower().startswith("audio/") or not 100 < len(response.content) <= 1000000:
            raise ValueError("Dịch vụ chưa trả về âm thanh hợp lệ.")
        audio.append(response.content)
    return b"".join(audio)


@st.fragment
def render_speech_audio(context):
    # Register with the active runtime, not at module import: AppTest and process
    # restarts may create a new component registry while Python modules survive.
    relay = st.components.v2.component("gsai_speech_audio", html="<span></span>",
                                       isolate_styles=False, js=_RELAY_JS)
    state = st.session_state.setdefault("_speech_audio_state", {})
    if state.get("context") != context:
        state = {"context": context, "response": {}, "handled": None}
        st.session_state["_speech_audio_state"] = state
    result = relay(data={"response": state["response"], "context": context},
                    key="gsai_speech_audio", on_request_change=lambda: None, height=0)
    request = result.request
    if not valid_request(request, context) or request["id"] == state["handled"]:
        return
    state["handled"] = request["id"]
    now = time.monotonic()
    recent = [t for t in st.session_state.get("_speech_audio_requests", []) if now - t < 60]
    response = {"id": request["id"]}
    if len(recent) >= 20:
        response["error"] = "Đang đọc nhiều đoạn liên tiếp. Hãy đợi một phút rồi thử lại."
    else:
        st.session_state["_speech_audio_requests"] = recent + [now]
        try:
            response["audio"] = base64.b64encode(free_speech_audio(request["text"], request["lang"])).decode("ascii")
        except Exception:
            response["error"] = "Giọng đọc trực tuyến hiện chưa đáp ứng. Hãy thử lại hoặc chọn giọng cài trên máy."
    state["response"] = response
    st.rerun(scope="fragment")
