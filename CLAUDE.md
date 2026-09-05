# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **Claude Code skill** (`cli-novel-writer`) for multi-agent novel writing. When a user says "写小说/创作故事/连载/小说", the main session (the「统筹队长」) dispatches 5 subagents via the Agent tool — each an independent-context worker. Data flows **between subagents through files, never through conversation**. The skill is a set of Markdown prompts/instructions; the only real code is a character-counting utility and its tests.

## Tests

```bash
python -m pytest tests/test_count_cjk.py -q    # full suite (10 tests, fast)
python -m pytest tests/test_count_cjk.py::test_mixed_cjk_only -q   # single test
```

Python is optional at runtime — `count_cjk.py` is only used by subagents to verify per-chapter word counts.

## Architecture (the big picture)

The skill is split so that `SKILL.md` stays thin and each subagent's knowledge lives in its own module:

- **`SKILL.md`** — the single entry point, read when the skill triggers. Holds: positioning, the dispatch protocol (派单), global rules (通信经济/否决权/熔断权), the workflow (逐章循环), local storage conventions, version management. It does **not** embed the full role rules — only one-line summaries + relative links into `references/agents/<角色>/rules.md`.
- **`references/agents/<角色>/`** — one directory per subagent (文笔/复核/剧情/人物/世界). Each has `rules.md` (the full role prompt, migrated verbatim from the original SKILL.md) + `checklist.md` (pre-task/verdict checks). Only **文笔** has `good_examples.md`/`bad_examples.md`, and **复核** has `bad_examples.md` — those two roles are the ones where examples correct output best.
- **Dispatch protocol**: when the队长 dispatches a subagent, it sends role key-points + a module path (`references/agents/文笔/rules.md`) rather than pasting the full rule text; the subagent reads its own module. Keep this "发要点+路径" model intact — don't re-embed role text into SKILL.md.
- **Editorial dependency to respect**: the「复核六一致性」list in `SKILL.md` must stay identical to the six in `references/agents/复核/checklist.md` (剧情逻辑/人物目标/情绪与关系/身体与信息状态/场景与转场/章末承接). The「去 AI 味」section in SKILL.md must point at `文笔/checklist.md`. If one changes, update the other.
- **Project output**: when a novel is started, the队长 creates `outputs/日期-项目名/` with 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X).

## Key conventions

- **All skill content is in Chinese** — write prompts/checklists/examples in Chinese, matching the existing files.
- **The `文笔` good_examples are sourced from a real corpus** (`Chinese-WebNovel-Skill/analysis/excerpts.csv`, excerpt_type 开头钩子/高张力对白/结尾余韵). When adding examples, use real verbatim excerpts from that CSV — never invent them — and keep「该学什么」about structure/rhythm, not style.
- `scripts/count_cjk.py` and `tests/` are deliberately unchanged by the refactor; keep them stable.

## Local dev commands

```bash
python scripts/count_cjk.py <file> [--min N --max M]   # count CJK chars; exit 0=in-range, 1=out, 2=usage, 3=unreadable
```

## Install (for real users, not needed for dev)

- Windows: `powershell -ExecutionPolicy Bypass -File install.ps1`
- macOS/Linux: `bash install.sh` — installs to `~/.claude/skills/cli-novel-writer/`
