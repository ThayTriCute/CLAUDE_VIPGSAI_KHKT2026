"""Preserve explicit review holds at every archive-to-delivery boundary."""

def exam_delivery_held(exam):
    if not isinstance(exam, dict):
        return True
    if exam.get('source_review_issues'):
        return True
    wrapped = exam.get('data')
    if isinstance(wrapped, dict) and exam_delivery_held(wrapped):
        return True
    groups = [exam.get(p, []) for p in ('p1', 'p2', 'p3', 'part_viet')]
    reading = exam.get('part_doc_hieu')
    if isinstance(reading, dict):
        groups.append(reading.get('questions', []))
    elif isinstance(reading, list):
        groups.append(reading)
    for group in groups:
        if not isinstance(group, list):
            continue
        for question in group:
            if isinstance(question, dict):
                if question.get('source_review_issues'):
                    return True
                if any(isinstance(s, dict) and s.get('source_review_issues')
                       for s in question.get('stmts', []) or []):
                    return True
    return False
