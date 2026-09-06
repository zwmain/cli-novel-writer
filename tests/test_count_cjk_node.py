"""test_count_cjk_node.py — 参数化子进程测 count_cjk（py + node 两套实现）。

不 import 函数（与 test_check_dir.py / test_write_file.py 同模式），用 subprocess 跑
真实 CLI，断言退出码 + stdout/stderr 内容，验证 py / node 双实现行为一致。
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

PY_SCRIPT = str(REPO_ROOT / "scripts" / "count_cjk.py")
NODE_SCRIPT = str(REPO_ROOT / "scripts" / "count_cjk.mjs")

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
def test_empty_file_counts_0(impl, tmp_path):
    # 空文件 → 0 个中文字符，低于默认区间 → FAIL（退出码 1）。
    p = tmp_path / "empty.md"
    p.write_text("", encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "0 中文字符" in result.stdout
    assert "FAIL" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_latin_punct_whitespace_not_counted(impl, tmp_path):
    # 无汉字 → 0，低于默认区间 → FAIL（退出码 1）。
    p = tmp_path / "latin.md"
    p.write_text("abc123!@# \t\n。，！？！", encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "0 中文字符" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_pure_cjk_counts(impl, tmp_path):
    # 4 个汉字，低于默认区间 → FAIL（退出码 1）；计数正确。
    p = tmp_path / "cjk.md"
    p.write_text("你好世界", encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "4 中文字符" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_mixed_counts_only_hanzi(impl, tmp_path):
    # 只数汉字，中文标点不计；低于默认区间 → FAIL。
    p = tmp_path / "mixed.md"
    p.write_text("abc你好，world！流光", encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "4 中文字符" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_default_range_pass_2000(impl, tmp_path):
    p = tmp_path / "ch.md"
    p.write_text("中" * 2000, encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 0
    assert "PASS" in result.stdout
    # 下边界 2000 含
    p.write_text("中" * 4000, encoding="utf-8")
    assert _run(impl, [str(p)], tmp_path).returncode == 0  # 上边界 4000 含


@pytest.mark.parametrize("impl", ["py", "node"])
def test_below_range_fail(impl, tmp_path):
    p = tmp_path / "ch.md"
    p.write_text("中" * 100, encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "100 中文字符" in result.stdout
    assert "FAIL" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_above_range_fail(impl, tmp_path):
    p = tmp_path / "ch.md"
    p.write_text("中" * 4001, encoding="utf-8")
    result = _run(impl, [str(p)], tmp_path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_custom_range(impl, tmp_path):
    p = tmp_path / "ch.md"
    p.write_text("字" * 10, encoding="utf-8")
    result = _run(impl, [str(p), "--min", "1", "--max", "100"], tmp_path)
    assert result.returncode == 0
    assert "PASS" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_custom_range_mismatch(impl, tmp_path):
    p = tmp_path / "ch.md"
    p.write_text("字" * 10, encoding="utf-8")
    result = _run(impl, [str(p), "--min", "20", "--max", "100"], tmp_path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout


@pytest.mark.parametrize("impl", ["py", "node"])
def test_missing_file_returns_3(impl, tmp_path):
    result = _run(impl, [str(tmp_path / "nope.md")], tmp_path)
    assert result.returncode == 3
    assert "无法读取文件" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_no_args_usage_error(impl, tmp_path):
    result = _run(impl, [], tmp_path)
    assert result.returncode == 2
    assert "用法" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_help_returns_0(impl, tmp_path):
    result = _run(impl, ["--help"], tmp_path)
    assert result.returncode == 0
    assert "用法" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_unknown_flag_as_file_returns_3(impl, tmp_path):
    # 未知 `-` 前缀在文件位 → 当作文件名 → 读不到 → 退出码 3。
    result = _run(impl, ["--bogus"], tmp_path)
    assert result.returncode == 3
    assert "无法读取文件" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_flag_without_value_usage_error(impl, tmp_path):
    # `--min`/`--max` 无值：末尾 --min → 视为文件名 → 读不到 → 退出码 3。
    result = _run(impl, ["--min"], tmp_path)
    assert result.returncode == 3


@pytest.mark.parametrize("impl", ["py", "node"])
def test_unknown_extra_flag_usage_error(impl, tmp_path):
    # 文件之后出现未知参数 → 用法错误（退出码 2）。
    p = tmp_path / "ch.md"
    p.write_text("中" * 10, encoding="utf-8")
    result = _run(impl, [str(p), "--bogus"], tmp_path)
    assert result.returncode == 2
    assert "未知参数" in result.stderr


@pytest.mark.parametrize("impl", ["py", "node"])
def test_chinese_filename_utf8(impl, tmp_path):
    # 文件名含中文，验证路径字节往返。
    p = tmp_path / "第1章.md"
    p.write_text("章" * 30, encoding="utf-8")
    result = _run(impl, [str(p), "--min", "1", "--max", "100"], tmp_path)
    assert result.returncode == 0
    assert "30 中文字符" in result.stdout