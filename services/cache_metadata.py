"""Safe archive labels independent of long-lived widget-state imports."""

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


def cached_exam_widget_key(subject, grade, labels):
    """Bind selection to context and actual catalogue order, not an old index."""
    import hashlib
    import json
    payload = json.dumps([str(subject), str(grade), list(labels)], ensure_ascii=False)
    return 'sel_cached_exam_t3_' + hashlib.sha256(payload.encode()).hexdigest()[:20]
