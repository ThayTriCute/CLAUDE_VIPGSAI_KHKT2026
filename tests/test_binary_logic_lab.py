import json
import unittest
from services.lab_scope import binary_logic_state, reviewed_logic_lab_request, is_local_logic_command
from services.curriculum_policy import lesson_generation_request

TOPIC = 'Tin học 11 - Định hướng Khoa học máy tính, KNTT, Bài 4: Bên trong máy tính'
COMMAND = 'Cổng logic và cộng hai bit'

class BinaryLogicLabTests(unittest.TestCase):
    def test_complete_truth_table_and_half_adder_numeric_value(self):
        expected = [(0,0,0,0,0,0,0), (0,1,0,1,1,0,0),
                    (1,0,0,1,1,0,1), (1,1,1,1,0,1,0)]
        for a,b,and_bit,or_bit,s,c,y in expected:
            result = binary_logic_state(a,b)
            self.assertEqual([result[k] for k in ('and_bit','or_bit','sum_bit','carry_bit','a_and_not_b')],
                             [and_bit,or_bit,s,c,y])
            self.assertEqual(result['not_a'],1-a)
            self.assertEqual(result['not_b'],1-b)
            self.assertEqual(int(result['binary_sum'],2),a+b)
    def test_non_bits_cannot_be_silently_coerced(self):
        for value in (-1,2,0.5,'1',None,True):
            with self.assertRaises(ValueError): binary_logic_state(value,0)
            with self.assertRaises(ValueError): binary_logic_state(0,value)
    def test_only_explicit_command_with_exact_reviewed_model_routes_locally(self):
        self.assertTrue(is_local_logic_command(COMMAND))
        payload=reviewed_logic_lab_request(COMMAND,'Tin học',11,TOPIC)
        self.assertEqual(payload['type'],'binary_logic')
        self.assertTrue(payload['sources'])
        for subject,grade,topic,command in [('Tin học',10,TOPIC,COMMAND),('Toán học',11,TOPIC,COMMAND),
                ('Tin học',11,'Other topic',COMMAND),('Tin học',11,TOPIC,'Other command')]:
            self.assertIsNone(reviewed_logic_lab_request(command,subject,grade,topic))
    def test_missing_reviewed_local_logic_command_cannot_fall_through_to_model(self):
        import ast
        from pathlib import Path
        tree=ast.parse(Path('app.py').read_text(encoding='utf-8'))
        assignment=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and
                        any(isinstance(t,ast.Name) and t.id=='local_workshop_requested' for t in n.targets))
        self.assertIn('is_local_logic_command(lab_command)',ast.unparse(assignment.value))
        branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and
                    all(t in ast.unparse(n.test) for t in ('lab_clicked','explicit_local_model is None','not local_workshop_requested')))
        self.assertIn('not local_workshop_requested',ast.unparse(branch.test))

    def test_local_model_and_answer_data_do_not_add_generation_payload(self):
        _,user=lesson_generation_request('Tin học',11,TOPIC)
        review=json.loads(user.splitlines()[0])['reviewed_requirements_source']
        self.assertNotIn('source_workshop',review)
        self.assertNotIn('content_corrections',review)

if __name__ == '__main__': unittest.main()
