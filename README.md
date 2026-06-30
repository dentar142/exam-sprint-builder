# exam-sprint-builder

> 一键把复习课录屏 / 讲义 / 题库整理成可离线使用的考前冲刺包。  
> *Turn lecture recordings, handouts, and question banks into a self-contained offline exam-prep bundle — in one guided session.*

`[MIT]` `[Node LTS]` `[Python 3.10+ optional]` `[Offline-first]` `[Claude Code Skill]`

---

## 产出物 / What It Produces

运行本 skill 后，你将得到一个包含以下 **10 项交付物** 的冲刺包目录：

| # | 文件 | 说明 |
|---|------|------|
| 1 | `复习笔记.md` | 结构化 Markdown 笔记，含知识点、考点标注 |
| 2 | `复习系统.html` | 单文件离线复习站（明暗双主题，file:// 可直接打开） |
| 3 | `模拟卷.html` | 随机抽题模拟考卷，自动评分，含答题解析 |
| 4 | `题库.js` | 结构化题库（选择题 + 判断题 + 填空题 + 简答题） |
| 5 | `幻灯片/` | 从录屏中提取的关键帧截图（场景切换检测） |
| 6 | `转录文本.txt` | 录屏语音转文字稿（faster-whisper，可选） |
| 7 | `知识点索引.json` | 机器可读的知识点 → 题目 → 页码 三向索引 |
| 8 | `错题本模板.html` | 可记录错题与备注的离线错题本 |
| 9 | `考点速查卡.html` | 打印友好的 A4 速查卡（双栏，关键词高亮） |
| 10 | `troubleshooting.md` | 本次整理过程中遇到的坑与解决方案 |

---

## 六步引导流程 / 6-Step Guided Flow

1. **输入收集** — 提供讲义（docx/pdf/md）、录屏（mp4/mkv）、或已有题库（js/json/txt）中的任意组合。
2. **内容提取** — 自动解析 docx 图片、提取录屏截图帧、转录语音（可选）。
3. **知识点梳理** — Claude 整理章节结构、标注重点考点、生成 Markdown 笔记。
4. **题库构建** — 从原始题目中清洗、去重、分类，输出结构化 `题库.js`。
5. **页面生成** — 用内置模板生成复习站 HTML 与模拟卷 HTML，全部内联，无外部依赖。
6. **验证交付** — 脚本自动校验 HTML 完整性、题库格式，输出冲刺包目录。

---

## 环境要求 / Requirements

| 工具 | 版本 | 必需？ | 用途 |
|------|------|--------|------|
| **Node.js** | LTS (18+) | **必需** | HTML 生成、题库处理 |
| Python | 3.10+ | 可选 | docx 图片提取、验证脚本、Whisper 转录 |
| ffmpeg | 任意现代版 | 可选（录屏输入时需要） | 录屏关键帧提取 |
| faster-whisper | 0.9+ | 可选（语音转录时需要） | 录屏语音转文字 |

> **注意：** 首次使用 faster-whisper 时会自动下载模型权重（base 模型约 145 MB），请确保网络畅通。后续运行使用本地缓存，完全离线。

---

## 安装 / Install

### 方式 A — 作为 Claude Code skill 安装（推荐）

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/your-org/exam-sprint-builder \
  ~/.claude/skills/exam-sprint-builder
```

重启 Claude Code 后，skill 自动加载。

### 方式 B — 作为项目插件使用

```bash
git clone https://github.com/your-org/exam-sprint-builder \
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

Claude 会引导你完成六步流程，询问输入文件路径，并在当前目录下生成 `exam-sprint-output/` 冲刺包。

---

## 离线优先 / Offline-First

本 skill 产出的所有 HTML 文件均为**单文件内联**设计：

- 无 CDN 依赖，无外部字体请求，无网络图片
- CSS、JS、图片（base64）全部内联在单个 `.html` 文件中
- 支持 `file://` 协议直接双击打开，**不需要本地服务器**
- 默认**不部署上线**；如需部署，将 HTML 文件放到任意静态托管即可

---

## 仓库结构 / Repo Structure

```
exam-sprint-builder/
├── SKILL.md                        # Skill 入口描述与触发规则
├── README.md                       # 本文件
├── LICENSE                         # MIT License
├── references/
│   └── troubleshooting.md          # 已知坑点与解决方案
├── assets/
│   ├── md2html.js                  # Markdown → 单文件 HTML 转换器
│   ├── theme-tokens.css            # 明暗双主题 CSS 变量
│   └── templates/
│       ├── review-site.html        # 复习站模板
│       ├── quiz.html               # 模拟卷模板
│       ├── error-log.html          # 错题本模板
│       └── cheatsheet.html         # 速查卡模板
├── scripts/
│   ├── build_quiz.py               # 题库构建与洗牌（Python）
│   ├── extract_docx_images.py      # docx 图片提取
│   └── verify_html.py              # HTML 完整性校验
└── examples/
    └── sample-bank/                # 示例题库（虚构内容，无版权问题）
        ├── questions.js
        └── preview.html
```

---

## 致谢 / Credit

Built with [Claude Code](https://claude.ai/code) — Anthropic's agentic coding assistant.

本 skill 从一次真实的单片机期末复习整理 session 中提炼而来，保留了实际遇到的工程问题与解法，去除了所有真实考试内容。

---

## License

MIT © 2026 Neko — see [LICENSE](LICENSE) for details.
