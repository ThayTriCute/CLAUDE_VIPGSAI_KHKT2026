import hashlib,json,lzma,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from services.lesson_sources import local_textbook_grounding
from services.curriculum_policy import lesson_generation_request,with_academic_grounding

class LocalTextbookGroundingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.folder=self.root/'reviewed_lesson_packets';self.folder.mkdir()
        self.env=patch.dict(os.environ,{'GSAI_TEXTBOOK_ARCHIVE_ROOT':str(self.root)});self.env.start();self.addCleanup(self.env.stop)
        self.payload=dict(schema_version=1,review_status='source_reviewed',subject='Lịch sử',grade=10,topic='Exact lesson',sources=[dict(title='Reviewed source',url='https://taphuan.nxbgd.vn/book',locator='page6',edition_note='Scope checked',reviewed_excerpt='A source fact not supplied in the topic')])
        self.write_packet()
    def write_packet(self):
        self.packet=self.folder/'lesson.json.xz';self.packet.write_bytes(lzma.compress(json.dumps(self.payload).encode()))
        self.entry=dict(subject='Lịch sử',grade=10,topic='Exact lesson',path=self.packet.name,sha256=hashlib.sha256(self.packet.read_bytes()).hexdigest())
        self.write_index()
    def write_index(self):
        (self.folder/'index.json').write_text(json.dumps(dict(entries=[self.entry])),encoding='utf-8')
    def test_actual_decoded_excerpt_reaches_lesson_request_without_changing_system_or_task(self):
        system,user=lesson_generation_request('Lịch sử',10,'Exact lesson')
        context=json.loads(user.splitlines()[0]);source=context['textbook_grounding']
        self.assertEqual(source['status'],'reviewed_excerpt_packet_loaded')
        self.assertIn('A source fact not supplied in the topic',source['sources'][0]['reviewed_excerpt'])
        self.assertFalse(source['semantic_acceptance']);self.assertFalse(source['online_lookup_performed'])
        self.assertNotIn('A source fact',system)
        self.assertEqual(local_textbook_grounding('Lịch sử',11,'Exact lesson')['status'],'no_exact_reviewed_packet')
        self.assertEqual(local_textbook_grounding('Lịch sử',10,'Other lesson')['status'],'no_exact_reviewed_packet')
    def test_tampered_packet_cannot_be_sent_as_reviewed_source(self):
        self.packet.write_bytes(b'wrong')
        result=local_textbook_grounding('Lịch sử',10,'Exact lesson')
        self.assertEqual(result['status'],'invalid_reviewed_packet');self.assertNotIn('sources',result)
    def test_path_traversal_is_rejected(self):
        self.entry['path']='../outside.json.xz';self.write_index()
        self.assertEqual(local_textbook_grounding('Lịch sử',10,'Exact lesson')['status'],'invalid_reviewed_packet')
    def test_mismatched_unreviewed_or_oversized_content_is_not_evidence(self):
        for change in [dict(review_status='draft'),dict(grade=11),dict(topic='Wrong'),dict(sources=[]),dict(sources=['bad']),dict(sources=[dict(title='x',url='https://unverified.example/book',locator='p1',edition_note='x',reviewed_excerpt='x')]),dict(coverage_note='x'*70000)]:
            original=dict(self.payload);self.payload.update(change);self.write_packet()
            self.assertEqual(local_textbook_grounding('Lịch sử',10,'Exact lesson')['status'],'invalid_reviewed_packet')
            self.payload=original
    def test_missing_archive_explicit_and_shared_api_rules_require_local_first(self):
        with patch.dict(os.environ,{'GSAI_TEXTBOOK_ARCHIVE_ROOT':str(self.root/'missing')}):
            self.assertEqual(local_textbook_grounding('Lịch sử',10,'Exact lesson')['status'],'archive_unavailable')
        rules=with_academic_grounding('Keep schema')
        self.assertIn('Trạm1 sinh bài phải căn cứ nguồn local XZ trước',rules)
        self.assertIn('API không tự mở ổ F hoặc tra web',rules)
        self.assertIn('KNTT thống nhất',rules)
        self.assertEqual(with_academic_grounding(rules),rules)

if __name__=='__main__':unittest.main()
