# Annual Dimension — Review & Planning Workflows

This document defines the complete workflows for `pulse annual`, `pulse annual-review`, and `pulse annual-plan`. It is loaded by the command router (SKILL.md) when any annual command is triggered. This is the most comprehensive dimension in the Pulse system, covering full-year strategic planning and deep retrospective review.

---

## Command Dispatch

Determine the sub-command from the user's input:

| User Input | Sub-Command | Action |
|------------|-------------|--------|
| `pulse annual` / `年度` | guided choice | Present options, then execute the chosen workflow |
| `pulse annual-review` / `年度回顾` | annual-review | Execute annual review only |
| `pulse annual-plan` / `年度计划` | annual-plan | Execute annual plan only |

### Guided Choice (`pulse annual`)

When the user runs `pulse annual` without specifying review or plan:

1. Present the options:
   > Would you like to do an **annual review** or **annual plan**?
   > 1. Annual Review — reflect on the past year
   > 2. Annual Plan — set strategy for the coming year
2. Wait for user response.
3. Route to the corresponding workflow below.

---

## Time Period Calculation Rules

### For Annual Review

| Current Date Range | Default Review Year | Rationale |
|--------------------|-------------------|-----------|
| Jan 1 - Feb 28/29 | Previous year | Still close enough to review the year that just ended |
| Mar 1 - Dec 31 | Current year | Mid-year or late-year partial review |

After determining the default:
1. Confirm with user: "I suggest reviewing **{year}**. Is this correct?"
2. If user disagrees, accept their specified year.

### For Annual Planning

| Current Date Range | Default Plan Year | Rationale |
|--------------------|-----------------|-----------|
| Jan 1 - Feb 28/29 | Current year | Year has just started; plan for now |
| Mar 1 - Dec 31 | Next year | Current year is well underway; plan ahead |

After determining the default:
1. Confirm with user: "I suggest planning for **{year}**. Is this correct?"
2. If user disagrees, accept their specified year.

---

## Workflow Mode Selection

Two modes are available for all annual workflows:

### Standard Mode (Default)

- Step-by-step interactive process.
- Wait for user response after each phase or section.
- Provide detailed analysis and questions at each step.
- Recommended for first-time users or thorough sessions.

### Quick Mode

- Activated when user says: "use quick mode", "skip questions", "quick", or similar.
- User provides all information upfront or in large batches.
- Minimal confirmations — proceed unless user objects.
- Generate the full document in one pass after collecting essential inputs.
- Still apply ADVISOR.md principles in analysis, but compress interaction rounds.

---

## Workflow: `pulse annual-review`

Execute the following steps in order.

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following the process defined in CONFIG.md ("How to Read Config at Runtime").
2. Extract `vault_path`, `pulse_dir`, `timezone`, and `language`.
3. Compute the current date using the configured timezone.

### Step 2: Determine Review Year

1. Apply Time Period Calculation Rules (see above) to determine the default review year.
2. Confirm with user.
3. Store the confirmed year as `{review_year}`.

### Step 3: Check File Overwrite Protection

1. Construct the output path: `{vault_path}/{pulse_dir}/40. Annual/{review_year}-annual-review.md`
2. If the file already exists:
   - Read it and display a brief summary (year, three summary words if present, Life Wheel scores if present).
   - Ask user: "An annual review for {review_year} already exists. Overwrite? [Y/n]"
   - If user declines, abort.
   - If user confirms, proceed.

### Step 4: Check for Annual Plan (Determines Workflow Branch)

1. Check if the annual plan for `{review_year}` exists: `{vault_path}/{pulse_dir}/40. Annual/{review_year}-annual-plan.md`
2. If the plan file **exists** -> proceed with **Workflow A** (Plan-Referenced Review).
3. If the plan file **does NOT exist** -> proceed with **Workflow B** (Life Wheel Structured Review).

### Step 5: Gather Source Data

Regardless of workflow branch, collect all available data:

1. **Monthly reviews**: Scan `{vault_path}/{pulse_dir}/30. Monthly/` for files matching `{review_year}-*-monthly-review.md`. Read all found files.
2. **Monthly plans**: Scan `{vault_path}/{pulse_dir}/30. Monthly/` for files matching `{review_year}-*-monthly-plan.md`. Read all found files.
3. **External data sources**: Get `annual-review` source directories from `sources.annual-review.dirs` in config. Scan for `.md` files matching `{review_year}` per CONFIG.md date matching rules.
4. Present a summary of collected data to the user:
   > Found: {N} monthly reviews, {M} monthly plans, {K} external source files for {review_year}.
   > Any additional information or documents you'd like me to consider?
5. Wait for user to provide supplementary context (optional).

### Step 5.5: Process Inline Directives

Follow the Inline Directive Processing rules defined in SKILL.md. Scan all files read in Step 5 (monthly reviews, monthly plans, external data source files) for `{{{...}}}` directives. If any are found, present them to the user, execute upon confirmation, and remove the markers from the source files before proceeding.

---

### Workflow A: Plan-Referenced Annual Review

Use this workflow when the annual plan for `{review_year}` exists. The review is structured around evaluating plan execution.

#### A1: Read and Parse Annual Plan

1. Read `{vault_path}/{pulse_dir}/40. Annual/{review_year}-annual-plan.md`.
2. Extract:
   - Annual theme word
   - Battlefields and strategic positioning
   - Objectives and Key Results (OKRs)
   - Key commitments and success criteria
   - Routine schedules
   - Subtraction list
   - 12-week rhythm milestones

#### A2: Guide Plan-Referenced Review

Walk through the review by referencing specific goals and battlefields from the plan. For each Objective:
- Ask about achievement of each Key Result with measurable evidence.
- Compare actual outcomes vs planned targets.
- Identify gaps between plan and reality.
- Ask: "What structural factors contributed to success or failure?"

**Apply ADVISOR.md principles throughout.** Follow its Review Analysis Guidelines: Compare Plan vs. Actual, Identify Patterns, Root Causes, Project Forward. Use evidence-based, honest feedback per ADVISOR.md Feedback Style.

#### A3: Progress Through All 12 Review Sections

Guide the user through each section of `templates/annual-review-template.md`, one at a time (Standard Mode) or in batches (Quick Mode). For each section, think independently BEFORE presenting analysis to the user (per ADVISOR.md).

**Section 1 (一): Annual Overview**
- Key data: major events count, significant changes
- Overall feeling/assessment
- Three words to summarize the year
- Questions: "What were the 3-5 most impactful events this year?" "If you described this year in three words, what would they be?"

**Section 2 (二): Life Wheel Year-End Assessment**
- Score each of the 8 dimensions (1-10)
- Compare vs. last year (if prior annual review exists, read it for baseline)
- Mark status: normal / risk / over-drafted
- Structural analysis: dangerous weaknesses, over-drafted strengths, systemic risks, surprise improvements
- Questions: "Score each dimension 1-10. For any score below 5 or above 8, explain why."

**Section 3 (三): Pattern Recognition**
- Top 3 positive feedback patterns: what happened, root cause, prerequisites, replicability
- Top 3 cost patterns: surface achievement, hidden sacrifice, spillover, sustainability
- Top 3 repeated failure patterns: description, frequency, root cause, structural fix needed
- Use data from monthly reviews to identify recurring themes
- Questions: "What patterns kept repeating this year, both good and bad?" "What costs were hidden behind your achievements?"

**Section 4 (四): Goal/OKR Achievement**
- Per Objective: original target, actual result, completion percentage, key learning
- Achievement/failure cause analysis: accurate predictions, surprises, external factors, internal factors
- Cross-reference with the plan's success criteria
- Questions: Ask about each specific KR from the plan.

**Section 5 (五): Key Decisions and Turning Points**
- Major decisions: context, outcome, would you choose the same again?
- Turning points and their lasting impact
- Questions: "What were the 2-3 biggest decisions you made this year?" "Would you make the same choices again?"

**Section 6 (六): Time and Energy Audit**
- Time distribution: estimated vs. actual percentages across categories (work, family, projects, social, recovery, waste)
- Energy analysis: top 3 drains, top 3 sources
- Questions: "Where did your time actually go vs. where you planned it to go?" "What drained you most? What energized you?"

**Section 7 (七): Capabilities and Growth**
- New skills acquired, with proficiency level
- Cognitive updates: old belief -> new understanding -> behavioral change
- Influential books/resources and key takeaways
- Questions: "What new capabilities did you develop?" "What beliefs changed?"

**Section 8 (八): Relationships**
- Strengthened relationships
- Weakened or lost relationships
- New meaningful connections
- Questions: "Which relationships grew stronger? Which faded?" "Who new became important?"

**Section 9 (九): Financial Review**
- Income overview, year-over-year change, sources
- Expense overview, major categories, unexpected expenses
- Net worth change (beginning -> end, delta)
- Best and worst financial decisions
- Questions: "How did your financial position change?" "What was your best and worst financial decision?"

**Section 10 (十): Health Review**
- Physical health: notable changes, injuries, exercise consistency
- Mental health: overall state, high-stress periods, coping methods
- Sleep: average duration, quality
- Questions: "How is your body different from a year ago?" "When were your highest stress periods and what helped?"

**Section 11 (十一): Insights for Next Year**
- Amplify: things to do more of (3 items)
- Eliminate: things to stop doing (3 items)
- Repair: things that need fixing (3 items)
- Unfinished items: what and next steps
- Questions: "What should you amplify, eliminate, and repair next year?"

**Section 12 (十二): Gratitude and Letters**
- Top 5 things grateful for
- Letter to past self (this year's self)
- Letter to future self (next year's self)
- Questions: "What 5 things are you most grateful for?" "What would you tell yourself at the start of this year?"

---

### Workflow B: Life Wheel Structured Annual Review

Use this workflow when NO annual plan exists for `{review_year}`. The review is structured around the 8 Life Wheel dimensions rather than goal achievement.

#### B1: Dimension-by-Dimension Deep Dive

Go through the 8 dimensions ONE BY ONE. For each dimension, ask 2-3 specific questions, then wait for the user's response before proceeding to the next.

**1. Health**
- "How did your physical health change this year? Any injuries, improvements, or concerns?"
- "How consistent was your exercise routine? What helped or hindered it?"
- "How was your sleep and energy level throughout the year?"

**2. Career / Studies**
- "What were your biggest professional achievements this year?"
- "What challenges or setbacks did you face at work/school?"
- "What did you learn professionally that changed how you work?"

**3. Wealth / Financial Security**
- "How did your income and spending patterns change?"
- "What was your best and worst financial decision?"
- "How do you feel about your current financial trajectory?"

**4. Family**
- "How did your family relationships evolve this year?"
- "How much quality time did you spend with family?"
- "Were there any significant family events or changes?"

**5. Intimate Relationships**
- "How would you describe the quality of your intimate relationship(s) this year?"
- "What changed, for better or worse?"

**6. Social / Friends**
- "How did your friendships and social life change?"
- "Did you invest enough in meaningful relationships?"
- "Any new connections that became important?"

**7. Personal Growth**
- "What new skills or knowledge did you acquire?"
- "What beliefs or mental models changed?"
- "What books, courses, or experiences had the most impact?"

**8. Leisure / Recovery**
- "Did you maintain adequate rest and recovery time?"
- "What hobbies or leisure activities brought you joy?"
- "Did you feel balanced between productivity and rest?"

#### B2: Synthesize Patterns

After all 8 dimensions are covered:
1. Synthesize cross-dimensional patterns from user responses.
2. Identify common themes, trade-offs, and interconnections.
3. Present pattern analysis to user for validation.

#### B3: Complete Remaining Template Sections

Progress through sections 1-12 of `templates/annual-review-template.md`, but focus on **pattern recognition** (Section 3) rather than goal achievement (Section 4 may be minimal or skipped if no explicit goals existed).

Apply ADVISOR.md Review Analysis Guidelines throughout: honest assessment, evidence-based, structural fixes over willpower.

---

### Step 6: Generate Annual Review Document

After completing all sections (Workflow A or B):

1. Compile all section content into the annual review document.
2. Use `templates/annual-review-template.md` as the structural reference.
3. Replace ALL placeholders with actual data from the conversation.
4. Translate all content to the user's language (detected from conversation; see Output Language Rules).

### Step 7: Write Annual Review File

1. Use Bash heredoc method for the long document:
   - Wrap all `cat` commands in `{ }` braces for a single Bash call.
   - Use `cat >` for the first section, `cat >>` for subsequent sections.
   - Use `<< 'EOF'` (quoted) to prevent variable expansion.
2. Write to: `{vault_path}/{pulse_dir}/40. Annual/{review_year}-annual-review.md`
3. Confirm to user: "Annual review saved to {file_path}"

### Step 8: Offer Next Steps

After saving:
1. Suggest: "Would you like to proceed with annual planning for {next_year}? (`pulse annual-plan`)"
2. If the user agrees, pass the review context forward and begin the annual-plan workflow.

---

## Workflow: `pulse annual-plan`

Execute the following phases in order. This is a multi-phase strategic planning process.

### Step 1: Load Configuration

1. Read `.pulse-config.yaml` following CONFIG.md ("How to Read Config at Runtime").
2. Extract `vault_path`, `pulse_dir`, `timezone`, and `language`.
3. Compute the current date using the configured timezone.

### Step 2: Determine Plan Year

1. Apply Time Period Calculation Rules (see above) to determine the default plan year.
2. Confirm with user.
3. Store the confirmed year as `{plan_year}`.

### Step 3: Check File Overwrite Protection

1. Construct the output path: `{vault_path}/{pulse_dir}/40. Annual/{plan_year}-annual-plan.md`
2. If the file already exists:
   - Read it and display a brief summary (theme word, battlefields, number of OKRs).
   - Ask user: "An annual plan for {plan_year} already exists. Overwrite? [Y/n]"
   - If user declines, abort.
   - If user confirms, proceed.

### Step 4: Pre-Planning Review Check

Before starting annual planning, check for a review of the previous year:

1. Compute `{previous_year}` = `{plan_year}` - 1.
2. Check if the annual review exists: `{vault_path}/{pulse_dir}/40. Annual/{previous_year}-annual-review.md`
3. **If NOT found**:
   - Inform user: "No annual review found for {previous_year}. I recommend doing a review first — it provides essential data for planning."
   - Ask: "Would you like to do the annual review first, or proceed with planning without it?"
   - If user wants review first, switch to the annual-review workflow with `{review_year}` = `{previous_year}`.
   - If user wants to proceed, continue without review context.
4. **If found**:
   - Read the review document.
   - Extract key insights: Life Wheel scores, patterns, amplify/eliminate/repair lists, unfinished items, key learnings.
   - These will be used as inputs throughout the planning phases.

### Step 5: Gather Additional Source Data

1. Get `annual-plan` source directories from `sources.annual-plan.dirs` in config.
2. Scan for `.md` files matching `{plan_year}` per CONFIG.md date matching rules.
3. Read any matched files as additional context.

---

### Phase 0: Reality Check

**Purpose**: Ground the plan in reality before any goal-setting begins.

1. Ask the user to list current constraints across these categories:

   | Constraint Type | Examples |
   |----------------|---------|
   | Time | Work hours, commute, family obligations, fixed commitments |
   | Energy | Health conditions, chronic fatigue, recovery needs |
   | Financial | Budget limits, debt, income uncertainty |
   | Relationships | Caregiving duties, partner expectations, social obligations |

2. **Calculate actual available hours/week** after obligations:
   - Start with 168 hours/week
   - Subtract: sleep (target 7-8h x 7), work (include commute), fixed obligations, meals/hygiene, mandatory family time
   - The remainder is **discretionary time** — this is the ONLY budget for new goals
   - Present the calculation transparently

3. **Challenge unrealistic assumptions** following ADVISOR.md Rule 1 and Rule 3:
   - If discretionary time is less than 20 hours/week, flag this as a tight budget
   - If user claims more available time than the math supports, push back with evidence
   - Reference previous year's review data if available

4. **Identify current main life roles** (e.g., employee, parent, student, caregiver, partner):
   - Each role has time and energy costs
   - Roles constrain which battlefields are realistic

Wait for user response. Record all constraints.

---

### Phase 1: Life Wheel Scan

**Purpose**: Assess current state across all 8 dimensions to identify where intervention is needed.

1. Ask the user to **score each dimension 1-10**:

   | Dimension | Score | Status |
   |-----------|-------|--------|
   | Health | | normal / danger zone / over-drafted |
   | Career / Studies | | |
   | Wealth / Financial Security | | |
   | Family | | |
   | Intimate Relationships | | |
   | Social / Friends | | |
   | Personal Growth | | |
   | Leisure / Recovery | | |

2. **Apply independent analysis** before presenting to user (per ADVISOR.md):
   - Identify dangerous imbalances (any dimension <= 3)
   - Identify system-collapse risks (multiple dimensions <= 4, or health <= 4)
   - Identify over-drafted dimensions (score >= 9 that may be masking costs elsewhere)
   - Cross-reference with previous year's review scores if available

3. **Mark each dimension**:
   - **Normal**: Score 5-8, no immediate structural concern
   - **Danger Zone**: Score <= 4, requires protective action even if not a battlefield
   - **Over-Drafted**: Score >= 9, investigate hidden costs to other dimensions

4. **Present assessment honestly**, highlighting areas the user may be avoiding:
   - Per ADVISOR.md Rule 4: play devil's advocate on comfortable narratives
   - "You scored Health at 3 but Career at 9. Is your career success coming at the cost of your health?"

Wait for user response. Adjust scores if user provides additional context.

---

### Phase 2: Strategic Focus

**Purpose**: Select annual theme and battlefields. Less is more.

1. **Annual theme word selection**:
   - Ask user: "Choose one word or short phrase as your annual theme. This is your north star for decisions."
   - Examples: "Foundation", "Growth", "Balance", "Launch", "Recovery"
   - If previous review exists, suggest themes that address identified gaps.

2. **Battlefield selection** (maximum 2-3):
   - Ask user to identify which dimensions they want to actively improve this year.
   - **Critical constraint**: Maximum 3 battlefields.
   - If user proposes > 3 battlefields, push back per ADVISOR.md Rule 1:
     > "You've selected {N} battlefields. Based on your available {X} discretionary hours/week, each battlefield gets approximately {X/N} hours/week. Research shows meaningful progress requires at minimum 5-7 hours/week of focused effort. I recommend selecting 2-3 battlefields."
   - Provide time budget analysis to support the recommendation.

3. **Define strategic positioning** for ALL dimensions:

   | Position Type | Description | Action Level |
   |--------------|-------------|--------------|
   | **Main Battlefield** | Active improvement focus; receives majority of discretionary time and energy | Maximum effort |
   | **60-Point Strategy** | Maintain at acceptable level; prevent decline but don't optimize | Minimum viable effort |
   | **Not Optimizing** | Consciously deprioritized this year; accept current state | Monitor only |

4. **Annual success criteria**:
   - Define 3 success criteria. At least 2 of 3 met = successful year.
   - Each criterion must be verifiable with evidence.
   - Challenge vague criteria: "How will we know this was achieved?"

Wait for user response. Record battlefield assignments and success criteria.

---

### Phase 3: Anti-Fantasy OKR

**Purpose**: Create verifiable objectives with measurable Key Results. Challenge optimism bias.

For each battlefield:

1. **Define the Objective** — a state change, not an activity:
   - Bad: "Exercise more" (activity)
   - Good: "Establish a sustainable fitness routine that maintains body weight at Xkg and enables 30min continuous running" (state change)

2. **Define Key Results** (2-3 per Objective):
   - Each KR must have a measurable target
   - Each KR must have 12-week (quarterly) milestones
   - Push for specificity per ADVISOR.md Rule 3: "How will we measure this?"

3. **Challenge based on past performance** per ADVISOR.md Rule 8:
   - If previous year review data exists: "Last year you aimed for {X} but achieved {Y}. What's different this time?"
   - If no prior data: "What evidence do you have that this target is achievable?"
   - Encourage setting targets at 70-80% of the aspirational level to build momentum

4. **Format each OKR**:

   ```
   Objective: {state_change_description}

   | Key Result | Measurable Target | Q1 Milestone | Q2 Milestone | Q3 Milestone | Q4 Milestone |
   |------------|-------------------|--------------|--------------|--------------|--------------|
   | KR1: ... | ... | ... | ... | ... | ... |
   | KR2: ... | ... | ... | ... | ... | ... |
   ```

Wait for user response. Refine OKRs based on discussion.

---

### Phase 4: Action System Design

**Purpose**: Convert KRs into concrete, structural action systems. Structure over willpower.

For each Key Result:

1. **Minimal action** (5-20 minute low-barrier start):
   - Define the smallest possible action that still moves the KR forward
   - Must be so easy that "not doing it" feels silly
   - Example: "Put on running shoes and walk out the door (running is optional)"

2. **Environment / system change**:
   - What physical or digital environment modification supports the action?
   - Example: "Set gym bag by front door the night before", "Block social media 9-11am daily"

3. **Failure pre-mortem** (2 risks + fallback for each):
   - Anticipate the two most likely failure scenarios
   - Define a concrete fallback plan for each
   - Per ADVISOR.md Rule 4: play devil's advocate on timelines and assumptions

   | Risk | Likelihood | Fallback Plan |
   |------|-----------|---------------|
   | {risk_1} | High/Med/Low | {fallback_1} |
   | {risk_2} | High/Med/Low | {fallback_2} |

Wait for user response per KR.

---

### Phase 4 (Appendix): Daily Routine Schedule

**Purpose**: Extract repeating routines from the action system into structured schedules.

After all KR action systems are designed:

1. **Extract daily routines**:

   | Time Slot | Routine Name | Linked KR | Duration | Notes |
   |-----------|-------------|-----------|----------|-------|
   | {HH:MM-HH:MM} | {name} | {kr_ref} | {Xmin} | {note} |

2. **Extract weekly routines**:

   | Day of Week | Time Slot | Routine Name | Linked KR | Duration | Notes |
   |-------------|-----------|-------------|-----------|----------|-------|
   | {day} | {HH:MM-HH:MM} | {name} | {kr_ref} | {Xmin} | {note} |

3. **Extract monthly routines**:

   | Date | Time Slot | Routine Name | Linked KR | Duration | Notes |
   |------|-----------|-------------|-----------|----------|-------|
   | {date} | {HH:MM-HH:MM} | {name} | {kr_ref} | {Xmin} | {note} |

4. Validate routines:
   - Check for time conflicts within the same day
   - Verify total routine time fits within the discretionary time budget from Phase 0
   - Flag any conflicts and ask user to resolve

Wait for user confirmation of routine schedule.

---

### Phase 5: Recovery & Input Budget

**Purpose**: Protect rest, learning, and creative input as non-negotiable first-class activities.

1. **Recovery activity pool**:

   | Activity | Energy Effect | Reservation Method |
   |----------|--------------|-------------------|
   | {activity} | +{effect} | {when/how reserved} |

   - Must include at minimum: sleep protection, weekly unstructured time, physical recovery
   - Per ADVISOR.md: INSIST on minimum recovery thresholds

2. **Input activity pool** (learning, reading, exploration):

   | Direction | Expected Gain | Reservation Method |
   |-----------|--------------|-------------------|
   | {direction} | {gain} | {when/how reserved} |

3. **Anti-squeeze strategy**:
   - Identify: "What is most likely to get squeezed when life gets busy?"
   - Define: "What is the protection mechanism?"
   - Per ADVISOR.md Rule 6: recovery is non-negotiable. Push back on "hustle culture" if user tries to minimize recovery:
     > "Eliminating recovery time increases burnout risk and reduces overall productivity within 2-3 weeks. This is not optional. What is your minimum viable recovery plan?"

4. No frequency KPIs for recovery/input — only "clear value + conscious reservation".

Wait for user response.

---

### Phase 6: Annual Subtraction List

**Purpose**: Create space by removing before adding.

1. Ask user: "What will you STOP or REDUCE this year?"
2. Guide with categories:
   - Habits to break
   - Commitments to decline
   - Activities to reduce
   - Relationships to deprioritize (if energy-draining)
   - Information/media to eliminate
3. For each item: what it is, why remove it, estimated time/energy recovered.
4. Frame the subtraction list with the principle:
   > "The key this year is not working harder, but making fewer mistakes. Subtraction comes before addition."
5. If user cannot name at least 3 subtractions, challenge per ADVISOR.md Rule 3:
   > "If you cannot name things to subtract, the plan is likely over-committed. What can you let go of?"

Wait for user response.

---

### Phase 7: 12-Week Rhythm

**Purpose**: Break the annual plan into quarterly execution chunks with clear milestones.

1. Define for each quarter:

   | Quarter | Theme | Aligned KRs | Milestone (Verifiable) | Key Risk & Fallback |
   |---------|-------|-------------|----------------------|-------------------|
   | Q1 (W1-12) | {theme} | {kr_list} | {milestone} | {risk} -> {fallback} |
   | Q2 (W13-24) | {theme} | {kr_list} | {milestone} | {risk} -> {fallback} |
   | Q3 (W25-36) | {theme} | {kr_list} | {milestone} | {risk} -> {fallback} |
   | Q4 (W37-48+) | {theme} | {kr_list} | {milestone} | {risk} -> {fallback} |

2. Each quarter theme should reflect a natural progression:
   - Q1: Foundation / launch / establish habits
   - Q2: Build momentum / deepen practice
   - Q3: Push / expand / mid-year adjustment
   - Q4: Consolidate / harvest / prepare for next year

3. Milestones must be verifiable — reject "make progress on X" in favor of "complete X" or "achieve Y metric."

Wait for user response.

---

### Phase 8: Annual Calendar View

**Purpose**: Month-by-month overview for at-a-glance reference.

1. Generate the calendar view:

   | Month | Quarter | Focus KR | Key Dates |
   |-------|---------|----------|-----------|
   | Jan | Q1 | | |
   | Feb | Q1 | | |
   | Mar | Q1 | | |
   | Apr | Q2 | | |
   | May | Q2 | | |
   | Jun | Q2 | | |
   | Jul | Q3 | | |
   | Aug | Q3 | | |
   | Sep | Q3 | | |
   | Oct | Q4 | | |
   | Nov | Q4 | | |
   | Dec | Q4 | | |

2. Fill in:
   - Focus KR from the 12-week rhythm for that quarter
   - Known key dates: holidays, deadlines, personal milestones, planned vacations, review dates
   - Quarterly review checkpoints (end of W12, W24, W36, W48)

3. Present to user for additions and corrections.

---

### Step 6: Generate Annual Plan Document

After completing all phases (0-8):

1. Compile all phase outputs into the annual plan document.
2. Use `templates/annual-plan-template.md` as the structural reference.
3. Replace ALL placeholders with actual data from the conversation.
4. Translate all content to the user's language (see Output Language Rules).

### Step 7: Write Annual Plan File

1. Use Bash heredoc method for the long document (annual plans are typically 200-400 lines):
   - Wrap all `cat` commands in `{ }` braces for a single Bash call.
   - Use `cat >` for the first section, `cat >>` for subsequent sections.
   - Use `<< 'EOF'` (quoted) to prevent variable expansion.
2. Write to: `{vault_path}/{pulse_dir}/40. Annual/{plan_year}-annual-plan.md`
3. Confirm to user: "Annual plan saved to {file_path}"

### Step 8: Post-Plan Actions

After saving the annual plan, prompt the user with two recommended next steps:

#### Action 1: Create First Month Plan

- Recommend: "I strongly recommend creating the first monthly plan now while the annual strategy is fresh. Would you like to run `pulse monthly-plan`?"
- If user agrees, pass the annual plan context to the monthly-plan workflow.

#### Action 2: Calendar Sync

Offer to sync routines to the user's calendar:

1. Ask: "Would you like to export your routines to a calendar (.ics) file?"
2. If yes, execute the calendar integration process (see Calendar Integration section below).

---

## Calendar Integration

This section describes how to sync routine schedules from the annual plan to external calendars.

### Process

1. **Parse routines** from the annual plan's routine schedule section (Phase 4 Appendix):
   - Extract daily, weekly, and monthly routine tables.
   - For each routine row, create a `RoutineEvent` object with:
     - `name`: routine name
     - `start_time`: time slot (HH:MM format)
     - `duration`: duration string
     - `frequency`: "daily", "weekly:{day_number}", or "monthly:{day_number}"
     - `kr_ref`: linked KR reference
     - `note`: additional notes

2. **Validate routines** (using `utils/calendar_integration.py` if available, otherwise validate manually):
   - Check for:
     - Time conflicts between same-day events
     - Invalid time formats
     - Missing required data
   - If `utils/calendar_integration.py` exists, call `validate_routines(events)`.
   - If the utility does not exist, perform validation logic directly (compare time ranges, verify HH:MM format, check required fields).
   - If validation issues are found, present them to user and ask for corrections.

3. **Generate ICS file**:
   - Get timezone from config (`timezone` field in `.pulse-config.yaml`).
   - If `utils/calendar_integration.py` exists, call `generate_ics(events, plan_year, timezone)` to produce the ICS content.
   - If the utility does not exist, generate the ICS content directly using the standard iCalendar (RFC 5545) format with VEVENT entries for each routine, respecting RRULE for recurring events.
   - Write to: `{vault_path}/{pulse_dir}/40. Annual/routines-{plan_year}.ics`

4. **Provide import instructions** based on user's platform:

   | Platform | Import Method |
   |----------|--------------|
   | macOS Calendar | Double-click the .ics file, or File > Import |
   | Google Calendar | Settings > Import & Export > Import > select .ics file |
   | Outlook | File > Open & Export > Import/Export > Import an iCalendar file |
   | iOS | Open .ics file from Files app, tap "Add All Events" |

5. Confirm: "Calendar file saved to {ics_path}. Import it into your calendar app using the instructions above."

---

## Workflow: `pulse annual` (Guided Combined)

The combined `pulse annual` flow guides the user through the choice and then delegates:

1. Present choice (see Command Dispatch above).
2. If user chooses **Annual Review**:
   - Execute `pulse annual-review` workflow (Steps 1-8).
   - After completion, offer to continue with annual planning.
3. If user chooses **Annual Plan**:
   - Execute `pulse annual-plan` workflow (Steps 1-8, Phases 0-8).
   - The pre-planning review check (Step 4) will handle the review dependency.

---

## Document Generation Guidelines

### Bash Heredoc Method

Annual documents are long (200-500 lines). Always use the Bash heredoc method:

```bash
{
cat > "{output_path}" << 'EOF'
# {year} Annual Plan/Review
...first section content...
EOF

cat >> "{output_path}" << 'EOF'
## Section 2
...second section content...
EOF

cat >> "{output_path}" << 'EOF'
## Section 3
...third section content...
EOF
}
```

Key rules:
- Wrap all `cat` commands in `{ }` braces for a single Bash call
- Use `cat >` (overwrite) for the first section
- Use `cat >>` (append) for all subsequent sections
- Use `<< 'EOF'` (single-quoted) to prevent shell variable expansion
- Fill ALL template placeholders with actual data — no unfilled `{placeholder}` tokens in output

### Output Language Rules

1. Detect the user's language from conversation context.
2. Generate ALL content in that language:
   - Section headers and sub-headers
   - Table headers and row labels
   - Descriptions, analyses, and recommendations
   - Questions and prompts
3. Templates are structural references only — translate everything from them.
4. Keep the following UNTRANSLATED:
   - Proper nouns (names, places)
   - Technical terms: OKR, KR, PDCA, Q1-Q4
   - File paths and filenames
   - Markdown syntax

---

## File Operations Reference

### Output Directory

All annual files are stored in: `{vault_path}/{pulse_dir}/40. Annual/`

### File Naming Conventions

| File Type | Naming Pattern | Example |
|-----------|---------------|---------|
| Annual Plan | `{YYYY}-annual-plan.md` | `2026-annual-plan.md` |
| Annual Review | `{YYYY}-annual-review.md` | `2025-annual-review.md` |
| Routines ICS | `routines-{YYYY}.ics` | `routines-2026.ics` |

### Reading Monthly Files for Annual Review

When gathering monthly data for the annual review:

1. Scan `{vault_path}/{pulse_dir}/30. Monthly/` directory.
2. Match files containing `{review_year}-{MM}` in the filename.
3. Separate monthly reviews (`*-monthly-review.md`) from monthly plans (`*-monthly-plan.md`).
4. Read all matched files and extract relevant data.

---

## Cross-References

| Reference | File | Purpose |
|-----------|------|---------|
| Annual plan template | `templates/annual-plan-template.md` | Structural template for annual strategic map; defines phases, sections, and placeholders |
| Annual review template | `templates/annual-review-template.md` | Structural template for annual review; defines 12 sections and placeholders |
| Calendar utility | `utils/calendar_integration.py` (optional) | ICS generation, routine validation, time conflict detection; if not present, generate ICS directly |
| Config reading | CONFIG.md | Config file loading, path resolution, date matching rules, timezone |
| Advisor persona | ADVISOR.md | Independent thinking principles, review/planning guidelines, feedback style |
| Monthly files | `{vault_path}/{pulse_dir}/30. Monthly/` | Source data for annual review; target for post-plan monthly planning |
| Monthly plan command | MONTHLY.md | Monthly planning workflow, triggered as post-annual-plan action |
