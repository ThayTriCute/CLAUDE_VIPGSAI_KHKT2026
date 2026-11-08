import ast,json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from services.lab_scope import reviewed_workshop_request,evaluate_source_workshop
from services.curriculum_policy import lesson_generation_request

TOPICS=[('Lịch sử','Hiện thực lịch sử và lịch sử được con người nhận thức — Lịch sử 10, KNTT, Bài 1'),('Địa lý','Hệ quả địa lí các chuyển động của Trái Đất — Địa lí 10, KNTT, Bài 5'),('Giáo dục kinh tế và pháp luật','Khái niệm, đặc điểm và vai trò của pháp luật — GDKT&PL 10, KNTT, Bài 11')]
COMMAND='Đối chiếu tư liệu theo bài học'
class SourceWorkshopTests(unittest.TestCase):
    def test_three_topics_are_source_grounded_local_and_independent(self):
        for subject,topic in TOPICS:
            data=reviewed_workshop_request(COMMAND,subject,10,topic)
            self.assertEqual(data['type'],'source_workshop');self.assertTrue(data['sources'])
            qs=data['workshop']['questions'];answers=[x['correct'] for x in qs]
            self.assertEqual(evaluate_source_workshop(qs,answers)['score'],len(qs))
            wrong=[(x['correct']+1)%len(x['options']) for x in qs]
            self.assertEqual(evaluate_source_workshop(qs,wrong)['score'],0)
            data['workshop']['cards'][0]['text']='MUTATED'
            self.assertNotEqual(reviewed_workshop_request(COMMAND,subject,10,topic)['workshop']['cards'][0]['text'],'MUTATED')
            self.assertIsNone(reviewed_workshop_request(COMMAND,subject,11,topic))
            self.assertIsNone(reviewed_workshop_request(COMMAND,subject,10,'Other lesson'))
            self.assertIsNone(reviewed_workshop_request('Other lab command',subject,10,topic))
    def test_incomplete_or_out_of_range_choices_do_not_score(self):
        qs=reviewed_workshop_request(COMMAND,*TOPICS[0][:1],10,TOPICS[0][1])['workshop']['questions']
        for choices in [[],[None]*len(qs),[-1]*len(qs),[999]*len(qs),[True]*len(qs)]:
            with self.assertRaises(ValueError):evaluate_source_workshop(qs,choices)
    def test_missing_local_workshop_does_not_fall_through_to_paid_model(self):
        from services.lab_scope import is_local_workshop_command
        self.assertTrue(is_local_workshop_command(COMMAND))
        self.assertIsNone(reviewed_workshop_request(COMMAND,'Lịch sử',12,'Missing'))
        tree=ast.parse(Path('app.py').read_text(encoding='utf-8'))
        branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and
            all(x in ast.unparse(n.test) for x in ('lab_clicked','explicit_local_model is None','not local_workshop_requested')))
        self.assertIn('not local_workshop_requested',ast.unparse(branch.test))

    def test_invalid_workshop_cannot_route_to_renderer(self):
        with patch('services.lesson_sources.reviewed_lesson_sources',return_value=dict(status='reviewed_requirements_source',source_workshop=dict(title='bad',cards=[],questions=[]))):
            self.assertIsNone(reviewed_workshop_request(COMMAND,'Lịch sử',10,'x'))
    def test_generation_does_not_pay_for_local_workshop_answer_data(self):
        for subject,topic in TOPICS:
            _,prompt=lesson_generation_request(subject,10,topic)
            context=json.loads(prompt.splitlines()[0])
            self.assertNotIn('source_workshop',context['reviewed_requirements_source'])
    def test_ui_renderer_runs_locally_with_clear_feedback_and_source_scope(self):
        from tests.test_expert_patch_regressions import load_function
        data=reviewed_workshop_request(COMMAND,'Lịch sử',10,TOPICS[0][1]);answers=[q['correct'] for q in data['workshop']['questions']]
        class Fake:
            session_state={}
            def __init__(self):self.successes=[];self.warnings=[];self.seen=[];self.pos=0
            def markdown(self,x):self.seen.append(str(x))
            def caption(self,x):self.seen.append(str(x))
            def write(self,x):self.seen.append(str(x))
            def columns(self,n):return [self]*n
            def radio(self,*args,**kwargs):x=answers[self.pos];self.pos+=1;return x
            def button(self,*args,**kwargs):return True
            def success(self,x):self.successes.append(x)
            def warning(self,x):self.warnings.append(x)
            def expander(self,*args,**kwargs):return self
            def __enter__(self):return self
            def __exit__(self,*args):return False
        st=Fake();render=load_function('render_smart_lab',st=st)
        render(data,'Lịch sử');self.assertIn('3/3',st.successes[0]);self.assertFalse(st.warnings)
        self.assertTrue(any('SGK' in x for x in st.seen));self.assertTrue(any('không phải trích nguyên văn' in x for x in st.seen))

if __name__=='__main__':unittest.main()
