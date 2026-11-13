"""Small, deterministic guards for persisted Streamlit widget state."""


def retained_subject_index(active_context, options):
    """Recover the last subject after a failed run cleans up widget state.

    Only retain a subject still offered by the selected grade. This does not
    restore attempts, chat, credentials, or another grade's lesson.
    """
    previous = str(active_context or '').partition('_')[2]
    return options.index(previous) if previous in options else 0


def purge_context_bound_widget_keys(state, previous=None):
    """Reset Trạm-3 topic checkboxes and stable lesson selectors on context flip.

    Lesson/topic selectboxes dùng key ổn định (`kntt_lesson_sel`, `topic_input_main`);
    checkbox chuyên đề dùng `cb_t3_*`. Không xóa `$$ID-…` nội bộ Streamlit.
    """
    doomed = []
    for key in list(state.keys()):
        sk = str(key)
        if sk.startswith(("cb_t3_", "cb_")) and "$$ID-" not in sk:
            doomed.append(key)
    for stable in ("kntt_lesson_sel", "topic_input_main"):
        if stable in state:
            doomed.append(stable)
    # Legacy keys gắn môn/lớp (bản cũ)
    prev = str(previous) if previous else ""
    if prev:
        for key in list(state.keys()):
            sk = str(key)
            if prev in sk and any(
                m in sk
                for m in (
                    "kntt_lesson_sel_",
                    "topic_input_",
                    "area_custom_prompt_main_",
                    "area_custom_prompt_gv_",
                )
            ) and "$$ID-" not in sk:
                doomed.append(key)
    for key in dict.fromkeys(doomed):
        try:
            del state[key]
        except Exception:
            state.pop(key, None)
    return len(doomed)


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
    purge_context_bound_widget_keys(state, previous=previous)


def valid_option_index(value, option_count):
    """Keep a real in-range index; reset stale labels/types to the first option.

    A label or numeric string is not an index: coercing it can silently select
    another exam after the subject/grade catalogue has changed.
    """
    if type(value) is int and 0 <= value < option_count:
        return value
    return 0
