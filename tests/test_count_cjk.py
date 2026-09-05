import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scripts.count_cjk import _check_range, count_cjk, main


def test_empty() -> None:
    assert count_cjk("") == 0


def test_latin_punct_whitespace_not_counted() -> None:
    assert count_cjk("abc123!@# \t\n。，！？！") == 0


def test_pure_cjk() -> None:
    assert count_cjk("你好世界") == 4


def test_mixed_cjk_only() -> None:
    # 只数汉字，中文标点不计
    assert count_cjk("abc你好，world！流光") == 4


def test_range_boundaries() -> None:
    assert _check_range(2000, 2000, 4000) is True   # 下边界含
    assert _check_range(4000, 2000, 4000) is True   # 上边界含
    assert _check_range(1999, 2000, 4000) is False
    assert _check_range(4001, 2000, 4000) is False


def test_main_pass(tmp_path, capsys) -> None:
    p = tmp_path / "ch.md"
    p.write_text("中" * 2000, encoding="utf-8")
    assert main(["count_cjk.py", str(p)]) == 0
    out = capsys.readouterr().out
    assert "2000 中文字符" in out
    assert "PASS" in out


def test_main_fail_below_range(tmp_path, capsys) -> None:
    p = tmp_path / "ch.md"
    p.write_text("中" * 100, encoding="utf-8")
    assert main(["count_cjk.py", str(p)]) == 1
    out = capsys.readouterr().out
    assert "100 中文字符" in out
    assert "FAIL" in out


def test_main_custom_range(tmp_path) -> None:
    p = tmp_path / "ch.md"
    p.write_text("字" * 10, encoding="utf-8")
    assert main(["count_cjk.py", str(p), "--min", "1", "--max", "100"]) == 0


def test_main_missing_file(tmp_path) -> None:
    assert main(["count_cjk.py", str(tmp_path / "nope.md")]) == 3


def test_main_usage_error() -> None:
    assert main(["count_cjk.py"]) == 2
    assert main(["count_cjk.py", "--help"]) == 0
