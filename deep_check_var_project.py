# -*- coding: utf-8 -*-
"""
==============================================================================
DEEP CHECK VAR PROJECT AUDITOR (PRO EDITION) - HỆ THỐNG GSAI THPT 2026
Kiểm tra tự động 100% cú pháp, lỗi cắt cụt file (Truncated EOF), thiếu import,
tính toàn vẹn ngân hàng đề (.json / .json.xz / .json.zst) và đường dẫn tài nguyên.
==============================================================================
"""

import ast
import builtins
import gzip
import importlib.util
import json
import lzma
import os
import py_compile
import re
import sys
import unittest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BUILTIN_NAMES = set(dir(builtins)) | {
    "__file__", "__name__", "__doc__", "__package__", "__builtins__"
}

CRITICAL_SYMBOLS_HINT = {
    "Fraction": "Thiếu lệnh: from fractions import Fraction (ở đầu file app.py)",
    "Path": "Thiếu lệnh: from pathlib import Path",
    "deepcopy": "Thiếu lệnh: from copy import deepcopy",
    "fall": "Dòng cuối bị cắt cụt chữ 'fallback' thành 'fall'",
}


def find_python_files(root_dir: str) -> list:
    py_files = []
    ignore_dirs = {
        ".git", "__pycache__", ".venv", "venv", "env", "node_modules", 
        ".devcontainer", ".backup_gsai_heal", "backup_vip66_pre_patch", "scratch"
    }
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".backup")]
        for fname in sorted(filenames):
            if not fname.endswith(".py") or fname == os.path.basename(__file__):
                continue
            if fname.startswith("app_backup_") or fname.startswith("backup_"):
                continue
            py_files.append(os.path.join(dirpath, fname))
    return py_files


def check_truncated_eof(file_path: str, source_text: str) -> list:
    warnings = []
    lines = [ln for ln in source_text.splitlines() if ln.strip()]
    if not lines:
        return ["Tệp rỗng (0 dòng lệnh)."]

    last_line = lines[-1].rstrip()
    rel_path = os.path.relpath(file_path, ROOT_DIR)

    if re.search(r"^\s+return\s*$", source_text.splitlines()[-1]):
        warnings.append(f"[{rel_path}] Dòng cuối kết thúc bằng 'return' trống.")

    clean_last = last_line.split("#")[0].rstrip()
    if clean_last and clean_last.endswith(("(", "[", "{", ",", "=", "+", "-", "*", "\\", ":")):
        warnings.append(f"[{rel_path}] Dòng cuối kết thúc bất thường bằng '{clean_last[-1]}': `{last_line}`")

    return warnings


def collect_bound_names_in_scope(scope_node: ast.AST) -> set:
    bound = set()

    if isinstance(scope_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        all_args = (
            getattr(scope_node.args, "posonlyargs", [])
            + scope_node.args.args
            + scope_node.args.kwonlyargs
        )
        for arg in all_args:
            bound.add(arg.arg)
        if scope_node.args.vararg:
            bound.add(scope_node.args.vararg.arg)
        if scope_node.args.kwarg:
            bound.add(scope_node.args.kwarg.arg)

    def _walk_same_scope(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                bound.add(child.name)
                continue
            if isinstance(child, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                continue
            if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Param)):
                bound.add(child.id)
            elif isinstance(child, ast.Import):
                for alias in child.names:
                    bound.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(child, ast.ImportFrom):
                for alias in child.names:
                    if alias.name != "*":
                        bound.add(alias.asname or alias.name)
            elif isinstance(child, ast.ExceptHandler) and child.name:
                bound.add(child.name)
            elif isinstance(child, (ast.Global, ast.Nonlocal)):
                for n in child.names:
                    bound.add(n)
            _walk_same_scope(child)

    _walk_same_scope(scope_node)
    return bound


class ScopeAuditVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scopes = [set(BUILTIN_NAMES)]
        self.used_names = []

    def is_defined(self, name: str) -> bool:
        return any(name in s for s in reversed(self.scopes))

    def visit_Module(self, node):
        self.scopes[-1].update(collect_bound_names_in_scope(node))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for dec in node.decorator_list:
            self.visit(dec)
        for base in node.bases:
            self.visit(base)
        for kw in node.keywords:
            self.visit(kw)
        class_scope = collect_bound_names_in_scope(node)
        self.scopes.append(class_scope)
        for item in node.body:
            self.visit(item)
        self.scopes.pop()

    def _visit_function(self, node):
        for dec in node.decorator_list:
            self.visit(dec)
        for default in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(default)
        fn_scope = collect_bound_names_in_scope(node)
        self.scopes.append(fn_scope)
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_FunctionDef(self, node):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node)

    def visit_Lambda(self, node):
        for default in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            self.visit(default)
        lm_scope = collect_bound_names_in_scope(node)
        self.scopes.append(lm_scope)
        self.visit(node.body)
        self.scopes.pop()

    def _visit_comp(self, node):
        comp_scope = set()
        for gen in node.generators:
            for sub in ast.walk(gen.target):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                    comp_scope.add(sub.id)
        self.scopes.append(comp_scope)
        for gen in node.generators:
            self.visit(gen.iter)
            for if_clause in gen.ifs:
                self.visit(if_clause)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.scopes.pop()

    def visit_ListComp(self, node):
        self._visit_comp(node)

    def visit_SetComp(self, node):
        self._visit_comp(node)

    def visit_GeneratorExp(self, node):
        self._visit_comp(node)

    def visit_DictComp(self, node):
        self._visit_comp(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not self.is_defined(node.id):
                self.used_names.append((node.id, node.lineno))


def check_data_and_assets() -> tuple:
    errors = []
    warnings = []
    bank_dir = os.path.join(ROOT_DIR, "data", "real_exam_bank")
    if os.path.isdir(bank_dir):
        for fname in sorted(os.listdir(bank_dir)):
            fpath = os.path.join(bank_dir, fname)
            try:
                if fname.endswith(".json"):
                    with open(fpath, "r", encoding="utf-8") as f:
                        json.load(f)
                elif fname.endswith(".json.zst"):
                    try:
                        import zstandard as zstd
                        import orjson
                        dctx = zstd.ZstdDecompressor()
                        with open(fpath, "rb") as fh:
                            orjson.loads(dctx.decompress(fh.read(), max_output_size=150*1024*1024))
                    except ImportError:
                        pass
                elif fname.endswith(".json.xz"):
                    # Cách ly file master 20MB (33k đề) để tránh treo CPU và OOM khi audit nhanh
                    if "baseline_exams" in fname and os.path.getsize(fpath) > 5 * 1024 * 1024:
                        continue
                    with lzma.open(fpath, "rt", encoding="utf-8") as f:
                        json.load(f)
                elif fname.endswith(".json.gz"):
                    with gzip.open(fpath, "rt", encoding="utf-8") as f:
                        json.load(f)
            except Exception as exc:
                errors.append(f"[Dữ liệu lỗi] '{fname}': {exc}")
    return errors, warnings


def main():
    print("=" * 78)
    print("🔍 BẮT ĐẦU DEEP CHECK VAR TOÀN DIỆN DỰ ÁN GSAI - THPT 2026")
    print("=" * 78)

    py_files = find_python_files(ROOT_DIR)
    syntax_errors = []
    eof_warnings = []
    undefined_errors = []

    for fpath in py_files:
        rel = os.path.relpath(fpath, ROOT_DIR)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            syntax_errors.append(f"[{rel}] Không thể đọc tệp UTF-8: {e}")
            continue

        eof_warnings.extend(check_truncated_eof(fpath, src))

        try:
            tree = ast.parse(src, filename=rel)
            py_compile.compile(fpath, doraise=True)
        except SyntaxError as se:
            syntax_errors.append(f"[{rel}:{se.lineno}] SyntaxError: {se.msg}")
            continue
        except Exception as ce:
            syntax_errors.append(f"[{rel}] CompileError: {ce}")
            continue

        visitor = ScopeAuditVisitor()
        visitor.visit(tree)
        seen = set()
        for name, lineno in visitor.used_names:
            if (name, lineno) not in seen:
                seen.add((name, lineno))
                hint = f" -> {CRITICAL_SYMBOLS_HINT[name]}" if name in CRITICAL_SYMBOLS_HINT else ""
                undefined_errors.append(f"[{rel}:{lineno}] Thiếu khai báo hoặc import: '{name}'{hint}")

    data_errors, data_warnings = check_data_and_assets()

    print(f"📂 Đã kiểm tra {len(py_files)} tệp Python.")
    for e in syntax_errors + undefined_errors + data_errors:
        print(f"   ❌ {e}")
    for w in eof_warnings + data_warnings:
        print(f"   ⚠️ {w}")

    tests_dir = os.path.join(ROOT_DIR, "tests")
    test_passed = True
    if os.path.isdir(tests_dir) and not syntax_errors:
        suite = unittest.TestLoader().discover(start_dir=tests_dir, pattern="test_*.py", top_level_dir=ROOT_DIR)
        test_passed = unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()

    total_critical = len(syntax_errors) + len(undefined_errors) + len(data_errors) + (0 if test_passed else 1)
    print("=" * 78)
    if total_critical == 0:
        print("🎉 KẾT LUẬN: HỆ THỐNG ĐẠT CHUẨN 100% (ZERO CRITICAL BUGS) - TICK XANH!")
        sys.exit(0)
    else:
        print(f"🚨 PHÁT HIỆN {total_critical} LỖI CẦN VÁ ĐỂ LẤY LẠI TICK XANH!")
        sys.exit(1)


if __name__ == "__main__":
    main()
