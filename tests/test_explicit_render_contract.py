"""Guard the rendering assumption behind disabling Streamlit magic.

If future code relies on implicit rendering, migrate that expression to an
explicit st.write first, or reconsider the runner setting.
"""
import ast
from pathlib import Path
import unittest

from streamlit.runtime.scriptrunner import magic


class TestExplicitRendering(unittest.TestCase):
    def test_application_does_not_depend_on_implicit_streamlit_output(self):
        source = Path(__file__).resolve().parents[1] / 'app.py'
        tree = magic.add_magic(source.read_text(encoding='utf-8'), str(source))
        implicit = [getattr(node, 'lineno', 0) for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == magic.MAGIC_MODULE_NAME
                    and node.func.attr == 'transparent_write']
        self.assertEqual(implicit, [], 'Use explicit st.write for these lines before disabling magic')
