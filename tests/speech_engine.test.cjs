const assert = require('node:assert/strict');
const test = require('node:test');
const s = require('../assets/pedagogical_speech.js');

test('Vietnamese explanation remains Vietnamese in an English lesson',()=>{
 assert.equal(s.languageOf('Chọn đáp án đúng cho câu sau.', 'en'),'vi');
 assert.equal(s.languageOf('photosynthesis', 'en'),'en');
 assert.equal(s.languageOf('unprecedented', 'en'),'en');
 assert.equal(s.languageOf('café', 'en'),'en');
});
test('bilingual passage changes language without translating its content',()=>{
 const p=s.planSpeech('Photosynthesis là quá trình quan trọng. Choose the correct answer.', 'Tiếng Anh');
 assert.equal(p[0].lang,'en'); assert.ok(p.some(x=>x.lang==='vi'));
 assert.equal(p.at(-1).lang,'en');
 assert.ok(p.some(x=>x.text.includes('quá trình')));
});
test('manual override resolves short ambiguous words',()=>{
 assert.ok(s.planSpeech('to', 'Tiếng Anh','vi').every(p=>p.lang==='vi'));
 assert.ok(s.planSpeech('to', 'Toán học','en').every(p=>p.lang==='en'));
});
test('subject abbreviations do not leak into other subjects',()=>{
 assert.equal(s.replaceTerms('CT và TCĐ', 'Ngữ văn'),'CT và TCĐ');
 assert.equal(s.replaceTerms('TCĐ và BBT', 'Toán học'),'tiệm cận đứng và bảng biến thiên');
 assert.equal(s.replaceTerms('ADN', 'Sinh học'),'a đê en');
 assert.equal(s.replaceTerms('ADN', 'Ngữ văn'),'ADN');
});
test('nested fractions and roots retain numerator and denominator structure',()=>{
 const t=s.prepareText('Ta có $\\frac{1}{\\sqrt{x+1}}$.','vi','Toán học');
 assert.ok(t.includes('tử số 1')); assert.ok(t.includes('mẫu số')); assert.ok(t.includes('căn bậc hai'));
 assert.ok(t.includes('x cộng 1')); assert.ok(!t.includes('\\'));
});
test('less/greater signs cannot be removed as HTML',()=>{
 const t=s.prepareText('$x<y$ và $z>0$.','vi','Toán học');
 assert.ok(t.includes('x nhỏ hơn y')); assert.ok(t.includes('z lớn hơn 0'));
});
test('notin and inequalities are whole commands, not corrupt prefixes',()=>{
 const t=s.formulaSpeech('x\\notin A, x\\leq 2, y\\geq 3','vi');
 assert.ok(t.includes('không thuộc')); assert.ok(t.includes('nhỏ hơn hoặc bằng')); assert.ok(!t.includes('q'));
});
test('formula semicolons and multiline display math survive sentence chunking',()=>{
 const t=s.planSpeech('Xét $$x \\in (0; 1)\n\\Rightarrow x>0$$.','Toán học').map(p=>p.text).join(' ');
 assert.ok(t.includes('thuộc')); assert.ok(t.includes('suy ra')); assert.ok(t.includes('lớn hơn'));
});
test('chemical notation reads symbols without inventing a chemical name',()=>{
 const t=s.formulaSpeech('\\ce{2H2 + O2 -> 2H2O}', 'vi');
 assert.ok(t.includes('công thức hóa học')); assert.ok(t.includes('chỉ số 2')); assert.ok(t.includes('tạo thành'));
 assert.ok(!t.includes('axit'));
});
test('units expand only in supported scientific subject context',()=>{
 assert.equal(s.prepareText('3,5 kg và 10 cm','vi','Vật lý'),'3,5 ki lô gam và 10 xen ti mét');
 assert.equal(s.prepareText('3,5 kg','vi','Ngữ văn'),'3,5 kg');
 assert.equal(s.prepareText('biến m và số s','vi','Toán học'),'biến m và số s');
});
test('unknown or partial formulas stop clearly instead of silently deleting syntax',()=>{
 assert.throws(()=>s.prepareText('$\\unsupported{x}$','vi','Toán học'),/Chưa có cách đọc/);
 assert.throws(()=>s.prepareText('$x+1','vi','Toán học'),/chưa đầy đủ/);
});
test('long reading is complete and preserves decimals and final sentences',()=>{
 const input=Array.from({length:120},(_,i)=>`Sentence ${i} has value 3.14.`).join(' ');
 const p=s.planSpeech(input,'Tiếng Anh');
 assert.ok(p.length>10); assert.ok(p.every(x=>x.text.length<=240));
 assert.equal(p.map(x=>x.text).join(' '),input);
 assert.ok(p.at(-1).text.includes('119')); assert.ok(p.every(x=>x.lang==='en'));
});
test('voice selection cannot fall back to a different language',()=>{
 const en={voiceURI:'en',name:'US test',lang:'en-US'}, vi={voiceURI:'vi',name:'Vietnamese test',lang:'vi-VN'};
 assert.equal(s.chooseVoice([en], 'vi'), null);
 assert.equal(s.chooseVoice([vi,en], 'en','vi'),en);
 assert.equal(s.chooseVoice([vi,en], 'vi','vi'),vi);
});
const fs=require('node:fs');
const vm=require('node:vm');
function runtime(available){
 const events=new Map(), elements=new Map();
 for(const id of ['gsai-speech-status','gsai-voice-vi','gsai-voice-en','gsai-auto-read','gsai-cloud-read','gsai-speech-language','gsai-play-audio'])elements.set(id,{value:'',textContent:'',checked:id==='gsai-auto-read',hidden:true,replaceChildren(){},append(){}});
 elements.get('gsai-speech-language').value='auto';
 const doc={addEventListener(k,v){events.set(k,[...(events.get(k)||[]),v]);},removeEventListener(){},getElementById:k=>elements.get(k),createElement:()=>({})};
 const utterances=[], audio=[];
 const synth={getVoices:()=>available,cancel(){},speak:u=>utterances.push(u),addEventListener(){},removeEventListener(){}};
 const root={document:doc,speechSynthesis:synth,SpeechSynthesisUtterance:class{constructor(text){this.text=text;}},Audio:class{constructor(src){this.src=src;audio.push(this);}play(){return Promise.resolve();}pause(){}},addEventListener(){},removeEventListener(){},localStorage:{getItem:()=>null,setItem(){}}};
 const sandbox={window:root,setTimeout,clearTimeout,console}; vm.createContext(sandbox);
 const source=fs.readFileSync(require.resolve('../assets/pedagogical_speech.js'),'utf8');
 vm.runInContext(source,sandbox);root.GSAISpeech.updateContext({subject:'Tiếng Anh',grade:6,station:1});
 return {root,events,elements,utterances,audio,load:()=>vm.runInContext(source,sandbox)};
}
test('installing engine again does not duplicate document listeners',()=>{
 const r=runtime([]), first=r.root.GSAISpeech, count=r.events.get('dblclick').length;
 r.load();assert.equal(r.root.GSAISpeech,first);assert.equal(r.events.get('dblclick').length,count);
});
test('native reading uses the exact English voice and stops queued speech',async()=>{
 const voice={name:'US voice',lang:'en-US',voiceURI:'en'};
 const r=runtime([voice]);r.root.GSAISpeech.speak('Good morning. Choose the correct answer.','en');
 assert.equal(r.utterances.length,1);assert.equal(r.utterances[0].voice,voice);
 assert.equal(r.utterances[0].lang,'en-US');r.utterances[0].onend();r.root.GSAISpeech.stop();
 await new Promise(resolve=>setTimeout(resolve,350));assert.equal(r.utterances.length,1);
});
test('missing Vietnamese voice is never replaced by English silently',()=>{
 const r=runtime([{name:'US voice',lang:'en-US',voiceURI:'en'}]);
 r.root.GSAISpeech.speak('Chào các em.','vi');assert.equal(r.utterances.length,0);
 assert.match(r.elements.get('gsai-speech-status').textContent,/Chưa có giọng tiếng Việt/);
});
test('remote fallback requires UI opt-in and canceled results cannot play',async()=>{
 const r=runtime([{name:'US voice',lang:'en-US',voiceURI:'en'}]);let calls=0, release;
 r.root.GSAISpeech.remoteAudio=()=>{calls++;return new Promise(resolve=>{release=resolve;});};
 r.root.GSAISpeech.speak('Chào các em.','vi');assert.equal(calls,0);
 r.elements.get('gsai-cloud-read').checked=true;
 r.root.GSAISpeech.speak('Chào các em.','vi');assert.equal(calls,1);
 r.root.GSAISpeech.stop();release('test-audio');await new Promise(resolve=>setTimeout(resolve,0));
 assert.equal(r.audio.length,0);
});
test('bounded integrals and vector primes are read structurally',()=>{
 const t=s.formulaSpeech('\\int_0^1 x^2 dx; \\overrightarrow{AB\'}','vi');
 assert.ok(t.includes('tích phân từ 0 đến 1')); assert.ok(t.includes('véc tơ A B phẩy'));
 assert.ok(!t.includes('p h ẩ y'));
});
test('code blocks do not execute formula pronunciation rules',()=>{
 const t=s.prepareText('```python\nprint(r"$\\unsupported{x}$")\n```','vi','Tin học');
 assert.ok(t.includes('Khối mã')); assert.ok(!t.includes('unsupported'));
});
