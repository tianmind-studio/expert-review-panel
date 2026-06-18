# expert-review-panel — Prompt Recipes

This file gives copy-pasteable prompt patterns for real use.

## 1. Chinese academic paper / 中文论文严审

```text
帮我严审这份中文论文摘要。我准备投 SSCI / CSSCI，标准请按外审来，不要温和反馈。
请输出：
1. P0 / P1 / P2 问题清单
2. 每条问题都写位置 + 证据 + 原因 + 修改方向
3. 最终给 GO / CONDITIONAL GO / NO-GO

正文如下：
[粘贴内容]
```

Best for:
- 摘要、引言、开题报告、章节初稿

## 2. English abstract / harsh reviewer mode

```text
Peer review this abstract like a harsh SSCI / top-conference reviewer.
I do not want gentle feedback.
Please give:
- a P0 / P1 / P2 issue list
- location + evidence + reason + concrete fix direction for each major criticism
- a final GO / CONDITIONAL GO / NO-GO verdict

Text:
[paste abstract]
```

Best for:
- abstract triage before submission
- fast screening of overclaim / weak methods / unsupported conclusions

## 3. Business plan / BP brutal review

```text
帮我用投资人和尽调视角严审这份 BP。请重点看：
- 市场规模是否虚高
- 单位经济模型是否缺失
- 团队是否和业务匹配
- 目标和资源是否失衡

输出要求：
- P0 / P1 / P2 排序
- 每条意见都写位置 + 证据 + 原因 + 修改方向
- 最终必须给 GO / CONDITIONAL GO / NO-GO

内容如下：
[粘贴 BP 摘要或正文]
```

## 4. Code / architecture / security review

```text
Please review this code like a principal engineer plus security auditor.
I care more about production risk than style nitpicks.

Output format:
- P0 / P1 / P2 issue list
- for each major issue: exact location + quoted evidence + why it matters + fix direction
- final verdict: GO / CONDITIONAL GO / NO-GO

Code:
[paste code]
```

Best for:
- backend code
- architecture notes
- deployment logic
- security-sensitive snippets

## 5. WeChat Mini Program / 小程序提审前代码严审

```text
帮我严审这个微信小程序项目，按上线前代码审查 + 微信提审风险一起看。
请重点看：
- 云函数和后端接口有没有信任前端传来的 openid / userId / 金额
- 隐私接口、登录、手机号、定位、头像昵称的调用时机是否合理
- UGC / 评论 / 图片上传 / AI 生成内容有没有内容安全和处置闭环
- 支付、订阅消息、外部跳转、诱导分享是否有平台风险
- 首屏、分包、弱网、重复提交和错误态是否会影响审核或真实使用

输出要求：
- P0 / P1 / P2 问题清单
- 每条问题都写位置 + 证据 + 原因 + 修改方向
- 最终必须给 GO / CONDITIONAL GO / NO-GO

代码和配置如下：
[粘贴 app.json / pages / cloudfunctions / project.config.json / 提审说明]
```

Best for:
- 微信小程序、小游戏、云开发项目
- Taro / uni-app / mpvue 编译到 `mp-weixin` 的项目
- 提审前、被驳回后、涉及隐私/支付/UGC 的变更

## 6. Competition deck /答辩材料

```text
帮我严审这份比赛 PPT / 答辩稿，按评委会现场挑刺的标准来。
请重点看：
- 前 30 秒是否抓人
- 逻辑链是否闭环
- 亮点是否足够清楚
- 是否有会被评委一票否决的硬伤

输出：
- P0 / P1 / P2
- 每条问题的 位置 + 证据 + 原因 + 修改方向
- 最终裁决 GO / CONDITIONAL GO / NO-GO

内容如下：
[粘贴答辩稿 / 大纲]
```

## 7. Creative work / long-form writing

```text
Please review this creative work brutally but constructively.
Do not just say "the tone is interesting" or "it could be clearer." I want concrete criticism.

For every important critique, include:
- location
- evidence
- why it weakens the piece
- revision direction

Then give a final verdict:
GO / CONDITIONAL GO / NO-GO

Text:
[paste draft]
```

## 8. Short-input mode

If you only have a short input, tell the skill to stay lightweight.

```text
This is only a short paragraph. If a full panel would be overkill, do a lightweight but still harsh review.
```

This helps avoid excessive verbosity while preserving rigor.

## 9. Deep-review mode

If the work is large and important, say so explicitly.

```text
This is high stakes. Use a deep review mode with more experts, stronger disagreement surfacing, and a tougher submission threshold.
```

## 10. Best practice

When possible, include:
- target submission context
- desired strictness
- what kind of failure you fear most
- whether you want a lightweight or deep review

That gives the skill much better calibration.
