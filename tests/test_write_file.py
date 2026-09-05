"""test_write_file.py — 参数化子进程测 write_file（py + node 两套实现）。

不 import 函数，用 subprocess 跑真实 CLI，断言退出码 + 文件副作用（存在/内容）。
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

PY_SCRIPT = str(REPO_ROOT / "scripts" / "write_file.py")
NODE_SCRIPT = str(REPO_ROOT / "scripts" / "write_file.mjs")

NODE = shutil.which("node")
if NODE is None:
    pytest.skip("node 不可用", allow_module_level=True)


def run_py(args, cwd):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"  # 子进程 stdout/stderr 统一 UTF-8，避免平台 locale 差异
    return subprocess.run(
        [sys.executable, PY_SCRIPT, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=cwd,
    )


def run_node(args, cwd):
    # node 一律输出 UTF-8 字节，读取侧显式 utf-8，Windows 上 GBK locale 也能正确解码。
    return subprocess.run(
        [NODE, NODE_SCRIPT, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
    )


def _run(impl, args, cwd):
    return run_node(args, cwd) if impl == "node" else run_py(args, cwd)


@pytest.mark.parametrize("impl", ["py", "node"])
def test_write_creates_file_and_parents(impl, tmp_path):
    target = tmp_path / "a" / "b" / "c.txt"
    result = _run(impl, [str(target), "hello world"], tmp_path)
    assert result.returncode == 0
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "hello world"
    assert (tmp_path / "a").is_dir()
    assert (tmp_path / "a" / "b").is_dir()


@pytest.mark.parametrize("impl", ["py", "node"])
def test_write_multiline(impl, tmp_path):
    target = tmp_path / "multi.txt"
    result = _run(impl, [str(target), "line1\nline2"], tmp_path)
    assert result.returncode == 0
    assert target.read_text(encoding="utf-8") == "line1\nline2"


@pytest.mark.parametrize("impl", ["py", "node"])
def test_write_empty_content(impl, tmp_path):
    target = tmp_path / "empty.txt"
    result = _run(impl, [str(target), ""], tmp_path)
    assert result.returncode == 0
    assert target.exists()
    assert target.stat().st_size == 0


@pytest.mark.parametrize("impl", ["py", "node"])
def test_overwrite_existing(impl, tmp_path):
    target = tmp_path / "x.txt"
    assert _run(impl, [str(target), "first"], tmp_path).returncode == 0
    result = _run(impl, [str(target), "second"], tmp_path)
    assert result.returncode == 0
    assert target.read_text(encoding="utf-8") == "second"


@pytest.mark.parametrize("impl", ["py", "node"])
def test_no_args_usage_error(impl, tmp_path):
    result = _run(impl, [], tmp_path)
    assert result.returncode == 2
    assert "用法" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_help_returns_0(impl, tmp_path):
    result = _run(impl, ["--help"], tmp_path)
    assert result.returncode == 0
    assert "用法" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_relative_path_resolves_against_cwd(impl, tmp_path):
    result = _run(impl, ["rel/f.txt", "x"], tmp_path)
    assert result.returncode == 0
    target = tmp_path / "rel" / "f.txt"
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "x"


@pytest.mark.parametrize("impl", ["py", "node"])
def test_content_named_help_goes_to_file(impl, tmp_path):
    # len==3（path + content）→ 内容 "--help" 写入文件，而非打印 usage。证明优先级。
    target = tmp_path / "x.txt"
    result = _run(impl, [str(target), "--help"], tmp_path)
    assert result.returncode == 0
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "--help"


@pytest.mark.parametrize("impl", ["py", "node"])
def test_write_chinese_content_utf8(impl, tmp_path):
    # 中文字节往返，验证 py open utf-8 / node writeFileSync utf-8。
    target = tmp_path / "zh.txt"
    result = _run(impl, [str(target), "你好世界"], tmp_path)
    assert result.returncode == 0
    assert target.read_text(encoding="utf-8") == "你好世界"
