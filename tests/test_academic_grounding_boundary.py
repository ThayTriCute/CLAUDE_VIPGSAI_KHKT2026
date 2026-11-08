import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from services.curriculum_policy import (
    ACADEMIC_GROUNDING_GUIDANCE, with_academic_grounding, legal_references,
)


class AcademicGroundingBoundaryTests(unittest.TestCase):
    def test_systemwide_verification_contract_is_in_injected_instruction_once(self):
        prepared = with_academic_grounding('KEEP REQUESTED SCHEMA')
        self.assertTrue(prepared.startswith('KEEP REQUESTED SCHEMA'))
        self.assertEqual(prepared.count('KIỂM CHỨNG TOÀN HỆ THỐNG:'), 1)
        for clause in ('mọi môn/lớp, Trạm1–2–3 và model dự phòng',
                       'không thay nghiệm thu kiến thức',
                       'không tự nhận đã chạy kiểm local'):
            self.assertIn(clause, prepared)
        self.assertEqual(with_academic_grounding(prepared), prepared)

    def test_cross_station_closure_rules_reach_shared_api_instruction(self):
        from services.philosophy_rotation import GUIDANCE
        prepared = with_academic_grounding('Requested JSON schema')
        self.assertIn(GUIDANCE, prepared)
        self.assertEqual(with_academic_grounding(prepared), prepared)
        self.assertIn('Trạm1,2,3', prepared)

    def test_civic_history_review_contract_preserves_schema_and_scope(self):
        prepared = with_academic_grounding('ONLY JSON schema X')
        self.assertTrue(prepared.startswith('ONLY JSON schema X'))
        for clause in ('Lịch sử, GDCD và Giáo dục kinh tế và pháp luật',
                       'VniTeach, Nền tảng Tập huấn NXBGDVN và Trường Học Số Quốc Gia',
                       'không hiểu thành ba loại SGK/SGV/SBT',
                       'không phải ba bằng chứng độc lập',
                       'Bài mẫu không đại diện toàn cuốn',
                       'điều/khoản liên quan, ngày hiệu lực',
                       'không tự gán tác giả',
                       'không chứng nhận đạt pháp luật Việt Nam'):
            self.assertIn(clause, prepared)
        self.assertEqual(with_academic_grounding(prepared), prepared)

    def test_membrane_counterexample_is_in_shared_system_guidance(self):
        prepared = with_academic_grounding('Keep requested JSON schema')
        for clause in ('chủ động thứ cấp', 'gradient điện hóa', 'tính thấm màng/chất tan'):
            self.assertIn(clause, prepared)
        self.assertEqual(with_academic_grounding(prepared), prepared)

    def test_both_transports_apply_before_fallback(self):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        for name in ('call_gemini_with_fallback', 'stream_gemini_with_fallback'):
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name) and n.func.id == 'with_academic_grounding']
            self.assertEqual(len(calls), 1)
            self.assertLess(calls[0].lineno, min(n.lineno for n in ast.walk(node) if isinstance(n, ast.For)))

    def test_metadata_uses_effective_registry_and_keeps_schema(self):
        with patch('services.curriculum_policy.policy_evaluation_date', return_value='2026-11-07'):
            prepared = with_academic_grounding('ONLY JSON schema X')
            self.assertTrue(prepared.startswith('ONLY JSON schema X'))
            self.assertEqual(with_academic_grounding(prepared), prepared)
            metadata = json.loads(prepared.split('Ngày áp dụng: 2026-11-07\n', 1)[1])
            self.assertEqual([r['code'] for r in metadata],
                             [r['code'] for r in legal_references('2026-11-07')])
            self.assertNotIn('89/2026/TT-BGDĐT', [r['code'] for r in metadata])
            self.assertIn('Thiếu nguồn', ACADEMIC_GROUNDING_GUIDANCE)

    def test_2026_source_does_not_reuse_2022_original(self):
        data = json.loads(Path('data/legal_references.json').read_text(encoding='utf-8'))
        row = next(r for r in data['documents'] if r['code'] == '13/2026/TT-BGDĐT')
        self.assertIn('docid=217189', row['url'])
        self.assertNotIn('original_copy_url', row)
        self.assertIn('not_full_text', row['verification_scope'])
