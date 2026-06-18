#!/usr/bin/env python3
"""
check_four_piece.py — expert-review-panel 输出后处理检查器

对 skill 产出的评审报告做程序化校验，强制执行 SKILL.md 里的硬承诺：
  1) 必须给出 GO / CONDITIONAL GO / NO-GO 三选一的明确裁决
  2) 问题清单至少 3 条，每条必须有 P0 / P1 / P2 严重级标签
  3) 全文四件套信号密度足够：位置 + 证据 + 原因 + 修改方向
  4) 每条可识别问题要覆盖四件套：位置 + 证据 + 原因 + 修改方向
  5) 报告里不得残留未替换的模板占位符（{xxx}）

使用：
    python3 scripts/check_four_piece.py <report.md>
    cat report.md | python3 scripts/check_four_piece.py -

退出码：
    0 — 所有检查通过
    1 — 存在未通过项（输出 JSON 会列出详情）
    2 — 参数错误 / 文件读取失败

注意：这是"粗检"，不是内容判断。脚本能发现"格式上的失守"——
比如完全没给裁决、没打 P0/P1/P2 标签、四件套关键词密度过低、
某条问题缺少证据字段、占位符没替换。它发现不了"说的有没有道理"
这种主观质量——那仍然依赖人类或另一个 LLM 做语义评审。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SEVERITY_RE = re.compile(r"\bP[012]\b")

PIECE_MARKERS: dict[str, list[str]] = {
    "位置": [
        r"位置[:：]",
        r"位于",
        r"第\s*\d+\s*(?:行|页|段|节|章|部分)",
        r"\bline\s*\d+",
        r"section\s*\d+",
    ],
    "证据": [
        r"证据[:：]",
        r"证据(?:是|为|来自|显示|表明|包括)",
        r"原文[:：]",
        r"引用[:：]",
        r"\bevidence\b",
        r"原文写道",
    ],
    "原因": [
        r"原因[:：]",
        r"为什么.{0,15}是问题",
        r"导致.{0,20}(?:问题|风险|后果)",
        r"\bbecause\b",
        r"原因在于",
    ],
    "修改方向": [
        r"修改方向[:：]",
        r"修改建议[:：]",
        r"建议[:：]",
        r"应(?:改为|改成|修改)",
        r"\bfix[:：]",
        r"\bsuggestion",
    ],
}

HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+")
ISSUE_HEADING_RE = re.compile(
    r"^\s{0,3}#{2,6}\s+(?:问题|Issue|Finding|缺陷|风险)\b",
    re.IGNORECASE,
)
TAGGED_HEADING_RE = re.compile(
    r"^\s{0,3}#{2,6}\s+.*\[\s*P[012]\s*\]",
    re.IGNORECASE,
)
SEVERITY_LINE_RE = re.compile(
    r"^\s*(?:[-*+]\s*)?(?:\*\*)?\s*(?:严重级|severity)\s*(?:\*\*)?\s*[:：]\s*(?:\*\*)?\s*\bP[012]\b",
    re.IGNORECASE,
)
TAGGED_LIST_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+.*\[\s*P[012]\s*\]",
    re.IGNORECASE,
)


def _count_piece_markers(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for piece, patterns in PIECE_MARKERS.items():
        total = 0
        for pat in patterns:
            total += len(re.findall(pat, text, flags=re.IGNORECASE))
        counts[piece] = total
    return counts


def check_verdict(text: str) -> dict[str, Any]:
    """检查是否含 GO / CONDITIONAL GO / NO-GO 裁决。

    这是 skill 最核心的硬承诺——主席必须敢于下结论，不能以"建议
    进一步打磨"这种模糊措辞收尾。
    """
    # 注意顺序：先匹配更长的 CONDITIONAL GO 和 NO-GO，避免被 GO 先匹掉
    patterns = [
        ("CONDITIONAL GO", r"CONDITIONAL\s+GO"),
        ("NO-GO", r"NO[\s-]?GO"),
        ("GO", r"(?<!CONDITIONAL\s)(?<!NO-)(?<!NO\s)\bGO\b"),
    ]
    found: list[str] = []
    for name, pat in patterns:
        if re.search(pat, text):
            found.append(name)
    if found:
        return {
            "passed": True,
            "evidence": f"found verdict(s): {found}",
        }
    return {
        "passed": False,
        "evidence": "no GO / CONDITIONAL GO / NO-GO verdict found — main chair must deliver a clear verdict",
    }


def check_severity_tags(text: str) -> dict[str, Any]:
    """检查 P0/P1/P2 严重级标签。至少 3 条带标签的问题。"""
    p0 = len(re.findall(r"\bP0\b", text))
    p1 = len(re.findall(r"\bP1\b", text))
    p2 = len(re.findall(r"\bP2\b", text))
    total = p0 + p1 + p2
    counts = {"P0": p0, "P1": p1, "P2": p2, "total": total}
    if total >= 3:
        return {
            "passed": True,
            "evidence": f"severity tag counts: {counts}",
            "counts": counts,
        }
    return {
        "passed": False,
        "evidence": f"severity tag counts: {counts} — expected ≥3 tagged issues",
        "counts": counts,
    }


def check_four_piece(text: str) -> dict[str, Any]:
    """粗检四件套（位置 / 证据 / 原因 / 修改方向）的关键词密度。

    阈值：每类至少 3 次出现。这是保底信号——低于此说明主席没执行
    "四件套"硬规定。脚本做不了"每一条都含四件套"的语义判定，只能
    保证整体密度合理。
    """
    counts = _count_piece_markers(text)
    missing: list[str] = []
    for piece, total in counts.items():
        if total < 3:
            missing.append(f"{piece}({total})")
    if missing:
        return {
            "passed": False,
            "evidence": f"low four-piece marker density: {', '.join(missing)} (expected ≥3 each)",
            "counts": counts,
        }
    return {
        "passed": True,
        "evidence": f"four-piece marker counts: {counts}",
        "counts": counts,
    }


def _strip_code_regions(text: str) -> str:
    """去掉 fenced code blocks 和 inline code spans。

    在 Markdown 评审报告里讨论模板本身时，作者可能写出 `{xxx}` 之
    类的"引用性占位符"作为例子——这不是未替换的占位符，是在讲占
    位符这件事。做占位符检测前要先把这些代码片段剥掉。
    """
    # fenced code blocks: ```...```
    text = re.sub(r"```[\s\S]*?```", "", text)
    # inline code spans: `...`
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def _heading_level(line: str) -> int | None:
    match = HEADING_RE.match(line)
    return len(match.group(1)) if match else None


def _is_issue_heading(line: str) -> bool:
    return bool(ISSUE_HEADING_RE.search(line) or TAGGED_HEADING_RE.search(line))


def _split_markdown_table_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _is_table_separator(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def _table_can_hold_issues(headers: list[str]) -> bool:
    joined = "".join(headers)
    return (
        "位置" in joined
        and ("修改方向" in joined or "修改建议" in joined)
        and ("问题" in joined or "证据" in joined or "原因" in joined)
    )


def _nearest_heading_severity(lines: list[str], index: int) -> str | None:
    for cursor in range(index, -1, -1):
        if _heading_level(lines[cursor]) is None:
            continue
        severity = SEVERITY_RE.search(lines[cursor])
        return severity.group(0) if severity else None
    return None


def _table_row_to_issue_block(
    headers: list[str],
    cells: list[str],
    fallback_severity: str | None,
) -> str | None:
    if len(cells) < len(headers):
        cells = cells + [""] * (len(headers) - len(cells))
    pairs = list(zip(headers, cells))
    if not any(cell.strip() for _, cell in pairs):
        return None

    labeled = "\n".join(f"{header}：{cell}" for header, cell in pairs if header)
    if not SEVERITY_RE.search(labeled):
        if not fallback_severity:
            return None
        labeled = f"严重级：{fallback_severity}\n{labeled}"
    return labeled


def _extract_issue_blocks(text: str) -> list[dict[str, Any]]:
    """Extract explicit issue blocks that should each carry the four pieces.

    The parser intentionally ignores summary tables and KPI bullets such as
    "P0: 2 条 / P1: 3 条" because those rows often summarize issues rather
    than express a full finding. It focuses on issue headings, severity lines,
    and bracketed list items like "- **[P0]** ...".
    """
    stripped = _strip_code_regions(text)
    lines = stripped.splitlines()
    blocks: list[dict[str, Any]] = []
    covered_ranges: list[tuple[int, int]] = []

    for index, line in enumerate(lines):
        if not _is_issue_heading(line):
            continue

        level = _heading_level(line) or 6
        end = len(lines)
        for cursor in range(index + 1, len(lines)):
            next_level = _heading_level(lines[cursor])
            if next_level is not None and next_level <= level:
                end = cursor
                break

        block = "\n".join(lines[index:end]).strip()
        if SEVERITY_RE.search(block):
            blocks.append({"start_line": index + 1, "text": block})
            covered_ranges.append((index, end))

    def is_covered(index: int) -> bool:
        return any(start <= index < end for start, end in covered_ranges)

    for index in range(len(lines) - 1):
        if is_covered(index):
            continue
        headers = _split_markdown_table_row(lines[index])
        separator = _split_markdown_table_row(lines[index + 1])
        if not headers or not separator or not _is_table_separator(separator):
            continue
        if not _table_can_hold_issues(headers):
            continue

        fallback_severity = _nearest_heading_severity(lines, index)
        cursor = index + 2
        while cursor < len(lines):
            cells = _split_markdown_table_row(lines[cursor])
            if not cells:
                break
            if _is_table_separator(cells):
                cursor += 1
                continue
            block = _table_row_to_issue_block(headers, cells, fallback_severity)
            if block:
                blocks.append({"start_line": cursor + 1, "text": block})
            cursor += 1

    for index, line in enumerate(lines):
        if is_covered(index):
            continue
        if not (SEVERITY_LINE_RE.search(line) or TAGGED_LIST_RE.search(line)):
            continue

        end = len(lines)
        for cursor in range(index + 1, len(lines)):
            if _heading_level(lines[cursor]) is not None:
                end = cursor
                break
            if SEVERITY_LINE_RE.search(lines[cursor]) or TAGGED_LIST_RE.search(lines[cursor]):
                end = cursor
                break

        block = "\n".join(lines[index:end]).strip()
        if SEVERITY_RE.search(block):
            blocks.append({"start_line": index + 1, "text": block})

    blocks.sort(key=lambda item: item["start_line"])
    return blocks


def _summarize_issue_block(block: str) -> str:
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        return re.sub(r"\s+", " ", line)[:100]
    return "(empty issue block)"


def check_issue_blocks(text: str) -> dict[str, Any]:
    """检查每条显式问题是否各自包含四件套。

    旧版只检查整篇报告的关键词密度，可能出现某条问题缺"证据"但全
    文仍通过的假阳性。这里对可识别的问题块逐条检查，确保每个 P0 /
    P1 / P2 finding 至少有位置、证据、原因、修改方向四类信号。
    """
    blocks = _extract_issue_blocks(text)
    if len(blocks) < 3:
        return {
            "passed": False,
            "evidence": f"found {len(blocks)} explicit issue block(s), expected ≥3 with per-issue four-piece structure",
            "issue_count": len(blocks),
        }

    incomplete: list[dict[str, Any]] = []
    for block in blocks:
        counts = _count_piece_markers(block["text"])
        missing = [piece for piece, count in counts.items() if count == 0]
        if missing:
            severity = SEVERITY_RE.search(block["text"])
            incomplete.append({
                "line": block["start_line"],
                "severity": severity.group(0) if severity else None,
                "missing": missing,
                "summary": _summarize_issue_block(block["text"]),
                "counts": counts,
            })

    if incomplete:
        return {
            "passed": False,
            "evidence": f"{len(incomplete)} issue block(s) missing required four-piece markers",
            "issue_count": len(blocks),
            "incomplete": incomplete[:10],
        }

    return {
        "passed": True,
        "evidence": f"all {len(blocks)} explicit issue block(s) include location/evidence/reason/fix markers",
        "issue_count": len(blocks),
    }


def check_no_placeholders(text: str) -> dict[str, Any]:
    """检查是否存在未替换的模板占位符 {xxx}（忽略代码块 / inline code）。

    SKILL.md 模板里大量使用 {...} 作为占位。如果 LLM 照搬模板忘
    了替换，就会在最终报告里留下未填充的占位符——用户看到会以为
    skill 半途崩了。但代码块 / inline code 里的 {...} 是在"讲"
    占位符而非遗留占位符，所以先剥掉这些区域再检测。
    """
    stripped = _strip_code_regions(text)
    # 找 {内容} 形式，排除明显的 JSON / f-string 模式
    placeholders = re.findall(r"\{[^{}\n\"]{2,80}\}", stripped)
    likely_template = [
        p for p in placeholders
        if not (":" in p and re.search(r'[\w\s]+":\s*', p))
        and not re.match(r"\{[a-z_]+\s*=", p)
    ]
    if likely_template:
        sample = likely_template[:5]
        return {
            "passed": False,
            "evidence": f"unreplaced template placeholders found ({len(likely_template)} total), e.g.: {sample}",
        }
    return {
        "passed": True,
        "evidence": "no unreplaced template placeholders (after stripping code regions)",
    }


def run_all_checks(text: str) -> dict[str, Any]:
    checks = {
        "verdict": check_verdict(text),
        "severity_tags": check_severity_tags(text),
        "four_piece": check_four_piece(text),
        "issue_blocks": check_issue_blocks(text),
        "no_placeholders": check_no_placeholders(text),
    }
    all_passed = all(c["passed"] for c in checks.values())
    return {
        "all_passed": all_passed,
        "checks": checks,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "usage: python3 check_four_piece.py <report.md | ->",
            file=sys.stderr,
        )
        return 2

    arg = sys.argv[1]
    try:
        text = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    except OSError as err:
        print(f"cannot read input: {err}", file=sys.stderr)
        return 2

    result = run_all_checks(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
