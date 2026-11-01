import re
import shutil
import subprocess
import unittest
from types import SimpleNamespace

from tests.test_expert_patch_regressions import load_function


class MindmapViewportTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required to exercise generated JavaScript')
    def test_actual_generated_fit_contains_tall_and_narrow_trees(self):
        pages = []
        render = load_function('render_mermaid', st=SimpleNamespace(iframe=lambda page, **kwargs: pages.append(page)))
        render('graph LR\nA[Writing] --> B[Review]')
        fit = re.search(r'function fitMindmap\(\) \{[\s\S]*?\n        \}\n        fitMindmap\(\);', pages[0])[0]
        script = '''
const assert = require('node:assert/strict');
let fitTimer, transform;
const clearTimeout = () => {};
const setTimeout = fn => {fn(); return 1;};
const zoom = {transform: () => {}};
const d3 = {zoomIdentity: {translate: (x,y) => ({scale: k => ({x,y,k})})}};
const svg = {call: (_, value) => {transform=value;}};
const height=550;
let bounds, container={clientWidth:1009};
const g={node:()=>({getBBox:()=>bounds})};
''' + fit + '''
for (const width of [320,600,1009]) {
  container.clientWidth=width;
  for (const box of [{x:35,y:-606,width:973,height:1212}, {x:0,y:0,width:90,height:50}]) {
    bounds=box; fitMindmap();
    assert(bounds.x*transform.k+transform.x>=23.99);
    assert(bounds.y*transform.k+transform.y>=23.99);
    assert((bounds.x+bounds.width)*transform.k+transform.x<=width-23.99);
    assert((bounds.y+bounds.height)*transform.k+transform.y<=height-23.99);
  }
}
'''
        # Remove the initial invocation until test bounds have been assigned.
        script = script.replace('\n        fitMindmap();', '')
        subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)
