# Guided Intake — verbatim script

This is the humane, step-by-step interview the skill runs on first use. The goals:
**never show a wall of questions, default hard, infer what you can, let the user skip
anything.** Prefer the host's structured question UI (e.g. `AskUserQuestion`) for the
multiple-choice steps; use plain chat for free-text like paths.

Speak the user's language (default 中文 in examples below; mirror whatever they write).
Ask **one step at a time**; carry answers forward and echo them back at the end.

---

## Step 0 — Welcome + dependency self-check

Open warm, set expectations, then check only what's needed.

> 👋 我可以把你的复习素材整理成一整套**离线可双击打开**的考前冲刺包：复习笔记库、HTML 复习系统、刷题 App、模拟卷、一页小抄、知识架构图、历年卷解析。
> 先做个快速准备，几步就好，能跳的都能跳。

Run a dependency probe and report a small table. **Only flag a tool as required once
the matching input is chosen** (so a notes-only user never needs ffmpeg):

| Tool | Needed for | Check |
|---|---|---|
| `node` | generating any HTML / running `md2html.js` | `node -v` |
| `python` (3.10+) | docx/pptx extraction, `build_quiz.py`, `verify_html.py`, whisper | `python --version` |
| `ffmpeg` + `ffprobe` | extracting slides & audio from a recording | `ffmpeg -version` |
| `faster-whisper` (pip) | transcribing audio → text | `python -c "import faster_whisper"` |

For anything missing, give a one-line install hint (e.g. `pip install faster-whisper`,
download ffmpeg, install Node LTS) and note which deliverables it gates. Do **not** block
the whole flow on a tool the user's inputs won't touch.

---

## Step 1 — Course basics (keep it tiny)

Ask as one short free-text block; every field is skippable.

1. **课程 / 科目名？**（如「单片机 / MCS-51」「数据结构」「微观经济学」）— used in titles & folder name.
2. **考试题型与分值结构？**（如 `选择10×3 / 填空10×2 / 简答3×5 / 编程3题=100`）
   → If unknown: *"不知道也行，我从你的素材里推断，回头再跟你确认。"*
3. **重点章节 / 范围？**（可选）
4. **输出目录？** 默认 `<科目>-考前冲刺/`。**强调：原始素材一律不改，只往新目录写。**

---

## Step 2 — Submit material (need ≥ 1)

Walk the list; for each, ask "有没有 / 路径或粘贴文本". Accept multiple. Make clear
**more sources = better grounding**, but one is enough to start.

| # | 素材 | 用途 | 接受 |
|---|---|---|---|
| 1 | 复习课**录屏** | 抽幻灯片帧 + 转写老师讲解 | mp4/mkv/mov/flv… 路径 |
| 2 | 单独**音频** | 只转写讲解 | mp3/wav/m4a… 路径 |
| 3 | **课件 / PPT** | 提要点与配图 | pptx/pdf 路径 |
| 4 | **笔记 / 讲义** | 知识底稿 | md/docx/txt/图片 路径 |
| 5 | **历年卷 / 真题** | 整理成带答案解析 | docx/pdf/图片 路径 |
| 6 | 老师**提纲 / AI 摘要** | 定位「点名考点」 | 直接粘文本 |
| 7 | 现有**学习库**（只参考不改） | 风格/内容参考 | 文件夹路径 |

Confirm each path exists before moving on. If a recording is large, mention extraction
may take a few minutes and can run in the background.

---

## Step 3 — Pick deliverables (multi-select)

Offer presets first, then the full menu (see `references/deliverables-catalog.md` for
each spec). Use a multi-select question.

**预设：** `全都要` ｜ `精简三件套`（① 笔记库 + ⑥ 刷题 + ④ 小抄）｜ `自定义`

| ✓ | 产物 | 一句话 |
|---|---|---|
| ① | 📒 MD 笔记库 (Obsidian) | MOC 总目录 + 分章 + `[[wikilink]]` 互链 |
| ② | 🖥 HTML 复习系统 | 考点卡片 + 速查表，明暗双主题 |
| ③ | 📄 一页速览 (md + html) | 必背点速览 |
| ④ | 🎴 A4 一页小抄 | 三栏打印优化，假定基础已会、只留采分点 |
| ⑤ | 📝 模拟卷 html | 可作答 + 自评 + 对照答案 |
| ⑥ | 🔥 刷题 App (Material 3) | 选/填/简答/混合/精选/错题本，即时反馈+正确率+localStorage |
| ⑦ | 🟦 磁贴刷题 (Win10 Metro) | 单选/多选/填空/简答/代码，导出导入 JSON |
| ⑧ | 🧩 知识架构交互图 | SVG 可点高亮（学科相关，如有结构性内容才建议） |
| ⑨ | ⭐ 点名考点 + 代码题逐行详解 | md + html |
| ⑩ | 🎯 历年卷整理与解析 | 带答案 + 代码（需提交了真题才有意义） |

Gate ⑩ on past papers existing; suggest ⑧ only when the subject has structural content
(architecture, pipelines, state machines). Otherwise present all ten.

---

## Step 4 — Style & options

Ask as a small batch of single/multi-selects. Recommended default is the first option.

1. **主视觉**（默认 **素雅温暖**）：
   - 🟫 素雅温暖（米黄/暖棕/赤陶，护眼）
   - 🌌 深色科技
   - 🎨 Material 3 / Pixel
   - 🟦 Windows 10 磁贴 Metro
   - 🖌 自定义主色（让用户给一个 hex）
   > 说明：刷题/磁贴两件套有各自的标志性风格，可单独沿用，不被主视觉覆盖。
2. **明暗**：双主题（默认）/ 仅亮 / 仅暗 — one `localStorage` key, anti-flash head script.
3. **题量**：精简(每章~10) / 标准(~20，默认) / 量大(30+)；**是否额外生成精选集？**
4. **对抗校对**（默认 **开**）：第二个 agent 复核每题贴合考点、抓签名/魔法值错误。
5. **汇报语言**（默认 中文）。
6. **部署**：**仅离线 `file://`（默认，且默认不上线）** / 另起本地静态服务器。Never publish
   online unless the user explicitly asks here.

---

## Step 5 — Confirm + generate

Echo a **one-screen summary** of every choice:

```
科目：单片机/MCS-51   题型：选10×3/填10×2/简3×5/编程3=100
素材：录屏✓  历年卷✓  AI摘要✓
产物：① ② ④ ⑥ ⑦ ⑩
风格：素雅温暖 · 明暗双主题 · 标准题量+精选 · 对抗校对开 · 离线
输出：单片机-考前冲刺/
```

Get an explicit go. Then run the generation pipeline (see SKILL.md), **verify
independently**, and report the finished file list with what was built and confirmation
that originals are untouched. Only claim "done" after the verifier passes — show evidence.

---

## Tone rules

- One step at a time; never dump all six steps at once.
- Every question has a sensible default and an explicit "可跳过".
- Reflect answers back so the user feels heard.
- If the user just says "全都要，你看着办" — accept it, pick defaults, confirm once, go.
