# -*- coding: utf-8 -*-
"""Streamlit Community Cloud entrypoint.

Cloud apps often default to ``streamlit_app.py``. The real application lives in
``app.py``; this wrapper keeps one source of truth while satisfying the platform.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().with_name("app.py")), run_name="__main__")
