"""test_pathresolve.py — 直接单测 scripts/pathresolve.py（纯函数，不跑 CLI）。

覆盖 is_absolute / normalize / resolve 三函数的平台无关断言。
"""
from __future__ import annotations

import os
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

from pathresolve import is_absolute, normalize, resolve  # noqa: E402


# ---------- is_absolute ----------

@pytest.mark.parametrize("p", ["C:\\x", "C:/x", "\\\\srv\\x"])
def test_is_absolute_win_true(p):
    assert is_absolute(p, is_windows=True) is True


@pytest.mark.parametrize("p", ["/x", "x\\y", "./x", "../x", "x/y"])
def test_is_absolute_win_slash_is_relative(p):
    # Windows 下 `/x` 也是相对路径。
    assert is_absolute(p, is_windows=True) is False


@pytest.mark.parametrize("p", ["x\\y", "./x", "../x", "x/y"])
def test_is_absolute_nix_relative(p):
    assert is_absolute(p, is_windows=False) is False


def test_is_absolute_nix_slash_absolute():
    # macOS/Linux 下 `/x` 是绝对路径。
    assert is_absolute("/x", is_windows=False) is True


# ---------- normalize ----------

def test_normalize_strips_quotes_and_whitespace():
    # normalize 只去空白/引号，不做 normpath（保留原分隔符）。
    assert normalize('  "  some/dir  "  ') == "some/dir"


def test_normalize_single_quote():
    assert normalize("'single'") == "single"


def test_normalize_tilde_expands():
    out = normalize("~")
    assert out == os.path.expanduser("~")


def test_normalize_tilde_slash_expands():
    out = normalize("~/sub")
    home = os.path.expanduser("~")
    assert out.startswith(home)
    # expanduser 仅前缀替换，Windows 上可能保留 `/` 原分隔符；用 startswith + 尾段断言。
    assert out.endswith("sub") or out.endswith("/sub") or out.endswith("\\sub")


# ---------- resolve ----------

def test_resolve_absolute_passthrough():
    # 绝对路径原样解析（平台无关：用当前平台的绝对形式）。
    base = os.path.abspath("x")
    assert resolve(base, "/irrelevant") == base


def test_resolve_relative_joins_cwd():
    # 相对路径以 cwd 展开为绝对路径。
    cwd = os.path.abspath("some/cwd")
    assert resolve("rel", cwd) == os.path.normpath(os.path.join(cwd, "rel"))


def test_resolve_tilde_slash_joins_home():
    out = resolve("~/x", "/ignored/cwd")
    assert out == os.path.normpath(os.path.join(os.path.expanduser("~"), "x"))
