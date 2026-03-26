# Weekly Dimension — Review & Plan

This document defines the complete workflow for `pulse weekly`, `pulse weekly-review`, and `pulse weekly-plan`. It is loaded only when one of these commands is triggered (see SKILL.md routing table).

---

## 1. Command Dispatch

Determine which sub-command is being invoked:

| User Command | Action |
|-------------|--------|
| `pulse weekly` | Execute **weekly-review** first, then **weekly-plan** in a single session (combined flow) |
| `pulse weekly-review` | Execute weekly review only |
| `pulse weekly-plan` | Execute weekly plan only |

Chinese aliases: `周回顾` maps to `weekly-review`, `周计划` maps to `weekly-plan`.

---

## 2. Week Calculation Rules

All week calculations follow **ISO 8601** and use the timezone from `.pulse-config.yaml` (default: `Asia/Shanghai`).

### Definitions

- **Week boundary**: Monday 00:00 to Sunday 23:59 (ISO 8601).
- **ISO week numbering**: W01 through W53. Week 1 is the week containing the first Thursday of the year.
- **Week ID format**: `YYYY-WXX` (e.g., `2026-W08`). The `YYYY` is the ISO week-year (which may differ from the calendar year near Jan 1).
- **"This week"**: The ISO week containing today's date.
- **"Last week"**: The ISO week immediately preceding this week.
- **"Next week"**: The ISO week immediately following this week.

### Date Range Calculation

```
Given a target ISO week (year, week_number):
  week_start = Monday of that ISO week (YYYY-MM-DD)
  week_end   = Sunday of that ISO week (YYYY-MM-DD)
```

### Typical Timing

- The user typically runs `pulse weekly` on **Sunday evening** to review the current week and plan the next week in one session.
- When running `pulse weekly-review`, the target week is **this week** (the week containing today).
- When running `pulse weekly-plan`, the target week is **next week** (the week after the week containing today).
- When running `pulse weekly` (combined), the review covers **this week** and the plan covers **next week**.

---

## 3. `pulse weekly-review` Flow

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following the process in CONFIG.md section "How to Read Config at Runtime".
2. Extract `vault_path`, `pulse_dir`, `timezone`, `language`, and `sources.weekly-review.dirs`.

### Step 2: Determine Target Week

1. Calculate the current date in the configured timezone.
2. Determine the ISO week number and year for the current date.
3. Compute `week_start` (Monday) and `week_end` (Sunday) for this week.
4. Construct the week ID: `YYYY-WXX`.

### Step 3: Check for Existing Review

1. Check if `{vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-review.md` already exists.
2. If it exists:
   - Display a summary of the existing file content to the user.
   - Ask: "本周的周回顾已存在。是否要覆盖？[y/N]"
   - If the user declines, stop execution.

### Step 4: Scan External Data Sources

1. Resolve all directories in `sources.weekly-review.dirs` relative to `vault_path`.
2. Recursively scan each directory for `.md` files.
3. Match filenames using the weekly date matching rule from CONFIG.md:
   - Extract `YYYY-MM-DD` from each filename using regex `\d{4}-\d{2}-\d{2}`.
   - Include the file if the extracted date falls within `week_start` to `week_end` (inclusive).
4. Read the content of all matched files.

### Step 5: Read Daily Files for This Week

1. Scan `{vault_path}/{pulse_dir}/10. Daily/` for files matching the pattern `YYYY-MM-DD-daily.md` where the date falls within Monday to Sunday of this week.
2. For each daily file found, extract:
   - **Part 1 (当日记录)**: Any manual entries the user recorded.
   - **Part 2 (Daily Review)**: Work task completion status, life dimension records, AI analysis.
   - **Part 3 (Daily Plan)**: Planned tasks and time blocks (for plan-vs-actual comparison).
3. Aggregate all daily data into a structured summary:
   - Total work tasks planned vs. completed across the week.
   - Life dimension activities aggregated by dimension.
   - Time block data for time allocation analysis.

### Step 6: Read Weekly Plan (If Exists)

1. Check for `{vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-plan.md`.
2. If it exists, read it to enable plan-vs-actual comparison:
   - Extract the Must Win goal and verification criteria.
   - Extract planned work tasks and their target dates.
   - Extract planned life goals by dimension.
   - Extract planned time allocation budget.
   - Extract improvement items from previous week.

### Step 7: Read Monthly Plan (If Exists)

1. Determine the current month from the target week's date range.
2. Construct the month ID: `YYYY-MM` (use the month that contains the majority of the target week's days; if the week spans two months, use the month containing Thursday of that week per ISO 8601 convention).
3. Check for `{vault_path}/{pulse_dir}/30. Monthly/{month_id}-monthly-plan.md`.
4. If it exists, read it for upward alignment analysis.

### Step 8: Present Data and Confirm

Present the aggregated data to the user in a structured summary:

```
--- 周回顾数据汇总 ({week_id}: {week_start} ~ {week_end}) ---

已找到的 Daily 文件: {count} / 7
外部数据源文件: {count}

工作任务汇总:
  计划: {planned_count} 项
  完成: {completed_count} 项

周计划: {found / not found}
月度计划: {found / not found}

是否有需要补充的信息？[输入补充内容，或按 Enter 继续]
```

Allow the user to add supplementary information (e.g., tasks not captured in dailies, context for missed items).

### Step 8.5: Process Inline Directives

Follow the Inline Directive Processing rules defined in SKILL.md. Scan all files read in Steps 4-7 (external data source files, daily files, weekly plan, monthly plan) for `{{{...}}}` directives. If any are found, present them to the user, execute upon confirmation, and remove the markers from the source files before proceeding.

### Step 9: Generate Weekly Review

Using ADVISOR.md guidelines, generate a comprehensive weekly review covering these sections (following `templates/weekly-review-template.md`):

1. **Data Source Summary** (`{aggregated_data}`):
   - List of daily files read and external source files.
   - Brief summary of data completeness.

2. **Work Review — Must Win Status**:
   - Compare the weekly plan's Must Win goal against actual outcomes.
   - Status: achieved (completed with evidence) / partially achieved (progress made, not fully met) / missed (not achieved).
   - Provide specific evidence from daily files.
   - Gap analysis if not fully achieved.

3. **Work Review — Task Completion Table**:
   - List all planned tasks from the weekly plan.
   - Mark each as completed / partially completed / not started.
   - Add any unplanned tasks that were completed.
   - Calculate overall completion rate: `{completed}/{total} = {pct}%`.
   - Identify key outcomes and achievements.
   - Identify blockers and problems.

4. **Life Review — 8 Dimension Weekly Summary**:
   - Aggregate daily life dimension records into a weekly summary.
   - For each of the 8 Life Wheel dimensions (Health, Career/Studies, Wealth, Family, Intimate Relationships, Social, Personal Growth, Leisure/Recovery):
     - Summarize execution status across the week.
     - Highlight notable activities, achievements, or issues.

5. **Time Allocation Analysis**:
   - Compare planned hours (from weekly plan time budget) vs. actual hours (aggregated from daily time blocks).
   - Calculate deviation for each category (work, study, health, rest, other).
   - Analyze significant deviations.

6. **AI Analysis — Pattern Recognition**:
   - Identify recurring patterns across the week (both positive and negative).
   - Cross-reference with previous weeks if historical data is available.
   - Look for: repeated successes, repeated failures, energy patterns, productivity patterns.
   - Apply ADVISOR.md rules: challenge assumptions, dig for root causes, project forward.

7. **AI Analysis — Improvement Suggestions**:
   - Provide 2-3 actionable improvement suggestions for next week.
   - Each suggestion must be **structural, not willpower-based** (per ADVISOR.md guidelines).
   - Format: what to change + why + how to implement it.

### Step 10: Save Weekly Review

1. Fill the template `templates/weekly-review-template.md` with all generated content.
2. Replace all placeholders:

   | Placeholder | Value |
   |------------|-------|
   | `{year}` | ISO week-year |
   | `{week_number}` | ISO week number (zero-padded, e.g., `08`) |
   | `{week_start}` | Monday date `YYYY-MM-DD` |
   | `{week_end}` | Sunday date `YYYY-MM-DD` |
   | `{created_at}` | Current timestamp in configured timezone |
   | `{week_id}` | `YYYY-WXX` |
   | `{month_id}` | `YYYY-MM` |
   | `{aggregated_data}` | Generated data summary |
   | All other placeholders | Corresponding generated content |

3. Write the file using Bash heredoc method:
   ```bash
   cat << 'WEEKLY_REVIEW_EOF' > "{vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-review.md"
   {filled_template_content}
   WEEKLY_REVIEW_EOF
   ```

4. Confirm to the user:
   ```
   周回顾已保存: {vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-review.md
   ```

---

## 4. `pulse weekly-plan` Flow

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following the process in CONFIG.md section "How to Read Config at Runtime".
2. Extract `vault_path`, `pulse_dir`, `timezone`, `language`, and `sources.weekly-plan.dirs`.

### Step 2: Determine Target Week

1. Calculate the current date in the configured timezone.
2. Determine **next week's** ISO week number and year.
3. Compute `week_start` (Monday) and `week_end` (Sunday) for next week.
4. Construct the week ID: `YYYY-WXX` for next week.

**Note**: When running as part of `pulse weekly` (combined flow), this step uses the week after the review target week.

### Step 3: Check for Existing Plan

1. Check if `{vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-plan.md` already exists.
2. If it exists:
   - Display a summary of the existing file content to the user.
   - Ask: "下周的周计划已存在。是否要覆盖？[y/N]"
   - If the user declines, stop execution.

### Step 4: Read This Week's Review

1. Determine **this week's** week ID.
2. Check for `{vault_path}/{pulse_dir}/20. Weekly/{this_week_id}-weekly-review.md`.
3. If it exists (it should, especially in combined flow), read it for:
   - Must Win achievement status.
   - Task completion rate and unfinished tasks.
   - Improvement suggestions to carry into next week's plan.
   - Life dimension status and gaps.
   - Time allocation deviations.

### Step 5: Read Monthly Plan

1. Determine the month that contains the majority of the target (next) week's days.
2. Check for `{vault_path}/{pulse_dir}/30. Monthly/{month_id}-monthly-plan.md`.
3. If it exists, read it for:
   - Monthly OKRs / result commitments for alignment.
   - Monthly life dimension goals.
   - Monthly time allocation strategy.

### Step 6: Scan External Data Sources

1. Resolve all directories in `sources.weekly-plan.dirs` relative to `vault_path`.
2. Scan for relevant planning materials (e.g., upcoming deadlines, scheduled events).
3. Read matched files to enrich planning context.

### Step 7: AI Generates Plan Suggestion

Using ADVISOR.md guidelines, generate a weekly plan suggestion covering these sections (following `templates/weekly-plan-template.md`):

1. **Must Win**:
   - Propose ONE non-negotiable deliverable for next week.
   - Must align with a current monthly goal.
   - Must have clear, verifiable acceptance criteria.
   - Apply ADVISOR.md rules: challenge over-commitment, verify upward alignment.

2. **Work Tasks**:
   - Priority task table with columns: Task, Monthly Alignment, Target Date, Priority (P0/P1/P2).
   - P0: Must Win related tasks (1-2 tasks).
   - P1: Important supporting tasks (2-3 tasks).
   - P2: Nice-to-have tasks (0-2 tasks).
   - Total should respect ADVISOR.md maximum commitment guidelines for weekly level.
   - Carry forward any unfinished P0/P1 tasks from this week's review (flag them as carried over).

3. **Life Goals**:
   - Goals for each relevant Life Wheel dimension with specific arrangements.
   - Must include at least: Health, Personal Growth, and one relationship dimension (Family/Social/Intimate).
   - Must include Leisure/Recovery (non-negotiable per ADVISOR.md recovery reservation rule).
   - Arrangements should be specific (day, time, activity) not vague.

4. **Time Allocation Budget**:
   - Hours per category for the week: Work, Study, Health, Rest/Recovery, Other.
   - Total must not exceed realistic available hours (factor sleep, commute, meals).
   - If this week's review showed significant time deviation, adjust budget and explain why.

5. **Previous Week Improvements**:
   - Take the 2-3 improvement suggestions from this week's review.
   - For each, define a concrete action to implement next week.
   - These are structural changes, not "try harder" commitments.

### Step 8: Present Plan and Confirm

Present the AI-generated plan suggestion to the user:

```
--- 下周计划建议 ({week_id}: {week_start} ~ {week_end}) ---

{generated_plan_content}

---
请确认或修改以上计划:
1. 确认并保存 [Enter]
2. 修改某项内容 [输入修改说明]
3. 取消 [输入 "cancel"]
```

Allow the user to review and adjust:
- If the user provides modifications, regenerate the affected sections.
- Iterate until the user confirms.
- Apply ADVISOR.md Rule 5 (Structured Decision Framework) if disagreements arise.

### Step 9: Save Weekly Plan

1. Fill the template `templates/weekly-plan-template.md` with confirmed content.
2. Replace all placeholders:

   | Placeholder | Value |
   |------------|-------|
   | `{year}` | ISO week-year for next week |
   | `{week_number}` | ISO week number for next week (zero-padded) |
   | `{week_start}` | Next Monday `YYYY-MM-DD` |
   | `{week_end}` | Next Sunday `YYYY-MM-DD` |
   | `{created_at}` | Current timestamp in configured timezone |
   | `{month_id}` | `YYYY-MM` of the month containing most of next week |
   | `{must_win_goal}` | Confirmed Must Win goal |
   | `{monthly_alignment}` | Which monthly goal the Must Win aligns with |
   | `{verification}` | Acceptance criteria for the Must Win |
   | All task rows | Confirmed work tasks |
   | All life goal rows | Confirmed life goals |
   | All time budget rows | Confirmed time allocation |
   | All improvement rows | Confirmed improvement actions |

3. Write the file using Bash heredoc method:
   ```bash
   cat << 'WEEKLY_PLAN_EOF' > "{vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-plan.md"
   {filled_template_content}
   WEEKLY_PLAN_EOF
   ```

4. Confirm to the user:
   ```
   周计划已保存: {vault_path}/{pulse_dir}/20. Weekly/{week_id}-weekly-plan.md
   ```

---

## 5. `pulse weekly` Combined Flow

When the user runs `pulse weekly`, execute both review and plan in a single session with shared context.

### Execution Order

1. **Run weekly-review** (Sections 3.1 through 3.10 above).
2. **Share context**: The review findings — especially Must Win status, completion rate, improvement suggestions, time deviations, and life dimension gaps — are directly available to inform the plan. Do NOT re-read files; use the in-memory review data.
3. **Run weekly-plan** (Sections 4.1 through 4.9 above), skipping Step 4 (Read This Week's Review) since the review data is already in context.

### Session Continuity

- The review and plan are generated in the same conversation session.
- The AI should explicitly reference review findings when making plan suggestions. For example:
  - "This week's Must Win was achieved; I recommend escalating the goal for next week."
  - "Exercise was completed only 2/7 days this week. Next week's plan includes a fixed morning slot to address this structural issue."
  - "Work consumed 15 hours more than budgeted. Next week's budget is adjusted to reflect actual capacity."

---

## 6. File Operations Reference

### Output Directory

```
{vault_path}/{pulse_dir}/20. Weekly/
```

### File Naming Convention

| Type | Filename Pattern | Example |
|------|-----------------|---------|
| Weekly Plan | `YYYY-WXX-weekly-plan.md` | `2026-W09-weekly-plan.md` |
| Weekly Review | `YYYY-WXX-weekly-review.md` | `2026-W08-weekly-review.md` |

### Week ID Calculation for Next Week

When generating a plan for next week:
1. Take today's date in the configured timezone.
2. Add 7 days to get a date in next week.
3. Calculate the ISO week number and ISO week-year of that date.
4. Format as `YYYY-WXX`.

### File Generation Method

Use Bash heredoc for file creation (consistent with other dimensions):

```bash
cat << 'EOF' > "/path/to/20. Weekly/YYYY-WXX-weekly-review.md"
{template_content_with_placeholders_filled}
EOF
```

Always quote the file path to handle spaces in directory names (e.g., `"20. Weekly"`).

---

## 7. Data Aggregation from Dailies

When building the weekly review, aggregate data from daily files as follows:

### Source Files

- Directory: `{vault_path}/{pulse_dir}/10. Daily/`
- Filename pattern: `YYYY-MM-DD-daily.md` where `YYYY-MM-DD` falls within the target week (Monday through Sunday).
- Expected: up to 7 files (one per day).

### Extraction per Daily File

From each daily file, extract the following sections:

| Section | What to Extract |
|---------|----------------|
| **当日记录** (Part 1) | Manual entries, ad-hoc tasks, notes |
| **工作回顾** (Daily Review) | Planned tasks with completion status (table rows) |
| **关键产出** | Key outputs for the day |
| **阻塞与问题** | Blockers and issues |
| **生活记录** (Life records) | 8-dimension table with content and notes |
| **AI 分析** | Plan vs. actual gap analysis, positives, improvements |
| **时间块** (Time blocks) | Morning / afternoon / evening plans and what actually happened |

### Aggregation Logic

1. **Work tasks**: Combine all daily planned tasks into one table. Count unique tasks (deduplicate across days if the same task appears). Calculate: total planned, completed, partially done, not started.

2. **Life dimensions**: For each of the 8 dimensions, collect all daily entries across the week. Summarize activity frequency and notable events.

3. **Time allocation**: Sum time block data from dailies by category (work, study, health, rest, other). Compare against weekly plan time budget if available.

4. **Key outputs**: Collect all key outputs across the week into a consolidated list.

5. **Blockers**: Collect all blockers. Identify recurring blockers (same blocker appearing 2+ days).

6. **Missing days**: Note which days have no daily file (gap in data). Factor this into completion rate calculations.

---

## 8. File Overwrite Protection

Before writing any weekly file (review or plan), check for existing files:

1. Construct the expected file path.
2. If the file exists:
   a. Read the file and display a brief summary (first few key lines: title, Must Win, completion rate if review, or Must Win goal if plan).
   b. Ask the user: "该文件已存在。是否要覆盖？[y/N]"
   c. Default is **No** (do not overwrite).
   d. If user confirms overwrite, proceed with generation.
   e. If user declines, stop that sub-command. (In combined flow, declining review does not prevent plan from running.)

---

## 9. Cross-References

### Obsidian Wikilinks in Generated Files

- Weekly plan links to monthly plan: `[[YYYY-MM-monthly-plan]]`
- Weekly review links to weekly plan: `[[YYYY-WXX-weekly-plan]]`
- Weekly review links to monthly plan: `[[YYYY-MM-monthly-plan]]`

### Internal Document References

| Document | When Referenced | Purpose |
|----------|---------------|---------|
| `CONFIG.md` | Steps 1-2 of all flows | Config loading, date matching rules, path resolution |
| `ADVISOR.md` | Steps 9 (review) and 7 (plan) | Analysis tone, questioning framework, commitment limits, planning guidelines |
| `templates/weekly-review-template.md` | Step 10 (review save) | Template for weekly review output |
| `templates/weekly-plan-template.md` | Step 9 (plan save) | Template for weekly plan output |

### Upward and Downward Alignment

```
Monthly Plan (30. Monthly/)
    |
    +-- Weekly Plan (20. Weekly/)    <-- must align upward
    |       |
    |       +-- Daily Plan (10. Daily/)
    |
    +-- Weekly Review (20. Weekly/)  <-- references weekly plan + monthly plan
```

---

## 10. Language and Content Generation

- Read the `language` field from `.pulse-config.yaml`.
- Generate all review and plan **content** in the configured language.
- `zh-CN`: Generate content in Chinese (default).
- `en-US`: Generate content in English.
- Template structure (section headers, table headers) is already in the template file and should be preserved as-is.
- Placeholders are filled with language-appropriate content.

---

## 11. Error Handling

| Scenario | Action |
|----------|--------|
| No daily files found for the week | Warn the user: "本周未找到任何 Daily 文件。周回顾将基于有限数据生成。" Proceed with available external sources. |
| No weekly plan exists for review | Warn: "未找到本周的周计划。回顾将无法进行计划对比分析。" Skip plan-vs-actual comparison in review. |
| No monthly plan exists | Warn: "未找到当月的月度计划。无法进行月度对齐分析。" Skip alignment analysis. |
| Config file missing or invalid | Display error per SKILL.md first-run check. Do not proceed. |
| Output directory does not exist | Create `20. Weekly/` directory before writing. |
| External source directory does not exist | Warn but continue: "数据源目录不存在: {dir}，已跳过。" |

---

*This document is read by the AI agent at runtime. It references but does not duplicate CONFIG.md (config schema, date matching), ADVISOR.md (persona, analysis guidelines), and templates/ (output format).*
