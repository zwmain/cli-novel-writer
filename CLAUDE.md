# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **Claude Code skill** (`cli-novel-writer`) for multi-agent novel writing. When a user says "写小说/创作故事/连载/小说", the main session (the「统筹队长」) dispatches 5 subagents via the Agent tool — each an independent-context worker. Data flows **between subagents through files, never through conversation**. The skill is a set of Markdown prompts/instructions; the only real code is a character-counting utility and its tests.

## Tests

```bash
python -m pytest tests/test_count_cjk.py -q    # count_cjk (10 tests, py unit)
python -m pytest tests/ -q                     # full suite (count_cjk + check_dir + write_file, py & node)
python -m pytest tests/test_count_cjk_node.py -q   # count_cjk py & node parity via subprocess
```

Python is optional at runtime — `count_cjk.py` (or its node twin `count_cjk.mjs`) is only used by subagents to verify per-chapter word counts.

## Architecture (the big picture)

The skill is split so that `SKILL.md` stays thin and each subagent's knowledge lives in its own module:

- **`SKILL.md`** — the single entry point, read when the skill triggers. Holds: positioning, the dispatch protocol (派单), global rules (通信经济/否决权/熔断权), the workflow (逐章循环), local storage conventions, version management. It does **not** embed the full role rules — only one-line summaries + relative links into `references/agents/<角色>/rules.md`.
- **`references/agents/<角色>/`** — one directory per subagent (文笔/复核/剧情/人物/世界). Each has `rules.md` (the full role prompt, migrated verbatim from the original SKILL.md) + `checklist.md` (pre-task/verdict checks). Only **文笔** has `good_examples.md`/`bad_examples.md`, and **复核** has `bad_examples.md` — those two roles are the ones where examples correct output best.
- **Dispatch protocol**: when the队长 dispatches a subagent, it sends role key-points + a module path (`references/agents/文笔/rules.md`) rather than pasting the full rule text; the subagent reads its own module. Keep this "发要点+路径" model intact — don't re-embed role text into SKILL.md.
- **Editorial dependency to respect**: the「复核六一致性」list in `SKILL.md` must stay identical to the six in `references/agents/复核/checklist.md` (剧情逻辑/人物目标/情绪与关系/身体与信息状态/场景与转场/章末承接). The「去 AI 味」section in SKILL.md must point at `文笔/checklist.md`. If one changes, update the other.
- **Project output**: when a novel is started, the队长 resolves the 项目根 directory (user-specified — absolute/relative cwd/`~` — or default `cwd/日期-项目名/`), writes `项目索引.md` (project name, created date, **absolute** root path, source-marker 原生/外来导入, chapter-mapping) for resume-lookup, and creates 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X). Path resolution rules live only in SKILL.md's 本地存储规范. The startup flow branches three ways in SKILL.md: (A) 新开 project from 题材/梗概; (B) continue a skill project via `项目索引.md` resume; (C) import a foreign novel (raw chapters only) by reading chapters → generating draft 叙事宪法/世界规则/人物档案/章节目录 (marked 从原章节推导) → user confirmation → build `项目索引.md` (source-marker 外来导入 + chapter map) → continue. Foreign raw chapters stay read-only. `剧情推演.md`（剧情动态状态：剧情现状事实链/情绪心电图/支线与矛盾/后续计划，剧情子代理每章定稿后增量更新，只追加不改写既定事实）也归一于项目根。

## Key conventions

- **All skill content is in Chinese** — write prompts/checklists/examples in Chinese, matching the existing files.
- **The `文笔` good_examples are sourced from a real corpus** (`Chinese-WebNovel-Skill/analysis/excerpts.csv`, excerpt_type 开头钩子/高张力对白/结尾余韵). When adding examples, use real verbatim excerpts from that CSV — never invent them — and keep「该学什么」about structure/rhythm, not style.
- `scripts/count_cjk.py` / `scripts/count_cjk.mjs` and `tests/` are deliberately kept minimal; add node twins by following the existing `.mjs` pattern (parity tests in `tests/test_*_node.py`).

## Local dev commands

```bash
python scripts/count_cjk.py <file> [--min N --max M]   # count CJK chars; exit 0=in-range, 1=out, 2=usage, 3=unreadable
node scripts/count_cjk.mjs <file> [--min N --max M]    # node equivalent (same CLI)
python scripts/check_dir.py <path> [--create]     # check/create dir; exit 0/1/2/3
python scripts/write_file.py <path> <content>     # write file (recursive parent create); exit 0/1/2/3
node scripts/check_dir.mjs <path> [--create]      # node equivalents (same CLI)
node scripts/write_file.mjs <path> <content>
```

## Install (for real users, not needed for dev)

- Windows: `powershell -ExecutionPolicy Bypass -File install.ps1`
- macOS/Linux: `bash install.sh` — installs to `~/.claude/skills/cli-novel-writer/`
