"""Local Streamlit integration sweep; NO live AI, NO academic certification.

Run from repository root: python scripts/verify_all_context_ui.py OUTPUT.json
Uses an isolated database and synthetic provider/bank responses in all contexts.
"""
import json
from pathlib import Path
import sys
import tempfile
import time
import faulthandler
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from services.academic_context import subjects_for_grade
from tests.lesson_samples import complete_lesson
from tests.test_all_context_publication import sample_exam
import database


def verify(output):
    rows = []
    failures = []
    started = time.monotonic()
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        previous = json.loads(output.read_text(encoding='utf-8'))
        failures = previous.get('earlier_failures', []) + [r for r in previous.get('rows', []) if 'error' in r]
        rows = [r for r in previous.get('rows', []) if r.get('station1') and r.get('station3') and 'error' not in r]
    completed = {(r['subject'], r['grade']) for r in rows}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        isolated = database.DatabaseManager(Path(folder) / 'ui_matrix.db')
        with patch.object(database, 'db_manager', isolated), patch('google.genai.Client') as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            for grade in range(6, 13):
                if all((subject, grade) in completed for subject in subjects_for_grade(grade)):
                    continue
                at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60)
                at.secrets['GEMINI_API_KEY'] = 'test-only-key'
                cold_start = time.monotonic()
                at.run()
                cold_start_seconds = round(time.monotonic() - cold_start, 3)
                next(s for s in at.selectbox if s.label == '🎯 Chọn khối lớp:').select(f'Lớp {grade}').run()
                for subject in subjects_for_grade(grade):
                    if (subject, grade) in completed:
                        continue
                    row = {'subject': subject, 'grade': grade, 'station1': False,
                           'station3': False, 'academic_verified': False}
                    before_calls = generate.call_count
                    try:
                        row['stage'] = 'station1_select_context'
                        row['app_start_seconds'] = cold_start_seconds
                        stage_start = time.monotonic()
                        at.session_state['selected_station'] = '📖 Trạm 1: Học Tập & Phòng Lab'
                        faulthandler.dump_traceback_later(35)
                        next(s for s in at.selectbox if s.label == '📚 Môn học cần hỗ trợ:').select(subject).run()
                        faulthandler.cancel_dump_traceback_later()
                        assert not at.exception, [e.message for e in at.exception]
                        row['station1_context_seconds'] = round(time.monotonic() - stage_start, 3)
                        theory = f'Môn: {subject}; lớp: {grade}\nNgữ liệu QA mô phỏng, không phải bài giảng đã thẩm định. Ký hiệu thử $\\frac{{1}}{{2}}$.'
                        generate.return_value = SimpleNamespace(text=complete_lesson(theory), candidates=[])
                        next(t for t in at.text_input if 'Bài học cần chiếm lĩnh' in t.label).set_value('Kiểm thử tích hợp')
                        stage_start = time.monotonic()
                        next(b for b in at.button if b.label == '🚀 Soạn bài học').click().run()
                        row['station1_mock_generation_seconds'] = round(time.monotonic() - stage_start, 3)
                        assert not at.exception, [e.message for e in at.exception]
                        assert at.session_state['current_lesson_context'] == (subject, grade)
                        assert len(at.session_state['parsed_quiz']) == 3
                        displayed = '\n'.join(str(m.value) for m in at.markdown)
                        assert displayed.count('Bước 1: Tìm hiểu đề') == 2
                        assert displayed.count('Bước 4: Kiểm tra và nhìn lại') == 2
                        assert 'PRIVATE_REASONING' not in displayed
                        assert sum(r.label.startswith('Chọn đáp án câu ') for r in at.radio) == 3
                        assert any('infographic chữ viết tay' in e.label for e in at.expander)
                        assert 'youtube.com/results?' in displayed
                        row['station1'] = True

                        row['stage'] = 'station3_open'
                        stage_start = time.monotonic()
                        next(b for b in at.button if b.key == 'top_nav_station_2').click().run()
                        row['station3_open_seconds'] = round(time.monotonic() - stage_start, 3)
                        assert not at.exception, [e.message for e in at.exception]
                        assert sum(b.key == 't3_create_practice_exam' for b in at.button) == 1
                        if subject != 'Ngữ văn':
                            for label, count in (('Số câu TN P.I:', 1), ('Số câu Đ/S P.II:', 0), ('Số câu TLN P.III:', 0)):
                                next(n for n in at.number_input if n.label == label).set_value(count)
                        exam = sample_exam(subject, grade)
                        if subject != 'Ngữ văn':
                            exam['p2'], exam['p3'] = [], []
                        with patch('real_exam_engine.generate_blended_real_exam', return_value=exam):
                            row['stage'] = 'station3_create'
                            faulthandler.dump_traceback_later(40)
                            stage_start = time.monotonic()
                            next(b for b in at.button if b.key == 't3_create_practice_exam').click().run()
                            row['station3_mock_generation_seconds'] = round(time.monotonic() - stage_start, 3)
                            faulthandler.cancel_dump_traceback_later()
                        assert not at.exception, [e.message for e in at.exception]
                        assert at.session_state['exam_state'] == 'testing'
                        assert at.session_state['exam_context']['subject'] == subject
                        assert at.session_state['exam_context']['grade'] == f'Lớp {grade}'
                        assert at.session_state['exam_data']['grade'] == grade
                        assert generate.call_count - before_calls == 1, 'Unexpected AI fallback during bank test'
                        row['station3'] = True
                        row['stage'] = 'complete'
                    except Exception as error:
                        row['error'] = f'{type(error).__name__}: {error}'[:1200]
                    rows.append(row)
                    print(json.dumps(row, ensure_ascii=False), flush=True)
                    output.write_text(json.dumps({'scope': 'Local UI with synthetic AI/bank responses; not academic certification',
                        'live_ai_calls': 0, 'elapsed_seconds': round(time.monotonic()-started, 2),
                        'earlier_failures': failures, 'rows': rows},
                        ensure_ascii=False, indent=2), encoding='utf-8')
                    if 'error' in row:
                        # Do not compound a broken UI state across remaining cases.
                        return 1
    return 0


if __name__ == '__main__':
    sys.exit(verify(sys.argv[1]))
