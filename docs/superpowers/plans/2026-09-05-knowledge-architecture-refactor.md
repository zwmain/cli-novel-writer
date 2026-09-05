# cli-novel-writer 知识架构重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 cli-novel-writer skill 的五个子代理规则从单个长 SKILL.md 拆成 `references/agents/` 模块，加入去 AI 味分层诊断、复核六一致性清单和精选例库，保留多代理协同。

**Architecture:** 知识组织从「单文件内联」改为「主文件路由 + 子代理模块下沉 + 精选例库」。SKILL.md 只留定位、派单协议（发要点+路径）、铁律与工作流；五个子代理的 rules/checklist/examples 各自独立成文件，子代理派单时按路径自读。

**Tech Stack:** Markdown 文档重组（无代码逻辑改动）。`scripts/count_cjk.py` 与 pytest 不受影响。

**Spec:** `docs/superpowers/specs/2026-09-05-knowledge-architecture-refactor-design.md`

## Global Constraints

- 不改多代理架构（不引入检索路由、不做主会话语料检索）。
- 不改 `scripts/count_cjk.py` 及 `tests/`、`conftest.py`。
- 不建独立 `data/` 目录、不写 `search_examples.py`。
- 剧情/人物/世界本期只建 `rules.md + checklist.md`，不建例库；文笔/复核建 rules + checklist + good/bad_examples。
- 派单协议改为「发角色要点 + 模块路径」，子代理按需深读，不再复制全文。
- 所有文件用中文书写（与现有 SKILL.md 一致），Markdown 相对链接路径必须正确可点。
- 铁律保留：数据靠文件传、一次只派一件事、写正文只派文笔、通信经济。

---

## Task 1: 建「剧情/人物/世界」子代理模块（rules + checklist）

**Files:**
- Create: `references/agents/剧情/rules.md`
- Create: `references/agents/剧情/checklist.md`
- Create: `references/agents/人物/rules.md`
- Create: `references/agents/人物/checklist.md`
- Create: `references/agents/世界/rules.md`
- Create: `references/agents/世界/checklist.md`

**Interfaces:**
- Consumes: 现 SKILL.md:41-45 中「世界/剧情/人物」三岗位长模板——原样下沉为 rules.md。
- Produces: 三个模块的 rules.md（角色规则全文）+ checklist.md（必查清单）。Task 6 会在 SKILL.md 里链接到这些 rules.md。

- [ ] **Step 1: 建目录**

```bash
mkdir -p references/agents/剧情 references/agents/人物 references/agents/世界
```

- [ ] **Step 2: 写 剧情/rules.md**

`# 剧情子代理规则` 标题，正文 = SKILL.md「【剧情子代理】」整段原样搬入（主线与因果的总策划。产出：主线节点、支线触发、伏笔台账、转折点设计。用「节点法」…读：宪法、已有台账、已写章节。）。

- [ ] **Step 3: 写 剧情/checklist.md**

```markdown
# 剧情子代理 checklist

- [ ] 这个节点是「因为…所以…」推出来的，不是拍脑袋硬写？
- [ ] 因果关系链完整（触发→决策→后果→兑现，缺哪一环）？
- [ ] 规划新节点前已检索伏笔台账，标注「回收第X章伏笔」？
- [ ] 每个节点都有冲突推动，不靠巧合推进？
- [ ] 节点只定关键情节点+情绪心电图，没越界去限制具体描写？
```

- [ ] **Step 4: 写 人物/rules.md**

`# 人物子代理规则` 标题，正文 = SKILL.md「【人物子代理】」整段原样搬入（人物灵魂与说话风格的档案库管理员。为每个角色建「灵魂四维」JSON 档案…读：白皮书、已有档案、最新章节。）。

- [ ] **Step 5: 写 人物/checklist.md**

```markdown
# 人物子代理 checklist

- [ ] 每个角色档案已含「灵魂四维」+ 语言基因卡两项？
- [ ] 已写人物关系网（敌友、亲疏值、这段关系怎么结下的）？
- [ ] 已写成长故事/成长弧光（从哪来、往哪去、什么事件让他改变）？
- [ ] 档案里没有「好人/坏人/高冷/温柔」这类扁平标签？
- [ ] 每章写完后做了「增量更新」，且标注变化依据（引用原文第几段）？
```

- [ ] **Step 6: 写 世界/rules.md**

`# 世界子代理规则` 标题，正文 = SKILL.md「【世界子代理】」整段原样搬入（世界背景与专有名词的唯一权威。产出 `世界规则白皮书` 和 `名词索引附录`。…读：题材梗概、已有白皮书。）。

- [ ] **Step 7: 写 世界/checklist.md**

```markdown
# 世界子代理 checklist

- [ ] 每条设定都展开成「设定是什么 + 为什么这样 + 对故事有什么影响」三段，没有一两句草草概括？
- [ ] 覆盖范围齐全：地理、气候、生态、人文、历史、种族、势力、政治、阶级、法律、经济、资源、战力/科技/魔法体系、语言宗教文化禁忌、传说与未解之谜？
- [ ] 已写明「当前主角战力 vs 天花板战力」的百分比差值？
- [ ] 给文笔只提供当章需要的「局部地图」和相关名词切片，没倾倒全量？
```

- [ ] **Step 8: 验证 6 个文件存在**

```bash
ls references/agents/剧情 references/agents/人物 references/agents/世界
```

Expected: 每组下有 rules.md + checklist.md 共 6 个文件。

- [ ] **Step 9: Commit**

```bash
git add references/agents/剧情 references/agents/人物 references/agents/世界
git commit -m "feat: add 剧情/人物/世界 subagent modules (rules + checklist)"
```

---

## Task 2: 建「文笔」子代理模块（rules + checklist + good/bad_examples）

**Files:**
- Create: `references/agents/文笔/rules.md`
- Create: `references/agents/文笔/checklist.md`
- Create: `references/agents/文笔/good_examples.md`
- Create: `references/agents/文笔/bad_examples.md`

**Interfaces:**
- Consumes: SKILL.md「【文笔子代理】」整段 + 设计 spec §2。
- Produces: 文笔模块全套（含去 AI 味 5 句 + 分层诊断）。Task 4 复核 bad_examples 引用其中的反例；Task 6 派单协议连接这里。

- [ ] **Step 1: 建目录**

```bash
mkdir -p references/agents/文笔
```

- [ ] **Step 2: 写 文笔/rules.md**

`# 文笔子代理规则` 标题，正文 = SKILL.md「【文笔子代理】」整段原样搬入（唯一写正文的。首要原则：遵从其它代理给出的要求…产出：第N章-vX.md 正文。字数核对：用 scripts/count_cjk.py 客观核对…）。

- [ ] **Step 3: 写 文笔/checklist.md**（落笔前必答 5 句 + 分层自查）

```markdown
# 文笔子代理 checklist

## 落笔前必答 5 句
- [ ] 1. 这一拍最重要的「局面变化」是什么？
- [ ] 2. 我准备用哪个「动作或物件」把它立住？
- [ ] 3. 这一拍里「谁最有压、谁最弱」？
- [ ] 4. 哪一句对白必须「带身份感」？
- [ ] 5. 这一段最该避免哪一句「空泛总结」？

## 写完后分层自查（去 AI 味）
- [ ] 空泛总结层：有没有「她很难过」「气氛很微妙」这类下判断句？改成动作/物件/反应链。
- [ ] 人物声音同质层：所有角色是不是都工整讲理、一个腔调？拉身份差/立场差/压人方式差。
- [ ] 套话氛围层：有没有「空气仿佛凝固」这类氛围套话？改场内变化/可听见的小声音/距离与动作变化。
- [ ] 平均节奏层：句子是不是都差不多长？拉句长/动作截断/短句插刀。
- [ ] 字数：章末用 scripts/count_cjk.py 核对 2000-4000 中文字符；无 Python 则估算并标注「估算」。
- [ ] 写对话前已查对应角色的「语言基因卡」。
- [ ] 落笔前先列镜头清单。
```

- [ ] **Step 4: 写 文笔/good_examples.md**

从隔壁语料 `analysis/excerpts.csv` 精选（按 `excerpt_type`），只借结构不借句面，每例带「该学什么」。结构：

```markdown
# 文笔正例库

## 开头钩子（精选 2-4 个）
### <来源：excerpt_id>
- 摘录：<原文>
- 该学什么：<从结构与节奏角度，一句话>

## 高张力对白（精选 2-4 个）
…同结构…
## 结尾余韵（精选 2-4 个）
…同结构…
```

（数据来源：`C:\Users\zwmai\.claude\skills\Chinese-WebNovel-Skill\analysis\excerpts.csv`，按 `excerpt_type` 字段 = `开头钩子/高张力对白/结尾余韵` 各挑 2-4 条真实摘录。选例标准：结构清晰、可迁移、不依赖特定长篇设定。）

- [ ] **Step 5: 写 文笔/bad_examples.md**

手写典型反例（覆盖 §2 四层），每例附「为什么不合」：

```markdown
# 文笔反例库

## 空泛总结
1. 反例：「她很悲伤，仿佛整个世界都失去了颜色。」
   为什么不合：作者替读者下结论；没有动作、物件、反应链。应改为具体行为（如反复摩挲一条旧手链，始终没说一句话）。

## 套话氛围
2. 反例：「空气仿佛凝固了，时间也慢了下来。」
   为什么不合：是气氛套话，没有场内变化。应写可听见的小声音、距离变化、具体动作。

## 人物声音同质
3. 反例：仆人和王爷都说出「这是我应尽的本分，还请殿下放心。」这类工整话语。
   为什么不合：没有身份差；两个完全不同身份的人说同一种腔调。
```

（可再补 1-2 条平均节奏/平铺直叙反例，格式同上。）

- [ ] **Step 6: 验证**

```bash
ls references/agents/文笔
```

Expected: rules.md + checklist.md + good_examples.md + bad_examples.md 共 4 个文件。

- [ ] **Step 7: Commit**

```bash
git add references/agents/文笔
git commit -m "feat: add 文笔 subagent module (rules + checklist + examples)"
```

---

## Task 3: 建「复核」子代理模块（rules + 六一致性 checklist + bad_examples）

**Files:**
- Create: `references/agents/复核/rules.md`
- Create: `references/agents/复核/checklist.md`
- Create: `references/agents/复核/bad_examples.md`

**Interfaces:**
- Consumes: SKILL.md「【复核子代理】」整段 + 设计 spec §3。
- Produces: 复核模块（六一致性清单 + 反例）。Task 4 会把「三色灯判决必须落到六一致性」写进 SKILL.md 派单协议；Task 6 连接。

- [ ] **Step 1: 建目录**

```bash
mkdir -p references/agents/复核
```

- [ ] **Step 2: 写 复核/rules.md**

`# 复核子代理规则` 标题，正文 = SKILL.md「【复核子代理】」整段原样搬入（只挑错、不改写。把正文逐条对照所有设定…字数检查：运行 scripts/count_cjk.py…）。

- [ ] **Step 3: 写 复核/checklist.md**（六一致性清单）

```markdown
# 复核子代理 checklist

逐项过六类一致性，每类做 🔴/🟡/🟢 判决；判决理由必须落到具体某一类，禁止「感觉不对」式泛判。

## 六一致性
- [ ] 1. 剧情逻辑一致性：关键事件有没有前提？关键决定有没有触发？关键变化有没有后果？
- [ ] 2. 人物目标一致性：主角这章到底想做什么？过程中有没有无故漂移？
- [ ] 3. 情绪与关系一致性：情绪有没有来路？关系温度跟上一场对不对得上？
- [ ] 4. 身体与信息状态一致性：伤势、疲劳、秘密、误会、已知信息有没有丢？（对照伏笔台账）
- [ ] 5. 场景与转场一致性：读者会不会迷路？上一场余力有没有带到下一场？
- [ ] 6. 章末承接一致性：章末是否收在变化上？下一章第一拍能不能接住？

## 判决规则
- 🔴 红灯=致命（人设崩塌/人物标签化/行为不合情理/战力冲突/地理错误/逻辑断链/伏笔未回收）→ 驳回让文笔重写，写清「哪里不合、为什么、怎么改」。
- 🟡 黄灯=警告（文笔略水/节奏拖沓/去 AI 味分层不过）→ 给修改建议，改后过审。
- 🟢 绿灯=通过。
- 整体判决：任两项 🔴 或三项 🟡 → 整体不过关。
- 额外：输出【节奏建议】和【章末钩子备选】（3 个不同方向，供队长选）。
- 字数：运行 scripts/count_cjk.py 核对 2000-4000 中文字符，脱离区间按偏离判 🟡/🔴。
```

- [ ] **Step 4: 写 复核/bad_examples.md**

手写六一致性反例，每例附「为什么不合」：

```markdown
# 复核反例库

## 章末承接
1. 反例：章末写「他转身离开了，一切都会好起来的。想到这里，他感到轻松了许多。」
   为什么不合：收在总结和讲理上，没有停在变化/危险/关系变化/半揭露真相上，下一章失去抓手。

## 逻辑断链
2. 反例：上一章主角没钱，下一章突然能付巨额诊金却无任何交代。
   为什么不合：关键变化（钱从哪来）没有前提/触发，读者会迷路。

## 情绪无来路
3. 反例：上一场主角还在冷静谈判，下一场毫无触发地大发雷霆。
   为什么不合：情绪没有来路；行为不符合人物目标和当下处境。
```

（可再补 1-2 条：身体信息丢失、人物目标漂移反例，格式同上。）

- [ ] **Step 5: 验证**

```bash
ls references/agents/复核
```

Expected: rules.md + checklist.md + bad_examples.md 共 3 个文件。

- [ ] **Step 6: Commit**

```bash
git add references/agents/复核
git commit -m "feat: add 复核 subagent module (rules + six-consistency checklist + bad examples)"
```

---

## Task 4: SKILL.md 瘦身（移走五岗位长模板，改派单协议为「发要点+路径」）

**Files:**
- Modify: `SKILL.md`（全文重写，保留头部 frontmatter：`name: cli-novel-writer` / `description` 原样）

**Interfaces:**
- Consumes: 前 3 个 Task 建好的 `references/agents/` 各模块；现 SKILL.md 全文。
- Produces: 瘦身后的 SKILL.md。Task 5 的 README 会引用它的架构说明；Task 6 校验链接。

- [ ] **Step 1: 重写 SKILL.md**

保留原结构骨架：定位/多核协同说明/派单协议/五岗位简介（改入口链接）/全局铁律/工作流/本地存储规范/章节版本管理/启动流程/输出纪律/脚本工具。

关键改动：
1. 「五个专职岗位」段 → 改为「五个专职岗位（子代理模块）」：每个岗位只留一句话职责摘要 + 链接 `references/agents/<角色>/rules.md`（相对链接）。
2. 「派单协议」三块不变，但第 1 块「角色规则」改为**发要点 + 模块路径**，示例：

```markdown
每次派单 prompt 三块不变（角色规则 / 本次任务 / 数据来源），第 1 块改为：

「角色：文笔子代理。完整规则见 references/agents/文笔/rules.md，
落笔前先读它的 checklist.md 并回答 5 句（§2）。本次任务是：……」
```

3. 新增「去 AI 味」小节（一句话原则 + 指向 `references/agents/文笔/checklist.md` 的分层诊断）。
4. 新增「复核六一致性」小节（六类一致性一句话列出 + 指向 `references/agents/复核/checklist.md`；判决理由必须落到六一致性）。
5. 保留铁律：数据靠文件传、一次只派一件事、写正文只派文笔、通信经济、否决权、熔断权。

（原文「五岗位长模板」与「人物档案 JSON Schema」示例整段内联内容删除——JSON Schema 是人物档案数据契约，保留在 SKILL.md「本地存储规范」内。）

- [ ] **Step 2: 校验 frontmatter 保留**

`name: cli-novel-writer` 与 `description` 原样未变；文件以 `---` 开头。

- [ ] **Step 3: 校验内链可点**

逐个打开 SKILL.md 中新增的相对链接，确认存在：

```bash
ls references/agents/文笔/rules.md references/agents/剧情/rules.md references/agents/人物/rules.md references/agents/世界/rules.md references/agents/复核/rules.md
```

Expected: 5 个文件都存在。

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: slim SKILL.md, move agent rules to references/agents, update dispatch protocol"
```

---

## Task 5: README.md 同步更新（架构说明 + 目录树）

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: 瘦身后的 SKILL.md（Task 4）。
- Produces: README 反映新架构。Task 6 会整体校验。

- [ ] **Step 1: 更新 README 内容**

在「这是什么」表后补一段「知识架构」：主文件路由 + 子代理模块下沉 + 精选例库；更新目录树为：

```text
├─ SKILL.md                主文件：定位 + 派单协议 + 铁律 + 工作流
├─ references/agents/      5 个子代理模块
│   ├─ 文笔/  rules + checklist + good/bad_examples
│   ├─ 剧情/  rules + checklist
│   ├─ 人物/  rules + checklist
│   ├─ 世界/  rules + checklist
│   └─ 复核/  rules + 六一致性 checklist + bad_examples
└─ scripts/ count_cjk.py   字数统计工具（未变）
```

保持「怎么用」「它会读写文件」「章节版本管理」「想改它」各节不变，只把「想改它」里的「全部提示词在 SKILL.md 里」改为「全部提示词在 SKILL.md + references/agents/ 里；子代理规则在 references/agents/<角色>/rules.md」。

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README for module-based architecture"
```

---

## Task 6: 整体校验（结构完整性 + 链接 + 全仓一致性）

**Files:**
- Read/校验: 全仓

**Interfaces:**
- Consumes: 全部前序 Task。
- Produces: 验证结果报告，无产出文件。

- [ ] **Step 1: 校验目录结构**

```bash
find references/agents -type f | sort
```

Expected: 5 个子代理目录齐全；文笔 4 文件、复核 3 文件、剧情/人物/世界各 2 文件，共 13 个文件。

- [ ] **Step 2: 校验 SKILL.md 内所有相对链接可点**

```bash
python - <<'PY'
import re, pathlib
root = pathlib.Path('.')
skill = (root/'SKILL.md').read_text(encoding='utf-8')
links = re.findall(r'\]\(([^)#]+)', skill)
bad = [l for l in links if not (root/l).exists() and not l.startswith('http')]
print('BAD LINKS:', bad if bad else 'none')
PY
```

Expected: `BAD LINKS: none`

- [ ] **Step 3: 校验无残留旧引用**

```bash
grep -rn "五个专职岗位" SKILL.md || echo "NO_OLD_REF"
grep -c "references/agents" SKILL.md README.md
```

Expected: 第一条输出 `NO_OLD_REF`（SKILL.md 已无「五个专职岗位」内联长模板旧引用）；第二条输出两个数字都 >= 2（`references/agents` 在 SKILL.md 与 README.md 中均有引用）。

- [ ] **Step 4: 跑原测试确认 count_cjk 未受影响**

```bash
python -m pytest tests/test_count_cjk.py -q
```

Expected: 全部通过（原逻辑未动）。

- [ ] **Step 5: 全仓库 git 状态干净**

```bash
git status --short
```

Expected: 无未提交改动（除已提交的 docs/）。

---

## Self-Review 记录

- Spec coverage: §1→Task1,2,3,4; §2→Task2; §3→Task3; §4→Task2; §5→Global Constraints。
- Placeholder scan: 无反例内容留「TBD」；good_examples 明确要求从 `analysis/excerpts.csv` 真实抽出，无空占位。
- Type/路径一致性: 全部 `references/agents/` 路径统一，Task 间递归一致；`count_cjk.py` 全程未改。