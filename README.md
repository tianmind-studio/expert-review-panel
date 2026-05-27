# expert-review-panel

> 一个面向作品投稿 / 答辩 / 提交前的严审 Claude skill：模拟顶级期刊审稿人、VC 尽调合伙人、资深架构师、竞赛评委组成的专家评审团，在真正提交前先翻出最容易致命的问题。
>
> A Claude skill for ruthless pre-submission review: papers, business plans, pitch decks, code, competition materials, and creative work, reviewed by a simulated multi-expert panel before you ship.

[![Release](https://img.shields.io/github/v/release/tianmind-studio/expert-review-panel)](https://github.com/tianmind-studio/expert-review-panel/releases/latest)
[![CI](https://github.com/tianmind-studio/expert-review-panel/actions/workflows/ci.yml/badge.svg)](https://github.com/tianmind-studio/expert-review-panel/actions/workflows/ci.yml)
[![GitHub Repo stars](https://img.shields.io/github/stars/tianmind-studio/expert-review-panel)](https://github.com/tianmind-studio/expert-review-panel/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Claude Skill](https://img.shields.io/badge/built%20for-Claude%20Skill-8A2BE2)](https://docs.claude.com)

## Quick Links

- Latest release: <https://github.com/tianmind-studio/expert-review-panel/releases/latest>
- Main skill: [`SKILL.md`](./SKILL.md)
- Prompt recipes: [`examples/prompt-recipes.md`](./examples/prompt-recipes.md)
- Full sample report: [`examples/full-sample-report-ssci-abstract.md`](./examples/full-sample-report-ssci-abstract.md)
- Output anatomy: [`examples/output-anatomy.md`](./examples/output-anatomy.md)
- Anti-groupthink design: [`references/anti-groupthink.md`](./references/anti-groupthink.md)
- Output validator: [`scripts/check_four_piece.py`](./scripts/check_four_piece.py)

## English Quickstart

### What You Get

This skill runs a strict review workflow instead of a polite "looks good overall" pass.

It produces:

- A full expert-by-expert review
- A priority-sorted issue list tagged `P0 / P1 / P2`
- A clear `GO / CONDITIONAL GO / NO-GO` verdict
- Critiques forced to follow the four-piece rule: `location + evidence + reason + concrete fix direction`

### Best-Fit Use Cases

- Academic papers and thesis drafts
- Business plans and pitch decks
- Code review and technical design review
- Product requirements documents
- Competition submissions and defense materials
- Creative writing and long-form content

### Example Prompts

- "Peer review this abstract like a harsh SSCI reviewer."
- "Red-team this pitch deck before investor meetings."
- "Review this code like a security auditor and principal architect."
- "帮我严审这份论文，看现在能不能投。"
- "这份 BP 有没有会被投资人一票否决的硬伤？"

### Install

Option 1: download the packaged skill from Releases:

1. Open <https://github.com/tianmind-studio/expert-review-panel/releases/latest>
2. Download `expert-review-panel-<version>.skill` or `expert-review-panel.skill`
3. Import the `.skill` file into Claude Desktop / Claude Code

Option 2: install from source:

```bash
git clone https://github.com/tianmind-studio/expert-review-panel.git ~/.claude/skills/expert-review-panel
```

Then restart Claude and invoke it with a review request.

### Why This Is Different

The main failure mode of LLM-based multi-expert review is not disagreement. It is shared blindness. Multiple simulated experts can still miss the same flaw because they come from the same base model.

This repo counters that with anti-groupthink mechanisms such as blind review, Devil's Advocate hard rules, minority-opinion protection, unanimous-check warnings, and chair self-challenge.

See [`references/anti-groupthink.md`](./references/anti-groupthink.md).

## 中文说明

### 它解决什么问题

大多数“帮我看看”式反馈的问题不是不友善，而是太温和、太空泛、太像安慰。真正要命的不是“文风可以更清晰”，而是：

- 论证链条里有断点，但没人直说
- 商业计划里有一票否决项，但没人点穿
- 代码里有生产级隐患，但 review 停留在表面
- 产品需求里有支付、隐私、上线风控问题，但排期前没人挡住
- 参赛材料方向跑偏，但答辩前没人扮演真正挑刺的评委

`expert-review-panel` 的目标，是在正式提交之前先做一次高压预审。

### 你会拿到什么

调用这个 skill 后，默认不是得到一段温和总结，而是得到三类可执行产物：

1. 完整专家报告：每位专家从自己的角色出发独立发言
2. 优先级问题清单：按 `P0 / P1 / P2` 排序，先改最致命的问题
3. 明确裁决：`GO / CONDITIONAL GO / NO-GO`

每条负面意见都应尽量满足四件套：

- 位置
- 证据
- 原因
- 修改方向

### 适用场景

| 作品类型 | 典型场景 |
| --- | --- |
| 中文学术论文 | SCI/SSCI/CSSCI 投稿、硕博论文、期刊外审模拟 |
| 英文学术论文 | Nature/Science、顶会、基金申请、PhD 答辩 |
| 商业方案 / PPT | 路演、BP 内审、投决会前 dry-run |
| 代码 / 技术方案 | 上线前 code review、架构评审、安全审计 |
| 产品需求文档 | MVP 范围评审、上线风险评审、指标与风控审查 |
| 参赛材料 | 互联网+、挑战杯、美赛、各类 PPT 答辩 |
| 创意文案 | 剧本、长文、广告创意 |

## Core Design

This skill relies on structure, not just harsh wording:

1. No vague praise: negative findings should include location, evidence, reason, and fix direction.
2. Dynamic panels: papers, business plans, code, products, and creative work use different expert libraries.
3. Anti-groupthink: blind review, Devil's Advocate rules, minority-opinion protection, and chair self-challenge reduce shared blind spots.
4. Final verdict required: every review ends with `GO / CONDITIONAL GO / NO-GO`.

## Workflow

```text
Phase 0  Intake and triage     -> identify artifact type, goal, and review depth
Phase 1  Independent review    -> each expert reviews independently with P0/P1/P2 severity
Phase 2  Cross-examination     -> surface disagreements and Devil's Advocate objections
Phase 3  Chair verdict         -> calibrate severity and issue the final verdict
Phase 4  Output self-check     -> run scripts/check_four_piece.py before delivery
```

## Repository Quality Gates

This repo includes basic maintainability checks:

- `evals/evals.json`: 4 baseline eval cases covering academic paper, business plan, code review, and product requirements review
- `scripts/check_four_piece.py`: validates review output structure
- GitHub Actions CI: validates repository structure and positive/negative fixture behavior

## Directory Structure

```text
expert-review-panel/
├── SKILL.md
├── references/
│   ├── academic-chinese.md
│   ├── academic-english.md
│   ├── business-docs.md
│   ├── code-tech.md
│   ├── competition.md
│   ├── creative-works.md
│   └── anti-groupthink.md
├── assets/
│   ├── review-report-template.md
│   ├── priority-list-template.md
│   └── verdict-template.md
├── scripts/
│   ├── check_four_piece.py
│   └── README.md
├── evals/
│   └── evals.json
├── tests/
│   └── fixtures/
│       ├── valid-review-report.md
│       └── invalid-review-report.md
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/ci.yml
```

## Self-Check Your Own Review Report

```bash
python scripts/check_four_piece.py your-review-report.md
```

The validator checks for:

- Clear verdict
- P0 / P1 / P2 labels
- Four-piece-rule signal density
- No leftover template placeholders

## Contributing

Issues and PRs are welcome.

High-value contribution areas:

- New expert libraries, such as medicine, law, game design, or grant review
- New eval cases in `evals/evals.json`
- Stronger anti-groupthink mechanisms
- Clearer output templates
- Better validation tooling and fixtures

For eval cases, prefer opening an eval proposal issue first. The repo includes:

- `.github/ISSUE_TEMPLATE/eval_case.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

When adding an eval case:

- Sync with current `main` before choosing the eval id
- Use the next available id
- Keep the diff narrow
- Avoid reformatting existing eval assertions
- Do not use `Fixes` / `Closes` for an issue that is already completed

## Inspiration

This skill was inspired by public work on multi-agent review and academic writing agents, including:

- [`wan-huiyan/agent-review-panel`](https://github.com/wan-huiyan/agent-review-panel)
- [`andrehuang/academic-writing-agents`](https://github.com/andrehuang/academic-writing-agents)
- [`Imbad0202/academic-research-skills`](https://github.com/Imbad0202/academic-research-skills)

This project focuses on cross-artifact review panels, localized Chinese academic / competition scenarios, and explicit anti-groupthink rules.

## License

[MIT](./LICENSE)

**Built by 王鑫 · Powered by Claude Skill**
