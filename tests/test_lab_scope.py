from copy import deepcopy
import ast
import hashlib
import json
from pathlib import Path
import unittest

from services.academic_context import subjects_for_grade
from services.lab_scope import preset_lab_label, preset_lab_note


class TestLabScope(unittest.TestCase):
    def test_existing_library_labels_and_payloads_remain_intact(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / 'tests/fixtures/pr6_lab_presets_payload_sha256.json').read_text(encoding='utf-8'))
        nodes = [n.value for n in ast.walk(ast.parse((root / 'app.py').read_text(encoding='utf-8')))
                 if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'available_labs' for t in n.targets)]
        digest = hashlib.sha256('\n'.join(ast.dump(n, include_attributes=False) for n in nodes).encode()).hexdigest()
        self.assertEqual(len(nodes), manifest['count'])
        self.assertEqual(digest, manifest['sha256'])

    def test_higher_grade_preset_is_explicitly_an_extension(self):
        for grade in range(6, 12):
            value = preset_lab_label('Hàm bậc ba (KNTT 12)', 'Toán', grade)
            self.assertIn('Mở rộng, nhãn lớp 12', value)
            self.assertNotIn('KNTT', value)

    def test_same_grade_is_reference_not_textbook_certification(self):
        value = preset_lab_label('Hàm bậc ba (KNTT 12)', 'Toán', 12)
        self.assertIn('Mẫu tham khảo, nhãn lớp 12', value)
        self.assertNotIn('KNTT', value)

    def test_untagged_tools_do_not_get_an_invented_curriculum_grade(self):
        value = preset_lab_label('Hình hộp chữ nhật (3D)', 'Toán', 6)
        self.assertTrue(value.startswith('[Công cụ minh họa]'))

    def test_all_context_notes_do_not_claim_to_reconstruct_the_current_lesson(self):
        presets = {'Hàm bậc ba (KNTT 12)': {'type': 'func_3', 'a': 1, 'b': -3, 'c': 0, 'd': 2}}
        original = deepcopy(presets)
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    note = preset_lab_note(subject, grade)
                    self.assertIn(f'lớp {grade}', note)
                    self.assertIn('không tự lấy', note)
                    self.assertIn('chưa phải đối chiếu SGK', note)
                    for label in presets:
                        self.assertTrue(preset_lab_label(label, subject, grade))
        self.assertEqual(presets, original)
