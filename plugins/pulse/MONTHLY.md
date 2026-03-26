# Monthly Dimension — Review, Plan & Quick Record

This document is loaded when the user invokes `pulse monthly`, `pulse monthly-review`, `pulse monthly-plan`, or `pulse record`. It defines all workflows for the monthly time dimension, including the lightweight quick-record flow.

Before executing any flow, complete the First-Run Check defined in SKILL.md. Load ADVISOR.md for all analysis and generation steps.

---

## Command Dispatch

Determine the sub-command from the user's input and execute the corresponding flow:

| Trigger | Flow |
|---------|------|
| `pulse record` / `记录` | [Quick Record Flow](#1-quick-record-flow-pulse-record) |
| `pulse monthly-review` / `月度回顾` | [Monthly Review Flow](#2-monthly-review-flow-pulse-monthly-review) |
| `pulse monthly-plan` / `月计划` | [Monthly Plan Flow](#3-monthly-plan-flow-pulse-monthly-plan) |
| `pulse monthly` | [Combined Flow](#4-combined-flow-pulse-monthly) — execute review first, then plan |

---

## 1. Quick Record Flow (`pulse record`)

This is a lightweight command for quick-capturing daily life events into the current month's record area. It should be fast — minimal interaction, smart defaults.

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` to obtain `vault_path`, `pulse_dir`, `timezone`, and `language`.
2. Set the monthly directory path: `{vault_path}/{pulse_dir}/30. Monthly/`.

### Step 2: Parse User Input

Extract three (or four) elements from the user's natural language input:

1. **Date** — resolve using the Date Resolution Table below.
2. **Content** — the record text (what happened).
3. **Category** — auto-classify using the Category Keywords Table below.
4. **Amount** — for Wealth dimension only, extract monetary amounts (see Amount Extraction rules).

If the user provides a bare command (`pulse record`) with no content, prompt:

> 请输入你要记录的内容（例如：昨天跑了5公里 / spent $50 on books）

### Step 3: Resolve Date

Use the following table to resolve the date from the user's input. If no date indicator is found, default to today.

#### Date Resolution Table

| Input Pattern | Resolution | Example (if today = 2026-02-21) |
|--------------|------------|--------------------------------|
| (none) / today / 今天 | Today's date | 2026-02-21 |
| yesterday / 昨天 | Yesterday | 2026-02-20 |
| 前天 | Day before yesterday | 2026-02-19 |
| last Monday / 上周一 | Previous week's Monday | 2026-02-09 |
| last Tuesday / 上周二 | Previous week's Tuesday | 2026-02-10 |
| last Wednesday / 上周三 | Previous week's Wednesday | 2026-02-11 |
| last Thursday / 上周四 | Previous week's Thursday | 2026-02-12 |
| last Friday / 上周五 | Previous week's Friday | 2026-02-13 |
| last Saturday / 上周六 | Previous week's Saturday | 2026-02-14 |
| last Sunday / 上周日 | Previous week's Sunday | 2026-02-15 |
| this Monday / 本周一 / 周一 | This week's Monday | 2026-02-16 |
| this Tuesday / 本周二 / 周二 | This week's Tuesday | 2026-02-17 |
| (other weekdays follow same pattern) | ... | ... |
| Jan 15 / 1月15日 / 1-15 | Current year, specified date | 2026-01-15 |
| 2026-02-18 | Exact date | 2026-02-18 |

**Validation**: The resolved date must NOT be in the future. If it is, reject and ask the user to correct:

> 日期 {date} 是未来日期，无法记录。请确认日期。

### Step 4: Classify Category

Match the user's content against keywords to determine which Life Wheel dimension the record belongs to.

#### Category Keywords Table

| Dimension | Section Header | Keywords (EN) | Keywords (ZH) |
|-----------|---------------|---------------|---------------|
| Health | `### 健康` | run, gym, swim, workout, exercise, yoga, cycling, sleep, doctor, hospital, medicine, walk, hike, diet, weight | 跑步, 健身, 游泳, 锻炼, 运动, 瑜伽, 骑行, 睡眠, 看病, 医院, 吃药, 体检, 散步, 徒步, 饮食, 体重 |
| Career | `### 事业/学习` | work, project, meeting, presentation, deadline, study, course, exam, code, deploy, release, review, client | 工作, 项目, 会议, 汇报, 截止, 学习, 课程, 考试, 培训, 代码, 上线, 发布, 评审, 客户 |
| Wealth | `### 财务` | bought, spent, paid, invest, salary, bonus, save, budget, income, expense, refund, tax, stock, fund | 买了, 花了, 消费, 投资, 工资, 奖金, 存钱, 预算, 收入, 支出, 报销, 税, 股票, 基金 |
| Family | `### 家庭` | family, parents, mom, dad, brother, sister, home, child, kids | 家人, 父母, 爸, 妈, 兄弟, 姐妹, 回家, 家庭, 孩子, 儿子, 女儿 |
| Intimate | `### 亲密关系` | partner, spouse, wife, husband, boyfriend, girlfriend, date, anniversary | 伴侣, 老婆, 老公, 男友, 女友, 约会, 纪念日 |
| Social | `### 社交` | friend, party, gathering, hangout, reunion, meetup, dinner | 朋友, 聚会, 聚餐, 饭局, 团建, 见面 |
| Growth | `### 个人成长` | book, read, learn, skill, practice, reflect, meditation, journal | 看书, 阅读, 学习, 技能, 练习, 反思, 冥想, 复盘, 写日记 |
| Leisure | `### 休闲` | movie, game, travel, vacation, hobby, relax, music, concert, show | 电影, 游戏, 旅行, 度假, 爱好, 放松, 音乐, 休息, 娱乐, 演出 |

**Classification priority** (when content matches multiple categories):
Health > Career > Wealth > Family > Intimate > Social > Growth > Leisure

**If no match**: Present the 8 dimensions numbered and ask the user to choose:

> 无法自动识别类别，请选择维度：
> 1. 健康  2. 事业/学习  3. 财务  4. 家庭
> 5. 亲密关系  6. 社交  7. 个人成长  8. 休闲

### Step 5: Extract Amount (Wealth dimension only)

If the category is Wealth (财务), attempt to extract a monetary amount from the content:

| Pattern | Example | Extracted |
|---------|---------|-----------|
| `$` + number | spent $100 | $100 |
| number + `dollars` | 100 dollars | $100 |
| `spent` + number | spent 100 | $100 |
| `￥` + number | ￥100 | ¥100 |
| number + `元` / `块` | 花了100元, 50块 | ¥100, ¥50 |
| `花了` + number | 花了200 | ¥200 |

If no amount can be extracted, set amount to `-`.

### Step 6: Locate or Create Monthly Review File

1. Determine target month from the resolved date (YYYY-MM format).
2. Construct file path: `{vault_path}/{pulse_dir}/30. Monthly/{YYYY-MM}-monthly-review.md`.
3. If the file exists, read it.
4. If the file does NOT exist, create it from `templates/monthly-review-template.md`:
   - Replace `{year}` with the target year.
   - Replace `{month}` with the target month (2-digit, zero-padded).
   - Replace `{created_at}` with the current datetime.
   - Replace `{last_updated}` with the current datetime.
   - Replace `{month_id}` with `YYYY-MM`.
   - Leave all review sections (below the `---` separator after the record area) as template placeholders — they will be filled by `pulse monthly-review` later.

### Step 7: Append Record

1. Find the correct category section in the file by matching the section header (e.g., `### 健康`, `### 财务`).
2. Locate the table under that section header.
3. Append a new row at the end of the existing table rows (before any blank line or next section):
   - **Standard dimensions**: `| {MM-DD} | {content} | {note} |`
   - **Wealth dimension**: `| {MM-DD} | {content} | {amount} | {note} |`
4. The `{note}` field defaults to empty unless the user explicitly provides additional notes.
5. Update `{last_updated}` in the file frontmatter to the current datetime.

### Step 8: Confirm to User

Display a confirmation summary:

```
已记录到 [{YYYY-MM} 月度回顾] - {dimension_name}：
  日期: {date}
  内容: {content}
  {amount_line if wealth}
```

Where `{amount_line}` is shown only for wealth records: `金额: {amount}`.

---

## 2. Monthly Review Flow (`pulse monthly-review`)

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` to obtain `vault_path`, `pulse_dir`, `timezone`, `language`, and `sources`.
2. Set paths:
   - Monthly directory: `{vault_path}/{pulse_dir}/30. Monthly/`
   - Weekly directory: `{vault_path}/{pulse_dir}/20. Weekly/`
   - Daily directory: `{vault_path}/{pulse_dir}/10. Daily/`
   - Annual directory: `{vault_path}/{pulse_dir}/40. Annual/`

### Step 2: Determine Target Month

1. Ask the user which month to review, or default to the previous month (if today is before the 5th) or the current month (if today is after the 25th).
2. If ambiguous, ask:

> 要回顾哪个月？
> 1. {current_month} (本月)
> 2. {previous_month} (上月)

### Step 3: Gather Source Data

Collect all relevant data for the target month:

1. **Monthly plan**: Read `{monthly_dir}/{YYYY-MM}-monthly-plan.md` — this is the baseline for plan-vs-actual comparison. If not found, note its absence but proceed.
2. **Existing monthly review file**: Read `{monthly_dir}/{YYYY-MM}-monthly-review.md` — **CRITICAL**: this file may contain daily record tables at the top that MUST be preserved.
3. **Weekly review files**: Scan `{weekly_dir}/` for files matching the target month (filenames containing dates within YYYY-MM). Read all matched files.
4. **Daily files**: Scan `{daily_dir}/` for files within the target month for supplementary detail. Read all matched files.
5. **External source files**: For `sources.monthly-review.dirs`, scan each directory for `.md` files matching the target month pattern (`YYYY-MM`). Read all matched files.
6. **Annual plan**: Read `{annual_dir}/{YYYY}-annual-plan.md` for OKR alignment verification.
7. **Previous month's review**: Read `{monthly_dir}/{PREV-YYYY-MM}-monthly-review.md` for Life Wheel comparison data (Section 三).

### Step 4: Present Data Summary

Present a summary of aggregated data to the user for confirmation:

- Number of weekly reviews found and their date ranges
- Number of daily entries found
- Number of daily records in the record area (from the existing monthly-review file)
- Monthly plan status (found/not found)
- Annual plan status (found/not found)

Ask:

> 以上是收集到的数据概况。是否继续生成月度回顾？如有需要补充的信息请告诉我。

### Step 4.5: Process Inline Directives

Follow the Inline Directive Processing rules defined in SKILL.md. Scan all files read in Steps 3 (monthly plan, existing monthly review, weekly reviews, daily files, external sources, annual plan, previous month's review) for `{{{...}}}` directives. If any are found, present them to the user, execute upon confirmation, and remove the markers from the source files before proceeding.

### Step 5: Generate Monthly Review

Following ADVISOR.md guidelines (independent thinking, evidence-based, structural fixes), generate the comprehensive review. Fill each section:

#### Section 一: Result Review (结果回顾)
- Compare Must Win outcome against the monthly plan's defined Must Win
- Verify each result commitment against its stated evidence criteria
- Calculate overall achievement rate
- Identify the 3 most effective investments (time/effort with highest return)
- Identify the 3 busiest-but-least-effective activities

#### Section 二: Cost & System Health (代价与系统健康)
- Identify cost events across health, relationships, and long-term capability
- Analyze mental load — what occupied the most mental bandwidth
- Score energy level, sleep quality, recovery sufficiency (1-10)
- Sustainability projection: "If this continues for 3 months, what happens?"

#### Section 三: Life Wheel Quick Retest (生命之轮快速重测)
- Score each of the 8 dimensions (1-10)
- Compare with previous month's scores (from previous review file)
- Calculate deltas and explain the 2-3 biggest changes

#### Section 四: Failure Pattern Recognition (失败模式识别)
- Identify failures that occurred 2+ times during the month
- For each pattern: surface cause, root cause, systemic/environmental factors
- Propose correction strategies — structural, not willpower-based

#### Section 五: Subtraction Execution Review (减法承诺执行)
- Check each subtraction commitment from the monthly plan
- Status: executed / partially executed / not executed
- Assess the effect of successful subtractions

#### Section 六: Recovery & Input Execution (恢复与输入执行)
- Review planned recovery activities vs. actual execution
- Review planned input activities vs. actual execution
- Identify what got squeezed and by what disruptor

#### Section 七: Rolling Adjustment (下月滚动调整)
- Suggest next month's theme based on patterns observed
- Recommend commitment adjustments (continue / stop / replace)
- Propose next month's Must Win

#### Section 八: Key Insights (关键洞察)
- 1-3 sentences capturing the most important learning from this month

#### Appendix: Annual KR Progress (年度 KR 进度更新)
- Update progress on each annual KR based on this month's contributions
- Traffic light status: green (on track), yellow (slight deviation), red (significantly behind)

### Step 6: Write to File

1. Read the existing `{YYYY-MM}-monthly-review.md` file again (to get the latest version).
2. **CRITICAL**: Preserve the entire daily record area (everything from `## 日常记录` up to and including the `---` separator line that precedes `## 以下内容由月末`).
3. Replace everything from `## 以下内容由月末` onward with the newly generated review content.
4. Update `{last_updated}` in the frontmatter.
5. If the file does not exist at all, create it from `templates/monthly-review-template.md` first, then fill both record area (empty tables) and review sections.
6. Write the file to: `{vault_path}/{pulse_dir}/30. Monthly/{YYYY-MM}-monthly-review.md`.

### Step 7: Confirm

Display a summary of key findings:

```
月度回顾已生成: {YYYY-MM}-monthly-review.md

核心发现:
- Must Win: {status}
- 承诺达成率: {x}/{total}
- 生命之轮变化最大维度: {dimension} ({delta})
- 关键洞察: {insight_summary}
```

---

## 3. Monthly Plan Flow (`pulse monthly-plan`)

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` to obtain `vault_path`, `pulse_dir`, `timezone`, `language`, and `sources`.
2. Set paths (same as monthly-review flow).

### Step 2: Determine Target Month

1. Default to next month if today is after the 20th; otherwise default to current month.
2. If ambiguous, ask:

> 要制定哪个月的计划？
> 1. {current_month} (本月)
> 2. {next_month} (下月)

### Step 3: Check for Existing Plan

1. Check if `{YYYY-MM}-monthly-plan.md` already exists.
2. If it exists, warn and ask:

> 已存在 {YYYY-MM} 月度计划。是否覆盖？
> 1. 覆盖现有计划
> 2. 取消

If the user chooses cancel, stop the flow.

### Step 4: Gather Source Data

1. **Current/recent monthly review**: Read `{monthly_dir}/{YYYY-MM}-monthly-review.md` or the most recent review available. This provides the rolling adjustment suggestions (Section 七 of the review).
2. **Annual plan**: Read `{annual_dir}/{YYYY}-annual-plan.md` for OKR and theme alignment.
3. **External source files**: For `sources.monthly-plan.dirs`, scan each directory for `.md` files matching the target month pattern. Read all matched files.
4. **Previous monthly plan**: Read the previous month's plan for continuity context.

### Step 5: Generate Plan Suggestions

Following ADVISOR.md guidelines, generate a complete monthly plan with the following sections. Present each section to the user for confirmation/adjustment before finalizing.

#### Monthly Theme (月度主题)
- Derive from annual theme / quarterly theme and recent review insights
- Must be a clear, focused direction statement

#### Success Criteria (成功标准)
- 2-3 measurable items
- "At month end, if at least 2 of these are true, the month was successful"

#### Must Win
- One non-negotiable deliverable, expressed as a result state (not an activity)
- Must align with a specific annual KR
- Must have clear verification evidence

#### Result Commitments (结果承诺, max 3)
- Each must: align with an annual KR, be measurable, have a deadline
- Express as result states: "X is in state Y by date Z"
- Challenge if the user proposes more than 3 — reference ADVISOR.md Rule 1

#### Action System Design (行动系统)
For each commitment, define:
- **Minimal action** (5-20 min startup task to reduce resistance)
- **Environment/system change** (structural support, not willpower)
- **Failure pre-mortem** (1-2 risks and fallback plans)

#### Subtraction Commitments (减法承诺, 1-3 items)
- What to stop or reduce this month
- Why (what resource does it free)
- ADVISOR.md Rule: no new additions without corresponding subtractions

#### Recovery & Input Reservations (恢复与输入预留)
- Protected non-output activities (rest, learning, reflection)
- Anti-squeeze strategy: identify the most likely disruptor and protection mechanism
- ADVISOR.md Rule: recovery is not optional

#### Weekly Rhythm Suggestions (周节奏建议)
- Suggested fixed time windows for deep work, review, recovery
- Key dates this month (deadlines, checkpoints, events)

#### Annual Alignment Check (年度对齐检查)
- Verification table: Does Must Win push annual KR? Are commitments focused on priority dimensions? Does subtraction align with annual subtraction list? Is recovery protected?

### Step 6: User Confirmation

Present the complete plan and ask:

> 以上是 {YYYY-MM} 月度计划建议。请确认或提出调整意见。
> 1. 确认并保存
> 2. 我有调整意见（请直接说明）

If the user requests adjustments, revise and re-present. Repeat until confirmed.

### Step 7: Save Plan

1. Create the plan file from `templates/monthly-plan-template.md`.
2. Replace all placeholders with the confirmed content.
3. Save to: `{vault_path}/{pulse_dir}/30. Monthly/{YYYY-MM}-monthly-plan.md`.

### Step 8: Create Next Month's Empty Review File

1. Determine the next month (the month being planned).
2. Construct path: `{vault_path}/{pulse_dir}/30. Monthly/{YYYY-MM}-monthly-review.md`.
3. **If the file already exists, do NOT overwrite** — daily records may already be present.
4. If the file does not exist, create it from `templates/monthly-review-template.md`:
   - Fill metadata placeholders (year, month, created_at, month_id, year reference).
   - Keep all record tables empty (ready for `pulse record`).
   - Keep all review sections as placeholders (to be filled by `pulse monthly-review` later).

### Step 9: Confirm

```
月度计划已保存: {YYYY-MM}-monthly-plan.md
下月回顾文件已创建: {YYYY-MM}-monthly-review.md（用于日常记录）

本月 Must Win: {must_win_summary}
结果承诺: {count} 项
减法承诺: {count} 项
```

---

## 4. Combined Flow (`pulse monthly`)

Execute the monthly review and monthly plan in a single session with shared context.

### Execution Order

1. **Run Monthly Review Flow** (Steps 1-7 from Section 2).
2. **Pass review context to plan flow** — the review's Section 七 (Rolling Adjustment) feeds directly into the plan's theme, commitments, and Must Win.
3. **Run Monthly Plan Flow** (Steps 1-9 from Section 3), skipping redundant data loading — reuse data already gathered in the review phase.

### Context Sharing

The following data from the review feeds into the plan:

| Review Output | Plan Input |
|--------------|------------|
| Section 七 next theme suggestion | Monthly theme starting point |
| Section 七 commitment adjustments | Commitment drafts |
| Section 七 next Must Win | Must Win starting point |
| Section 四 failure patterns + corrections | Action system risk pre-mortems |
| Section 五 subtraction results | Subtraction commitment refinement |
| Section 六 squeeze analysis | Anti-squeeze strategy |
| Section 三 Life Wheel scores | Dimension priority for commitments |
| Appendix KR progress | Annual alignment verification |

---

## 5. File Operations Reference

### Output Directory

All monthly files are stored in: `{vault_path}/{pulse_dir}/30. Monthly/`

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Monthly Plan | `YYYY-MM-monthly-plan.md` | `2026-03-monthly-plan.md` |
| Monthly Review | `YYYY-MM-monthly-review.md` | `2026-02-monthly-review.md` |

### Templates

| File | Template Source |
|------|---------------|
| Monthly Plan | `templates/monthly-plan-template.md` |
| Monthly Review | `templates/monthly-review-template.md` |

### File Creation

When creating files from templates, use Bash heredoc method for long documents. Replace all `{placeholder}` tokens with actual data. Generate content in the user's configured language (`language` field from config).

### Cross-References (Obsidian Links)

- Monthly plan links to annual plan: `[[{YYYY}-annual-plan]]`
- Monthly review links to monthly plan: `[[{YYYY-MM}-monthly-plan]]`
- Monthly review links to annual plan: `[[{YYYY}-annual-plan]]`

---

## 6. Overwrite Protection Rules

| Scenario | Rule |
|----------|------|
| Monthly plan file exists | Ask user before overwriting |
| Monthly review — record area (top section) | **NEVER overwrite** — only append records or preserve as-is |
| Monthly review — review sections (bottom section) | May overwrite when regenerating review |
| Creating next month's empty review | Do NOT overwrite if file already exists |
| `pulse record` — target file does not exist | Create from template, then append |

The record area boundary is defined by the `---` separator line that appears immediately before the line `## 以下内容由月末`. Everything above this line (inclusive) is the record area. Everything from that line onward is the review area.

---

## 7. Reference Files

| File | When Used | Purpose |
|------|-----------|---------|
| `ADVISOR.md` | All analysis and generation steps | Strategic advisor persona, tone, questioning framework |
| `CONFIG.md` | Configuration loading | Config schema and file matching rules |
| `templates/monthly-plan-template.md` | Creating monthly plan | Plan structure and placeholders |
| `templates/monthly-review-template.md` | Creating monthly review | Review structure with record area and review sections |
