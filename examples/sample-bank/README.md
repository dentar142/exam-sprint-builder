# 示例题库 / Sample Question Bank

> **免责声明 / Disclaimer**
> 本目录内的所有题目均为**脱敏演示题目**，系作者原创编写，与任何真实考试、教材或版权内容无关。
> All questions in this directory are **sanitized demo questions** invented for illustration purposes. They are not derived from any real exam, textbook, or copyrighted material.

---

## 概览 / Overview

| 字段 | 内容 |
|------|------|
| 课程名 | 示例课程 · Sample Course |
| 文件 | `bank.json` |
| 题目数 | 12 |
| 覆盖题型 | `single`（单选）· `multi`（多选）· `fill`（填空）· `short`（简答）· `code`（编程） |
| 涉及章节 | 数制与编码 · MCU体系结构 · 串行通信 · 位操作 |

---

## 题型说明 / Question Types

| `type` | 中文名 | `answer` 格式 |
|--------|--------|--------------|
| `single` | 单选题 | `int`，选项数组中的正确项下标（**构建时自动打乱并重映射**） |
| `multi`  | 多选题 | `int[]`，所有正确项的下标列表（**构建时自动打乱并重映射**） |
| `fill`   | 填空题 | `string[][]`，外层=空格数，内层=可接受的等价答案列表 |
| `short`  | 简答题 | `string`，参考答案正文（由教师/评分者对照判卷） |
| `code`   | 编程题 | `{"code": "...", "explanation": "..."}` |

---

## 如何构建示例题 / How to Build the Sample Quiz

### 前提 / Prerequisites

- Python 3.7+
- 已准备好 HTML 模板文件（含占位符 `/*__BANK__*/[]`）

不改已提交的 `sample-quiz.html`、只做校验时，在仓库根目录跑夹具（会把两套刷题模板都构建到临时目录并运行 `verify_html.py`）：

```bash
python scripts/run_sample_fixture.py
```

### 构建命令 / Build Command

在本仓库根目录执行：

```bash
python scripts/build_quiz.py \
    --banks  examples/sample-bank \
    --template assets/templates/quiz-material3.html \
    --out     examples/sample-bank/sample-quiz.html
```

Windows PowerShell：

```powershell
python scripts\build_quiz.py `
    --banks  examples\sample-bank `
    --template assets\templates\quiz-material3.html `
    --out     examples\sample-bank\sample-quiz.html
```

### 预期输出 / Expected Output

```
[build_quiz] Bank files found: 1
  bank.json -> 12 questions loaded
[build_quiz] Statistics:
  Total questions : 12
  By type         : {'single': 4, 'multi': 2, 'fill': 3, 'short': 2, 'code': 1}
  Single-choice answer-index distribution: {0: 1, 1: 1, 2: 1, 3: 1}
    (percentages) {0: '25.0%', 1: '25.0%', 2: '25.0%', 3: '25.0%'}
[build_quiz] No problems found.
[build_quiz] Written: examples/sample-bank/sample-quiz.html (... bytes)
```

> **关于答案分布 / About the distribution**
> 注意 `Single-choice answer-index distribution` 的各键应大致均匀分布。这是因为构建脚本对每道选择题使用 `md5(id)` 派生的确定性随机种子打乱选项，消除"正确答案总在第一项"的位置偏差。详见 `references/question-bank-pipeline.md` 第4节。

---

## 自定义 / Customization

### 修改占位符 / Custom Placeholder

如果你的模板使用了不同的占位符（如 `/*__MY_BANK__*/[]`），传入 `--placeholder`：

```bash
python scripts/build_quiz.py \
    --banks examples/sample-bank \
    --template my-template.html \
    --out out.html \
    --placeholder "/*__MY_BANK__*/[]"
```

### 多文件题库 / Multiple Bank Files

将多个 JSON 文件放入同一目录，构建脚本会自动合并：

```
banks/
  ch01.json
  ch02.json
  ch03.json
```

```bash
python scripts/build_quiz.py --banks banks/ --template template.html --out quiz.html
```

或使用 glob 模式筛选：

```bash
python scripts/build_quiz.py --banks "banks/ch0*.json" --template template.html --out quiz.html
```

---

## 题目 JSON 结构速查 / Schema Quick Reference

```jsonc
{
  "id":          "ch01_q001",          // 全库唯一，建议 ch<章>_q<题号>
  "type":        "single",             // single | multi | fill | short | code
  "chapter":     "第1章 ...",          // 章节标题（可选，但推荐填写）
  "stem":        "题干文本",           // 题目正文
  "options":     ["A", "B", "C", "D"],// 仅 single/multi 需要
  "answer":      0,                    // 见上方题型说明
  "explanation": "解析文本",           // 必填；若来源无解析，由命题模型补充
  "tags":        ["tag1", "tag2"]      // 知识点标签（可选）
}
```

---

## 相关文档 / Related Docs

- `../../references/question-bank-pipeline.md` — 完整命题→审校→合并→打乱→注入→验证流水线说明
- `../../scripts/build_quiz.py` — 构建脚本源码
