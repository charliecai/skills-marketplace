---
name: pulse
description: |
  Unified Year-Month-Week-Day PDCA life management system with work and life domains.
  Integrates goal management, self-reflection, and continuous improvement in Obsidian vault.
  Use for: daily planning, daily review, weekly planning, weekly review, monthly planning,
  monthly review, annual planning, annual review, quick records, PDCA, life wheel assessment.
  Supports inline directives in files using {{{directive}}} syntax — detected and executed during reviews.
  Triggers: pulse daily, pulse weekly, pulse monthly, pulse annual, pulse record, pulse init,
  pulse daily-review, pulse daily-plan, pulse weekly-review, pulse weekly-plan,
  pulse monthly-review, pulse monthly-plan, pulse annual-review, pulse annual-plan,
  pulse status, 日计划, 周计划, 月计划, 年度计划, 日回顾, 周回顾, 月度回顾, 年度回顾, 日报, 年度, 记录, PDCA
---

# Pulse — PDCA Life Management System

Pulse applies the PDCA (Plan-Do-Check-Act) cycle across four time dimensions — Year, Month, Week, Day — to drive continuous improvement in both work and life. Life is measured across the 8 Life Wheel dimensions: Health, Career, Wealth, Family, Intimate Relationships, Social, Personal Growth, and Leisure. Act as an independent strategic advisor throughout all interactions (see ADVISOR.md for persona details, tone, and questioning framework).

## First-Run Check

On ANY pulse command, before executing:

1. Read `.pulse-config.yaml` from `{vault_path}/{pulse_dir}/`.
2. If the file does NOT exist, display the following message and STOP immediately:

> ⚠️ Pulse 尚未初始化。请运行 `pulse init` 来完成初始化配置。

3. If the file exists, load it and proceed to command routing.

## Command Routing

Route the user's command to the corresponding dimension file:

| Command | Action |
|---------|--------|
| `pulse init` | Read CONFIG.md, follow init flow |
| `pulse daily` | Read DAILY.md, execute combined daily review + plan |
| `pulse daily-review` | Read DAILY.md, execute daily review only |
| `pulse daily-plan` | Read DAILY.md, execute daily plan only |
| `pulse weekly` | Read WEEKLY.md, execute combined weekly review + plan |
| `pulse weekly-review` | Read WEEKLY.md, execute weekly review only |
| `pulse weekly-plan` | Read WEEKLY.md, execute weekly plan only |
| `pulse monthly` | Read MONTHLY.md, execute combined monthly review + plan |
| `pulse monthly-review` | Read MONTHLY.md, execute monthly review only |
| `pulse monthly-plan` | Read MONTHLY.md, execute monthly plan only |
| `pulse record` | Read MONTHLY.md, execute quick record flow |
| `pulse annual` | Read ANNUAL.md, execute guided annual review + plan |
| `pulse annual-review` | Read ANNUAL.md, execute annual review only |
| `pulse annual-plan` | Read ANNUAL.md, execute annual plan only |
| `pulse status` | Read latest files, display dashboard (see below) |

For Chinese triggers, map to the equivalent command: 日计划→daily-plan, 日回顾→daily-review, 日报→daily, 周计划→weekly-plan, 周回顾→weekly-review, 月计划→monthly-plan, 月度回顾→monthly-review, 年度计划→annual-plan, 年度回顾→annual-review, 年度→annual, 记录→record.

## Work/Life Structure

Every routine processes in this order:

1. **Work section** — professional goals, projects, tasks
2. **Life section** — 8 Life Wheel dimensions, each tracked independently
3. **Integrated analysis** — cross-domain insights, conflicts, synergies

Work and life are parallel but separate tracks. Never merge them into a single list.

## Inline Directive Processing

The user may embed inline directives in any Pulse file (daily notes, weekly plans, monthly files, etc.) using the triple-brace syntax:

```
{{{directive content}}}
```

Where `directive content` is a natural language instruction for the AI to execute (e.g., `{{{把这周的读书笔记整理到个人成长维度}}}`, `{{{remind me to schedule dentist appointment next week}}}`).

### When to Process

Inline directive processing applies to **all review flows** (daily-review, weekly-review, monthly-review, annual-review). Each review flow includes a dedicated directive processing step after data collection and before review generation. See the specific dimension files (DAILY.md, WEEKLY.md, MONTHLY.md, ANNUAL.md) for the exact step placement.

### Processing Rules

1. **Scan**: While reading files during the data collection phase of any review flow, detect all `{{{...}}}` patterns using regex `\{\{\{(.+?)\}\}\}` (with DOTALL flag for multi-line directives).
2. **Collect**: Build a directive list with: source file path, line location, and directive content.
3. **Present**: Show all found directives to the user:
   ```
   发现 {N} 条内联指令：
   1. [{source_file}] {directive_content_preview}
   2. [{source_file}] {directive_content_preview}
   ...
   是否执行这些指令？[Y/n]
   ```
4. **Execute**: Upon user confirmation, execute each directive in order. Directives are natural language instructions — interpret and act on them using available context and tools.
5. **Clean up**: After each directive is successfully executed, remove the entire `{{{directive content}}}` marker (including the triple braces) from the original source file. Preserve surrounding content unchanged.
6. **Report**: Confirm execution results to the user before proceeding with review generation.

### Edge Cases

- If a directive cannot be executed (ambiguous, requires missing data, etc.), ask the user for clarification before proceeding.
- If no directives are found in any scanned file, skip this step silently and proceed with review generation.
- Directives inside code blocks (fenced with ``` or indented 4+ spaces) should be ignored — they are documentation, not instructions.

## Status Dashboard (`pulse status`)

Read the most recent files:
- Latest daily note (today or most recent)
- Current weekly plan
- Current monthly plan
- Current annual plan

Display a concise dashboard:
- **Annual Goals**: Key objectives for the year
- **Monthly Focus**: This month's priorities and progress
- **Weekly Focus**: This week's key tasks and commitments
- **Today's Priorities**: Today's top items and schedule
- **Life Wheel Snapshot**: Brief status of each dimension

## File References

Load these files ONLY when the corresponding command is triggered:

| File | When Loaded | Purpose |
|------|-------------|---------|
| `CONFIG.md` | `pulse init` | Initialization flow, vault setup, config schema |
| `DAILY.md` | `pulse daily*` | Daily review and planning workflows |
| `WEEKLY.md` | `pulse weekly*` | Weekly review and planning workflows |
| `MONTHLY.md` | `pulse monthly*`, `pulse record` | Monthly review, planning, and quick record workflows |
| `ANNUAL.md` | `pulse annual*` | Annual review and planning workflows |
| `ADVISOR.md` | All commands (after config check) | Strategic advisor persona, tone, questioning style |
| `templates/*` | When creating new notes | Obsidian-compatible markdown templates for each note type |
| `utils/calendar_integration.py` | When calendar sync is needed (optional) | Calendar event reading and schedule integration; if not present, generate ICS content directly |
