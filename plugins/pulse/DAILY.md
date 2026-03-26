# Daily Dimension — Review & Planning Workflows

This document defines the complete workflows for `pulse daily`, `pulse daily-review`, and `pulse daily-plan`. It is loaded by the command router (SKILL.md) when any daily command is triggered.

---

## Command Dispatch

Determine the sub-command from the user's input:

| User Input | Sub-Command | Action |
|------------|-------------|--------|
| `pulse daily` / `日报` | combined | Execute daily-review, then daily-plan in a single session |
| `pulse daily-review` / `日回顾` | daily-review | Execute daily review only |
| `pulse daily-plan` / `日计划` | daily-plan | Execute daily plan only |

After dispatching, proceed to the corresponding workflow section below.

---

## Daily File Lifecycle

Each day has ONE file (`YYYY-MM-DD-daily.md`) with THREE sections managed by different actors:

```
Previous evening: pulse daily-plan
  -> Creates tomorrow's file from templates/daily-template.md
  -> Fills Part 3 (Daily Plan for tomorrow)

During the day: user manually records
  -> Appends to Part 1 (当日记录)

Current evening: pulse daily-review
  -> Reads Part 1 + Part 3 + external data sources + weekly plan
  -> Fills Part 2 (Daily Review)
  -> Then optionally chains into pulse daily-plan for tomorrow
```

### Section Markers in the Daily File

Use these markdown headings to locate each section:

| Part | Section Heading | Managed By |
|------|----------------|------------|
| Part 1 | `## 当日记录` | User (manual) |
| Part 2 | `## Daily Review` | `pulse daily-review` (AI-generated) |
| Part 3 | `## Daily Plan` | `pulse daily-plan` (AI-generated, from previous day) |

---

## Workflow: `pulse daily-review`

Execute the following steps in order.

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following the process defined in CONFIG.md ("How to Read Config at Runtime").
2. Extract `vault_path`, `pulse_dir`, `timezone`, and `language`.
3. Compute today's date in `YYYY-MM-DD` format using the configured timezone.
4. Compute the current ISO week number for weekly plan lookup.

### Step 2: Locate Today's Daily File

1. Construct the expected path: `{vault_path}/{pulse_dir}/10. Daily/{YYYY-MM-DD}-daily.md`
2. If the file exists, read it and parse Part 1 (当日记录) and Part 3 (Daily Plan).
3. If the file does NOT exist:
   - Inform the user: "今天的日志文件尚未创建。是否需要先运行 `pulse daily-plan` 来创建？"
   - If user confirms, switch to the daily-plan flow.
   - If user declines, create a minimal file from `templates/daily-template.md` with Part 1 only, then continue the review.

### Step 3: Scan Data Sources

1. Get `daily-review` source directories from `sources.daily-review.dirs` in the config.
2. For each directory, resolve the full path: `{vault_path}/{source_dir}`.
3. Recursively scan each resolved directory for `.md` files.
4. Apply the daily date matching rule (see CONFIG.md "Date Matching Rules"):
   - Extract `YYYY-MM-DD` from each filename using regex `\d{4}-\d{2}-\d{2}`.
   - Keep only files where the extracted date equals today's date.
5. Read the content of all matched files. These are the external data source inputs.

### Step 4: Load Weekly Plan Context

1. Determine the current week identifier: `{YYYY}-W{XX}` (ISO 8601 week numbering).
2. Look for the weekly plan file in `{vault_path}/{pulse_dir}/20. Weekly/`.
3. The weekly plan filename follows the pattern: `{YYYY}-W{XX}-weekly-plan.md`.
4. If found, read it. Extract:
   - Must Win goal
   - Work tasks list
   - Life goals for the week
5. If not found, note that no weekly plan exists for this week (proceed without it).

### Step 5: Present Collected Data to User

Display all gathered information to the user in a structured summary:

1. **Part 1 (当日记录)**: Show what the user recorded today.
2. **Part 3 (Daily Plan)**: Show what was planned for today (if any).
3. **External data sources**: List each matched file and summarize its content.
4. **Weekly plan context**: Show relevant weekly goals and Must Win.

Then ask:

> 以上是今天收集到的所有数据。请确认是否准确，并补充任何遗漏的内容：
> - 今天还有什么重要的事情没有被记录？
> - 有什么临时发生的事项需要纳入回顾？
> - 对生活各维度（健康、家庭、社交等）有补充吗？

Wait for user response. Incorporate any supplementary information.

### Step 5.5: Process Inline Directives

Follow the Inline Directive Processing rules defined in SKILL.md. Scan all files read in Steps 2-4 (today's daily file, external data source files, weekly plan file) for `{{{...}}}` directives. If any are found, present them to the user, execute upon confirmation, and remove the markers from the source files before proceeding.

### Step 6: Check Overwrite Protection (Part 2)

1. If Part 2 (`## Daily Review`) already contains generated content (not just template placeholders):
   - Ask user: "今天的 Daily Review 已经存在内容。是否覆盖？[Y/n]"
   - If user declines, abort the review generation.
   - If user confirms, proceed to overwrite.

### Step 7: Generate Daily Review Content

Using all collected data, generate the review following these guidelines:

**Apply ADVISOR.md principles throughout.** Do not duplicate ADVISOR.md content here; reference and follow its:
- Work/Life Parallel Analysis Guidelines (Step 1-4)
- Review Analysis Guidelines (Compare Plan vs. Actual, Identify Patterns, Root Causes, Project Forward)
- Feedback Style (Honest, Balanced, Actionable, Specific)

Generate content for each subsection of Part 2 as defined in `templates/daily-template.md`:

#### 7a: Data Source Summaries (数据源摘要)

For each external data source file matched in Step 3:
- List the file name and a 1-2 sentence summary of its content.
- If no external data sources were found, state: "今日无外部数据源记录。"

#### 7b: Work Review (工作回顾)

1. **Task completion table**: Compare each planned task from Part 3 (Daily Plan) against actual outcomes.
   - Status: ✅ (completed), ❌ (not done), ⚠️ (partially done / carried over)
   - Add notes explaining incomplete tasks.
2. **Key outputs** (关键产出): List the most significant work deliverables of the day.
3. **Blockers and issues** (阻塞与问题): List anything that blocked progress.

#### 7c: Life Records (生活记录)

Fill the 8 Life Wheel dimension table:

| Dimension Key | Chinese Name |
|--------------|-------------|
| Health | 健康 |
| Career/Studies | 事业/学习 |
| Wealth | 财务 |
| Family | 家庭 |
| Intimate Relationships | 亲密关系 |
| Social | 社交 |
| Personal Growth | 个人成长 |
| Leisure/Recovery | 休闲恢复 |

- Extract relevant records from Part 1 (当日记录), external data sources, and user supplements.
- For dimensions with no activity recorded, leave cells empty (do not fabricate content).

#### 7d: AI Analysis (AI 分析)

Generate three subsections following ADVISOR.md guidelines:

1. **Plan vs Actual (计划 vs 实际)**: Gap analysis comparing Part 3 plan to actual outcomes. Include completion rate percentage. Reference weekly plan alignment.
2. **What went well (做得好的)**: Specific, evidence-based recognition (per ADVISOR.md Feedback Style).
3. **What to improve (需改进的)**: Honest assessment with actionable structural suggestions (per ADVISOR.md: propose structural fixes, not willpower-dependent solutions).

### Step 8: Write Part 2 to Daily File

1. Read the current daily file content.
2. Locate the `## Daily Review` section (find the heading).
3. Replace everything between `## Daily Review` and the next `---` separator before `## Daily Plan` with the generated content.
4. Preserve Part 1 and Part 3 unchanged.
5. Write the updated file back to disk.
6. Confirm to user: "Daily Review 已写入 {file_path}"

### Step 9: Append Records to Monthly Review File

1. Determine the current month identifier: `{YYYY}-{MM}`.
2. Look for the monthly review file in `{vault_path}/{pulse_dir}/30. Monthly/`.
   - Filename pattern: files containing the `{YYYY}-{MM}` pattern and `monthly-review` in the name, e.g., `{YYYY}-{MM}-monthly-review.md`.
3. If the monthly review file exists:
   - For each Life Wheel dimension that has content in today's review (Step 7c):
     - Locate the corresponding dimension table under `## 日常记录` section.
     - The dimension tables are identified by their `### {dimension_name}` headings (健康, 事业/学习, 财务, 家庭, 亲密关系, 社交, 个人成长, 休闲).
     - Append a new row to the table: `| {YYYY-MM-DD} | {content} | {note} |`
     - For the 财务 dimension, the table has an extra column: `| {YYYY-MM-DD} | {content} | {amount} | {note} |`
   - Write the updated monthly review file.
   - Confirm to user: "已将今日记录追加到月度回顾文件。"
4. If the monthly review file does NOT exist:
   - Inform the user: "本月的月度回顾文件尚未创建。日常记录暂未追加，请先运行 `pulse monthly-plan` 创建月度文件。"

### Step 10: Offer to Continue with Daily Plan

If the sub-command was `daily-review` only (not combined):
- Ask user: "是否继续生成明天的计划？（`pulse daily-plan`）[Y/n]"
- If yes, proceed to the `pulse daily-plan` workflow below, passing the review context.

---

## Workflow: `pulse daily-plan`

Execute the following steps in order.

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following CONFIG.md ("How to Read Config at Runtime").
2. Extract `vault_path`, `pulse_dir`, `timezone`, and `language`.
3. Compute today's date and tomorrow's date in `YYYY-MM-DD` format using the configured timezone.
4. Compute the ISO week number for tomorrow (for weekly plan alignment).

### Step 2: Load Today's Review Context

1. If running as part of combined `pulse daily` flow, use the review data already in memory from the daily-review step. Skip to Step 3.
2. If running standalone (`pulse daily-plan`):
   - Read today's daily file: `{vault_path}/{pulse_dir}/10. Daily/{today_YYYY-MM-DD}-daily.md`
   - Parse Part 2 (Daily Review) if it exists — use it as context for tomorrow's planning.
   - If Part 2 is empty, check Part 1 (当日记录) for any context.
   - If today's file does not exist, proceed without today's context (plan based on weekly plan alone).

### Step 3: Scan Data Sources for Planning Context

1. Get `daily-plan` source directories from `sources.daily-plan.dirs` in the config.
2. Resolve full paths: `{vault_path}/{source_dir}`.
3. Recursively scan for `.md` files matching today's date (these are planning inputs, e.g., calendar exports, task lists).
4. Apply the daily date matching rule from CONFIG.md.
5. Read matched files as additional planning context.

### Step 4: Load Weekly Plan

1. Determine the ISO week number that tomorrow falls in.
2. Look for the weekly plan file: `{vault_path}/{pulse_dir}/20. Weekly/{YYYY}-W{XX}-weekly-plan.md`
3. If found, extract:
   - Must Win goal and its status
   - Remaining work tasks not yet completed
   - Life goals for the week
   - Time allocation budget
4. If not found, note the absence and proceed (plan based on available context only).

### Step 5: AI Generates Plan Suggestions

Using collected context, generate planning suggestions following ADVISOR.md guidelines:

**Apply ADVISOR.md principles throughout.** Reference its:
- Planning Guidelines (Maximum Commitments, Subtraction, Recovery, Upward Alignment, Challenge Over-Commitment)
- Work/Life Parallel Analysis Guidelines

Generate suggestions for each subsection of Part 3 as defined in `templates/daily-template.md`:

#### 5a: Work Tasks (工作任务)

1. Create a prioritized task list:
   - **P0**: Must-do tasks — directly tied to weekly Must Win or urgent deadlines
   - **P1**: Should-do tasks — important for weekly goals
   - **P2**: Nice-to-do tasks — beneficial but deferrable
2. For each task, specify:
   - Task description
   - Alignment to weekly goal (wikilink if applicable)
   - Estimated time
3. Follow ADVISOR.md Maximum Commitments: daily tasks should total 5-7 items across work and life.
4. If today's review shows incomplete tasks, carry them over with explicit notation.
5. Check upward alignment: every P0/P1 task should connect to a weekly plan goal. Flag unaligned tasks.

#### 5b: Life Arrangements (生活安排)

1. Plan activities across Life Wheel dimensions, focusing on:
   - **Health**: Exercise, meals, sleep schedule
   - **Personal Growth**: Learning, reading, reflection
   - **Other dimensions**: As relevant based on weekly life goals
2. Reference any patterns from today's review (e.g., if exercise was missed today, ensure it appears in tomorrow's plan).

#### 5c: Time Blocks (时间块)

1. Suggest a time block schedule:
   - **Morning (上午)**: High-focus work, P0 tasks
   - **Afternoon (下午)**: Collaborative work, P1 tasks, meetings
   - **Evening (晚上)**: Life activities, personal growth, recovery
2. Include buffer time between blocks (per ADVISOR.md: recovery reservation).
3. Ensure total planned hours are realistic (reference the user's typical day length from historical data if available).

### Step 6: Present Suggestions to User

Display the complete plan suggestion and ask for confirmation:

> 以下是明天（{tomorrow_date}）的计划建议。请确认或调整：
>
> [Display generated plan]
>
> 请告诉我：
> - 需要调整哪些任务的优先级？
> - 有什么已知的明天安排需要加入？（如会议、约会、截止日期）
> - 时间块安排是否符合你的作息习惯？

Wait for user response. Incorporate adjustments.

### Step 7: Check Overwrite Protection (Tomorrow's File)

1. Construct tomorrow's file path: `{vault_path}/{pulse_dir}/10. Daily/{tomorrow_YYYY-MM-DD}-daily.md`
2. If the file already exists:
   - Check if Part 3 (`## Daily Plan`) already has content.
   - If yes, ask: "明天的日志文件已存在且包含计划内容。是否覆盖 Daily Plan 部分？[Y/n]"
   - If user declines, abort plan writing.
   - If user confirms, proceed to overwrite Part 3 only (preserve Part 1 and Part 2).
3. If the file does NOT exist, proceed to create it in Step 8.

### Step 8: Write Tomorrow's Daily File

#### If creating a new file:

1. Read `templates/daily-template.md` from `{vault_path}/{pulse_dir}/` (the template is at the path where the pulse skill files reside: look under the `pulse/templates/` directory relative to the skill).
2. Replace template placeholders:

   | Placeholder | Value |
   |-------------|-------|
   | `{date}` | Tomorrow's date in `YYYY-MM-DD` format |
   | `{created_at}` | Current datetime in `YYYY-MM-DD HH:mm` format |
   | `{week_id}` | ISO week identifier for tomorrow: `{YYYY}-W{XX}` |
   | `{next_date}` | Tomorrow's date (same as `{date}` since this IS tomorrow's file) |

3. Fill Part 3 (Daily Plan) section with the confirmed plan content.
4. Leave Part 1 (当日记录) with default skeleton (single `-` bullet).
5. Leave Part 2 (Daily Review) with template placeholders.
6. Write the file to: `{vault_path}/{pulse_dir}/10. Daily/{tomorrow_YYYY-MM-DD}-daily.md`

#### If updating an existing file:

1. Read the existing file.
2. Locate the `## Daily Plan` section heading.
3. Replace everything from `## Daily Plan` to the final `---` before the footer with the new plan content.
4. Preserve Part 1 and Part 2 unchanged.
5. Write the updated file.

### Step 9: Confirm and Remind

1. Confirm to user: "明天的计划已写入 {file_path}"
2. Display a brief summary of tomorrow's top priorities (P0 tasks only).
3. Remind user about manual sync: "提醒：请将关键时间块同步到日历/滴答清单。"
4. Show a wikilink to the weekly plan for reference: `[[{YYYY}-W{XX}-weekly-plan]]`

---

## Workflow: `pulse daily` (Combined)

The combined flow executes both workflows in a single session with shared context.

### Execution Steps

1. **Run `pulse daily-review`** (Steps 1-9 above) for today.
2. **Pass review context forward**: The review results (task completion rates, identified patterns, life dimension status, AI analysis) are retained in memory.
3. **Run `pulse daily-plan`** (Steps 1-9 above) for tomorrow.
   - Skip Step 2 of daily-plan (loading today's review) since it is already in context.
   - In Step 5, the AI should explicitly reference today's review findings when generating tomorrow's plan:
     - Carry over incomplete tasks from today.
     - Address improvement areas identified in the review.
     - Maintain or adjust patterns based on what went well.
4. **End session**: Display a combined summary:

> **今日回顾完成** ✅
> - 工作完成率: {pct}%
> - 生活维度记录: {count}/8
>
> **明日计划已生成** ✅
> - P0 任务: {list}
> - 重点关注: {focus_area}
>
> 文件位置:
> - 今日回顾: `{today_file_path}`
> - 明日计划: `{tomorrow_file_path}`

---

## File Operations Reference

### Output Directory

All daily files are stored in: `{vault_path}/{pulse_dir}/10. Daily/`

### File Naming Convention

- Daily file: `{YYYY-MM-DD}-daily.md`
- Example: `2026-02-21-daily.md`

### Creating a New Daily File

1. Read `templates/daily-template.md`.
2. Replace all `{placeholder}` tokens with computed values (see placeholder table in Step 8 of daily-plan).
3. Write to: `{vault_path}/{pulse_dir}/10. Daily/{YYYY-MM-DD}-daily.md`

### Updating an Existing Daily File

1. Read the full file content.
2. Use section heading markers to locate the target section:
   - `## 当日记录` — Part 1 boundary start
   - `## Daily Review` — Part 2 boundary start
   - `## Daily Plan` — Part 3 boundary start
3. Each section ends at the `---` horizontal rule before the next section heading (or before the footer `*由 Pulse PDCA System 生成*`).
4. Replace the content between the section heading and its closing `---` with new content.
5. Preserve all other sections untouched.

### Appending to Monthly Review File

1. Locate the monthly review file: scan `{vault_path}/{pulse_dir}/30. Monthly/` for a file matching the current `{YYYY}-{MM}` and containing `monthly-review` in the filename.
2. The monthly review file has dimension tables under `## 日常记录`:

   | Dimension Heading | Table Columns |
   |-------------------|---------------|
   | `### 健康` | 日期, 内容, 备注 |
   | `### 事业/学习` | 日期, 内容, 备注 |
   | `### 财务` | 日期, 内容, 金额, 备注 |
   | `### 家庭` | 日期, 内容, 备注 |
   | `### 亲密关系` | 日期, 内容, 备注 |
   | `### 社交` | 日期, 内容, 备注 |
   | `### 个人成长` | 日期, 内容, 备注 |
   | `### 休闲` | 日期, 内容, 备注 |

3. For each dimension with recorded content, append a new table row after the last existing row in that dimension's table.
4. Do NOT overwrite existing rows; only append.

---

## Data Source Scanning

Follow the rules defined in CONFIG.md "Date Matching Rules". The key points for daily dimensions:

1. **Source directories**: Read from `sources.daily-review.dirs` or `sources.daily-plan.dirs` in config.
2. **Path resolution**: Each dir is relative to `vault_path`. Resolve to absolute: `{vault_path}/{dir}`.
3. **Recursive scan**: Include files in subdirectories.
4. **File filter**: Only `.md` files.
5. **Date matching**: Try TWO patterns in order:
   - Standard format: Extract `YYYY-MM-DD` from filename via regex `\d{4}-\d{2}-\d{2}`.
   - Chinese format: Extract date from filename via regex `(\d{4})年(\d{2})月(\d{2})日`, then normalize to `YYYY-MM-DD`.
   The extracted date (from either pattern) must exactly equal the target date.
6. **Multiple matches**: Collect all matching files as input.

---

## Overwrite Protection

### Part 2 (Daily Review) Protection

- **Trigger**: Running `pulse daily-review` when Part 2 already has content.
- **Detection**: Check if content between `## Daily Review` and the next section boundary contains more than template placeholders (i.e., check for actual generated text, tables with data, or AI analysis content).
- **Action**: Prompt user for confirmation before overwriting.

### Part 3 (Daily Plan) Protection

- **Trigger**: Running `pulse daily-plan` when tomorrow's file already has content in Part 3.
- **Detection**: Check if content between `## Daily Plan` and the file footer contains more than template placeholders.
- **Action**: Prompt user for confirmation before overwriting.

### Part 1 (当日记录) Protection

- Part 1 is NEVER overwritten by any automated process.
- It is always preserved during both daily-review and daily-plan operations.

---

## Cross-References

| Reference | File | Purpose |
|-----------|------|---------|
| Daily template | `templates/daily-template.md` | Template for new daily files; defines section structure and placeholders |
| Weekly plan | `{vault_path}/{pulse_dir}/20. Weekly/{YYYY}-W{XX}-weekly-plan.md` | Alignment context for daily tasks; Must Win reference |
| Monthly review | `{vault_path}/{pulse_dir}/30. Monthly/*-monthly-review.md` | Target for appending daily life dimension records |
| Config reading | CONFIG.md | Config file loading, path resolution, date matching rules |
| Advisor persona | ADVISOR.md | Review analysis guidelines, planning guidelines, feedback style, Work/Life parallel analysis |
| Weekly plan link | `[[{YYYY}-W{XX}-weekly-plan]]` | Wikilink embedded in daily file header for Obsidian navigation |
