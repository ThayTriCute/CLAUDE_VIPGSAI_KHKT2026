"""Independent review sidecars; never feed bank questions into Station1."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from services.academic_context import academic_context
from services.cognitive_levels import assessment_content_hash, validate_cognitive_review

REGISTRY = Path(__file__).resolve().parents[1] / 'data/cognitive_reviews.json'


def review_binding(question, shared_context=None):
    clean = {k: v for k, v in question.items() if k not in ('cognitive_audit', 'level_claimed')}
    return {'question': clean, 'shared_context': shared_context or {}}


def _load_reviews(registry_path=None):
    try:
        payload = json.loads(Path(registry_path or REGISTRY).read_text(encoding='utf-8'))
        if payload.get('schema_version') != 1 or not isinstance(payload.get('reviews'), dict):
            return {}
        return payload['reviews']
    except (OSError, ValueError, TypeError, AttributeError):
        return {}


def independent_question_audit(question, *, subject, grade, topic, purpose,
                               shared_context=None, as_of=None, registry_path=None, _reviews=None):
    subject, grade = academic_context(subject, grade)
    today = as_of or datetime.now(timezone(timedelta(hours=7))).date().isoformat()
    bound = review_binding(question, shared_context)
    digest = assessment_content_hash(bound)
    reviews = _load_reviews(registry_path) if _reviews is None else _reviews
    review = reviews.get(digest, {})
    if not isinstance(review, dict):
        review = {}
    result = validate_cognitive_review(bound, review, subject=subject, grade=grade,
                                       topic=str(topic or ''), as_of=today)
    if review.get('assessment_purpose') != purpose:
        result = dict(result, verified=False, status='blocked', reviewed_level='',
                      issues=sorted(set(result['issues'] + ['review_purpose_mismatch'])))
    return dict(result, content_sha256=digest,
                approval_scope='Independent record validity only; not Ministry certification',
                delivery_status='review_record_valid' if result['verified'] else 'needs_teacher_review')


def independent_exam_audit(exam, subject, grade, *, as_of=None, registry_path=None):
    rows = []
    reviews = _load_reviews(registry_path)
    # A question reviewed in one assessment context cannot authorize another.
    assessment_context = {key: exam[key] for key in (
        'exam_type', 'assessment_purpose', 'exam_session', 'curriculum',
        'textbook', 'textbook_series') if key in exam}
    groups = [(p, exam.get(p, [])) for p in ('p1', 'p2', 'p3', 'part_viet')]
    reading = exam.get('part_doc_hieu')
    if isinstance(reading, (dict, list)):
        groups.append(('part_doc_hieu', reading.get('questions', []) if isinstance(reading, dict) else reading))
    for part, questions in groups:
        if not isinstance(questions, list):
            continue
        for index, question in enumerate(questions):
            if not isinstance(question, dict):
                continue
            shared = {'assessment_context': assessment_context} if assessment_context else {}
            if part == 'part_doc_hieu':
                shared['reading'] = reading
            kwargs = dict(subject=subject, grade=grade, topic=question.get('topic', exam.get('topic', '')),
                          purpose='station3_assessment', as_of=as_of, _reviews=reviews)
            rows.append(dict(part=part, question=index + 1,
                             **independent_question_audit(question, shared_context=shared, **kwargs)))
            for si, statement in enumerate(question.get('stmts', []) or []):
                if isinstance(statement, dict):
                    parent = review_binding(question, shared)
                    rows.append(dict(part=part, question=index + 1, statement=si + 1,
                                     **independent_question_audit(statement, shared_context=parent, **kwargs)))
    return {'rows': rows, 'verified_records': sum(r['verified'] for r in rows),
            'pending_records': sum(not r['verified'] for r in rows),
            'scope': 'Per-item independent review lookup; no whole-exam semantic approval'}


def independent_lesson_quiz_audit(questions, subject, grade, topic, lesson, *, as_of=None,
                                  registry_path=None):
    reviews = _load_reviews(registry_path)
    return [independent_question_audit(question, subject=subject, grade=grade, topic=topic,
                purpose='station1_self_study', shared_context={'lesson': lesson},
                as_of=as_of, _reviews=reviews)
            for question in questions if isinstance(question, dict)]
