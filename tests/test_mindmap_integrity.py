import re
import shutil
import subprocess
import unittest
from types import SimpleNamespace

from tests.test_expert_patch_regressions import load_function


class MindmapIntegrityTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required')
    def test_tree_never_discards_nodes_or_recurses_through_cycles(self):
        pages = []
        render = load_function('render_mermaid', st=SimpleNamespace(
            iframe=lambda page, **kwargs: pages.append(page)))
        render('graph LR\nA[Input] --> B[Output]')
        page = pages[0]
        start = page.index('    function parseNodePart(')
        end = page.index('    // TẦNG CỨU HỘ', start)
        script = page[start:end] + '''
const assert = require('node:assert/strict');
assert.equal(parseMermaidToTree('graph LR\\nA[Input] --> B[Output]').children[0].name, 'Output');
assert.equal(parseMermaidToTree('graph LR\\nA[Input] --> B[Output]\\nC[Power]'), null);
assert.equal(parseMermaidToTree('graph LR\\nA --> B\\nB --> A'), null);
assert.equal(parseMermaidToTree('graph LR\\nA --> B\\nA --> C\\nB --> D\\nC --> D'), null);
'''
        subprocess.run([shutil.which('node'), '-e', script], check=True,
                       capture_output=True, text=True)
        self.assertNotIn('treeData = generateAutoHealerTree(rawCode)', page)
        self.assertIn('original.textContent = rawCode', page)
