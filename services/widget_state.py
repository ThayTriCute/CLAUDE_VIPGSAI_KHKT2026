"""Small, deterministic guards for persisted Streamlit widget state."""


def switch_exam_request_context(state, previous, current):
    """Keep each subject/grade's draft, without carrying it into another one.

    Run before rendering the request widgets, as part of the existing context
    switch. Exam-specific request text belongs to the old attempt, not a draft.
    """
    if previous is None or previous == current:
        return
    keys = ("custom_matrix_prompt", "area_custom_prompt_main", "area_custom_prompt_gv")
    drafts = state.setdefault("exam_request_drafts", {})
    drafts[previous] = {key: state[key] for key in keys if key in state}
    for key in (*keys, "custom_request_text"):
        state.pop(key, None)
    for key, value in drafts.get(current, {}).items():
        if key in keys:
            state[key] = value


def valid_option_index(value, option_count):
    """Keep a real in-range index; reset stale labels/types to the first option.

    A label or numeric string is not an index: coercing it can silently select
    another exam after the subject/grade catalogue has changed.
    """
    if type(value) is int and 0 <= value < option_count:
        return value
    return 0


def cached_exam_label(item):
    """Render heterogeneous archive metadata for every subject/grade."""
    from datetime import date, datetime
    row = item if isinstance(item, dict) else {}
    def text(value, fallback):
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            return str(value).strip() or fallback
        return fallback
    stamp = row.get('saved_at')
    if isinstance(stamp, (date, datetime)):
        stamp = stamp.isoformat()
    stamp = text(stamp, '')[:10]
    return f"Mã đề {text(row.get('code'), 'Chưa rõ')} - {text(row.get('topic'), 'Chuyên đề ôn tập')} ({stamp})"
