# exam-sprint-builder

> 一键把复习课录屏 / 讲义 / 题库整理成可离线使用的考前冲刺包。
> *Turn lecture recordings, handouts, and question banks into a self-contained offline exam-prep bundle — in one guided session.*

`[MIT]` `[Node LTS]` `[Python 3.10+ optional]` `[Offline-first]` `[Claude Code Skill]`

---

## 产出物 / What It Produces

本 skill 按 [references/deliverables-catalog.md](references/deliverables-catalog.md) 生成最多 **10 项交付物**。默认输出目录是 `<科目>-考前冲刺/`（原始素材一律不改）。

| # | 交付物 | 典型文件名 | 模板 |
|---|--------|------------|------|
| 1 | MD 笔记库 (Obsidian) | `{subject}/_MOC.md` + 分章 | 无模板，智能体按目录手写 |
| 2 | HTML 复习系统 | `{subject}_study_system.html` | `assets/templates/study-system.html` |
| 3 | 一页速览 | `{subject}_speed_review.md` / `.html` | 无模板，智能体按目录手写 |
| 4 | A4 一页小抄 | `{subject}_cheat_sheet.html` | `assets/templates/cheatsheet-a4.html` |
| 5 | 模拟卷 | `{subject}_mock_exam.html` | 无模板，智能体按目录手写 |
| 6 | 刷题 App (Material 3) | `{subject}_quiz_app.html` | `assets/templates/quiz-material3.html` |
| 7 | 磁贴刷题 (Metro) | `{subject}_metro_quiz.html` | `assets/templates/quiz-metro.html` |
| 8 | 知识架构交互图 | `{subject}_knowledge_diagram.html` | 无模板，智能体按目录手写 |
| 9 | 点名考点 + 代码逐行详解 | `{subject}_teacher_points.md` / `.html` | 无模板，智能体按目录手写 |
| 10 | 历年卷整理与解析 | `{subject}_past_papers.md` / `.html` | 无模板，智能体按目录手写 |

预设：`全都要` / `精简三件套`（笔记库 + 刷题 + 小抄）/ `自定义`。无模板的 HTML 必须遵守 [references/html-conventions.md](references/html-conventions.md)。

**题库契约（唯一）：** 顶层是 JSON **数组**；题干字段是 `stem`；题型为 `single | multi | fill | short | code`。由 `scripts/build_quiz.py` 合并、打乱、注入。详见 [references/question-bank-pipeline.md](references/question-bank-pipeline.md)。

---

## 六步引导流程 / 6-Step Guided Flow

完整话术见 [references/intake-flow.md](references/intake-flow.md)。摘要：

0. **欢迎 + 依赖自检** — 只检查当前素材需要的工具（`node` 始终需要；录屏才要 `ffmpeg` / Whisper）。
1. **课程基本信息** — 科目名、题型分值（可跳过）、重点章节、输出目录（默认 `<科目>-考前冲刺/`）。
2. **提交素材（≥1）** — 录屏 / 音频 / 课件 / 笔记 / 历年卷 / 提纲或 AI 摘要 / 仅参考的现有学习库。
3. **选择交付物** — 预设或自定义，对应上表十项。
4. **风格与选项** — 主题、明暗、题量、对抗校对、汇报语言、仅离线 `file://`。
5. **确认并生成** — 回显一屏摘要，跑流水线，独立校验通过后才宣称完成。

---

## 环境要求 / Requirements

| 工具 | 版本 | 必需？ | 用途 |
|---|---|---|---|
| **Node.js** | LTS (18+) | **必需** | HTML 生成（`md2html.js`） |
| Python | 3.10+ | 可选 | 题库构建、校验、docx 图片、Whisper |
| ffmpeg | 任意现代版 | 可选（录屏输入时需要） | 录屏关键帧提取 |
| faster-whisper | 0.9+ | 可选（语音转录时需要） | 录屏语音转文字 |

> **注意：** 首次使用 faster-whisper 时会自动下载模型权重（base 约 145 MB）。后续运行使用本地缓存。

---

## 安装 / Install

### 方式 A — 作为 Claude Code skill 安装（推荐）

```bash
git clone https://github.com/dentar142/exam-sprint-builder \
  ~/.claude/skills/exam-sprint-builder
```

重启 Claude Code 后，skill 自动加载。

### 方式 B — 作为项目插件使用

```bash
git clone https://github.com/dentar142/exam-sprint-builder \
  .claude/skills/exam-sprint-builder
```

放在项目根目录下的 `.claude/skills/` 即可对当前项目生效。

---

## 使用方法 / Usage

在 Claude Code 中直接用自然语言触发：

```
把这段复习课录屏整理成复习资料
```

或者显式调用：

```
/exam-sprint-builder
```

Claude 会按六步引导你，并在当前目录下生成 `<科目>-考前冲刺/` 冲刺包。

本地校验示例题库（不改仓库内已提交的 `sample-quiz.html`）：

```bash
python scripts/run_sample_fixture.py
```

---

## 离线优先 / Offline-First

本 skill 产出的所有 HTML 文件均为**单文件内联**设计：

- 无 CDN 依赖，无外部字体请求，无网络图片
- CSS、JS、图片（base64）全部内联在单个 `.html` 文件中
- 支持 `file://` 协议直接双击打开，**不需要本地服务器**
- 默认**不部署上线**；除非用户明确要求，否则不上线

---

## 仓库结构 / Repo Structure

```
exam-sprint-builder/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── intake-flow.md
│   ├── deliverables-catalog.md
│   ├── content-grounding.md
│   ├── media-extraction.md
│   ├── question-bank-pipeline.md
│   ├── html-conventions.md
│   ├── themes.md
│   ├── verification.md
│   └── troubleshooting.md
├── assets/
│   ├── md2html.js
│   ├── theme-tokens.css
│   └── templates/
│       ├── study-system.html       # 占位 <!--__CONTENT__-->
│       ├── cheatsheet-a4.html      # 占位 <!--__SECTIONS__-->
│       ├── quiz-material3.html     # 占位 /*__BANK__*/[]
│       └── quiz-metro.html         # 占位 /*__BANK__*/[]
├── scripts/
│   ├── build_quiz.py
│   ├── extract_docx_images.py
│   ├── verify_html.py              # 4 项判定；不要校验未注入的模板
│   └── run_sample_fixture.py
└── examples/
    └── sample-bank/
        ├── README.md
        ├── bank.json               # 顶层数组，字段 stem
        └── sample-quiz.html
```

---

## 致谢 / Credit

Built with [Claude Code](https://claude.ai/code) — Anthropic's agentic coding assistant.

本 skill 从一次真实的单片机期末复习整理 session 中提炼而来，保留了实际遇到的工程问题与解法，去除了所有真实考试内容。

---

## License

MIT © 2026 Neko — see [LICENSE](LICENSE) for details.
