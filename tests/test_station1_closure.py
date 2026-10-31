import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from tests.test_expert_patch_regressions import load_function


class Station1ClosureTests(unittest.TestCase):
    def test_explicit_no_more_questions_is_a_conclusion(self):
        detect = load_function('detect_student_concluded_intent')
        for message in ('Dạ em không còn thắc mắc.', 'Em hiểu bài rồi, không có thắc mắc.', 'Dạ hết thắc mắc rồi thầy.'):
            with self.subTest(message=message):
                self.assertTrue(detect(message))

    def test_new_question_or_unresolved_confusion_is_not_closed(self):
        detect = load_function('detect_student_concluded_intent')
        for message in ('Em không còn thắc mắc phần trước nhưng thầy cho em hỏi thêm?', 'Em chưa hết thắc mắc.', 'Em không hiểu.', 'Em chưa hết câu hỏi.', 'Em hiểu bài rồi nhưng không hiểu vì đổi dấu.', 'Em hiểu bài rồi nhưng chỗ này tại sao đổi dấu?'):
            with self.subTest(message=message):
                self.assertFalse(detect(message))

    def closure_try(self):
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8'))
        return next(node for node in ast.walk(tree) if isinstance(node, ast.Try) and
                    any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='t1_ans' for t in n.targets) for n in node.body))

    def run_reply(self, reply='', failure=False):
        class State(dict):
            __getattr__ = dict.__getitem__
        state=State(tram1_chat_history=[])
        register=Mock()
        st=SimpleNamespace(session_state=state, write_stream=Mock(side_effect=RuntimeError('offline') if failure else None,return_value=reply),error=Mock())
        ns=dict(st=st,t1_input='Em không còn thắc mắc.',t1_hist_ctx='',t1_sys_inst='',subject='Toán học',student_name='QA',
            detect_student_concluded_intent=lambda *a:True,get_unique_philosophical_lesson=lambda *a:{'lesson':'Kiên trì','author':'FixtureAuthor','origin':'fixture','quote':'test'},get_cross_station_pedagogical_context=lambda *a:'',register_station_closure=register,
            stream_gemini_with_fallback=Mock(return_value=iter(())),sanitize_katex_latex=lambda s:s)
        exec(compile(ast.Module(body=[self.closure_try()],type_ignores=[]),'t1-closure-try','exec'),ns)
        self.last_prompt = ns['stream_gemini_with_fallback'].call_args.args[0]
        return register

    def test_closure_keeps_lesson_without_unverified_quote_attribution(self):
        self.run_reply(reply='Kiên trì và trung thực.')
        self.assertIn('Kiên trì', self.last_prompt)
        self.assertIn('không gán tác giả', self.last_prompt)
        self.assertNotIn('FixtureAuthor', self.last_prompt)
        self.assertIn('không nhầm đạo hàm cấp một', self.last_prompt)

    def test_station2_closure_prompt_does_not_depend_on_station1_locals(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8'))
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='prompt_msg' for t in n.targets)
            and 'TRẠM 2 (CLOSURE)' in ast.dump(n.value))
        ns=dict(t2_cross_ctx='',history_context='',q='Em hiểu rồi',student_name='QA',
            t2_quote_data={'lesson':'Trung thực','author':'QA','origin':'fixture','quote':'test'})
        exec(compile(ast.Module(body=[node],type_ignores=[]),'t2-closure-isolation','exec'),ns)
        self.assertIn('Trạm 3',ns['prompt_msg'])

    def test_stream_error_or_empty_reply_does_not_register_closure(self):
        self.run_reply(failure=True).assert_not_called()
        self.run_reply(reply='').assert_not_called()

    def test_new_lesson_chat_does_not_inherit_previous_understanding(self):
        class State(dict):
            __getattr__ = dict.__getitem__
            __setattr__ = dict.__setitem__
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8'))
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.If) and
                    'tram1_active_chat_key' in ast.dump(n.test))
        from services.academic_context import subjects_for_grade
        for grade in range(6,13):
            for subject in subjects_for_grade(grade):
                state=State(tram1_active_chat_key='previous',tram1_chat_history=[],
                    tram1_understood=True,tram1_closure_info={'quote':'old'},
                    used_philosophical_quotes=['old'],current_topic='New lesson')
                ns=dict(st=SimpleNamespace(session_state=state),chat_context_key=f'{subject}_{grade}_new',student_name='QA',subject=subject)
                exec(compile(ast.Module(body=[node],type_ignores=[]),'t1-chat-reset','exec'),ns)
                self.assertFalse(state.get('tram1_understood'), (subject,grade))
                self.assertNotIn('tram1_closure_info',state)
                self.assertEqual(state['used_philosophical_quotes'],['old'])

    def test_successful_reply_registers_closure_once(self):
        self.run_reply(reply='Em hãy giữ tính trung thực và kiên trì trong học tập.').assert_called_once()


if __name__ == '__main__':
    unittest.main()
