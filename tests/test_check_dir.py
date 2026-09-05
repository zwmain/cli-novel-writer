"""test_check_dir.py — 参数化子进程测 check_dir（py + node 两套实现）。

不 import 函数，用 subprocess 跑真实 CLI，断言退出码 + 文件系统副作用。
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

PY_SCRIPT = str(REPO_ROOT / "scripts" / "check_dir.py")
NODE_SCRIPT = str(REPO_ROOT / "scripts" / "check_dir.mjs")

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
def test_dir_exists_returns_0(impl, tmp_path):
    (tmp_path / "a").mkdir()
    result = _run(impl, [str(tmp_path / "a")], tmp_path)
    assert result.returncode == 0
    assert str(tmp_path / "a") in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_dir_missing_returns_1(impl, tmp_path):
    result = _run(impl, [str(tmp_path / "nope")], tmp_path)
    assert result.returncode == 1
    assert "不存在" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_create_missing_dir(impl, tmp_path):
    target = tmp_path / "a" / "b" / "c"
    result = _run(impl, ["--create", str(target)], tmp_path)
    assert result.returncode == 0
    assert target.is_dir()
    assert (tmp_path / "a").is_dir()
    assert (tmp_path / "a" / "b").is_dir()


@pytest.mark.parametrize("impl", ["py", "node"])
def test_create_idempotent(impl, tmp_path):
    target = tmp_path / "a" / "b"
    assert _run(impl, ["--create", str(target)], tmp_path).returncode == 0
    result = _run(impl, ["--create", str(target)], tmp_path)
    assert result.returncode == 0
    assert target.is_dir()


@pytest.mark.parametrize("impl", ["py", "node"])
def test_create_existing(impl, tmp_path):
    target = tmp_path / "a"
    target.mkdir()
    result = _run(impl, ["--create", str(target)], tmp_path)
    assert result.returncode == 0
    assert target.is_dir()


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
    # 先创建子目录，用相对名检查 → 相对 cwd 解析成功。
    (tmp_path / "sub").mkdir()
    result = _run(impl, ["sub"], tmp_path)
    assert result.returncode == 0
    # --create 相对嵌套目录 → 创建在 tmp_path 之下。
    result = _run(impl, ["--create", "rel/dir"], tmp_path)
    assert result.returncode == 0
    assert (tmp_path / "rel" / "dir").is_dir()


@pytest.mark.parametrize("impl", ["py", "node"])
def test_file_is_not_dir_returns_1(impl, tmp_path):
    # 是文件而非目录 → 退出码 1（证明 isdir/isDirectory 逻辑，而非 exists）。
    f = tmp_path / "plain.txt"
    f.write_text("x", encoding="utf-8")
    result = _run(impl, [str(f)], tmp_path)
    assert result.returncode == 1
