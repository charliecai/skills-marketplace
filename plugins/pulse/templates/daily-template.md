<!--
  Pulse Daily Template
  ====================
  每日文件包含三个部分:

  Part 1 - 当日记录: 由 `pulse daily-plan` 创建文件时生成骨架，用户在一天中手动填写
  Part 2 - Daily Review: 由晚间运行的 `pulse daily-review` 自动填充
  Part 3 - Daily Plan: 由前一天运行的 `pulse daily-plan` 自动填充次日计划
-->

# {date} 日志

> 创建时间: {created_at}
> 所属周计划: [[{week_id}-weekly-plan]]

---

## 当日记录

> 随时记录当天发生的事情、想法、临时任务等

-

---

## Daily Review

> 由 `pulse daily-review` 生成，请勿手动编辑此区域

### 数据源摘要

> 以下内容从配置的数据源自动收集

{data_source_summaries}

### 工作回顾

| 计划任务 | 完成状态 | 备注 |
|----------|---------|------|
| {task} | ✅/❌/⚠️ | {note} |

#### 关键产出
- {key_output}

#### 阻塞与问题
- {blocker}

### 生活记录

| 维度 | 内容 | 备注 |
|------|------|------|
| 健康 | {content} | {note} |
| 事业/学习 | | |
| 财务 | | |
| 家庭 | | |
| 亲密关系 | | |
| 社交 | | |
| 个人成长 | | |
| 休闲恢复 | | |

### AI 分析

#### 计划 vs 实际
{gap_analysis}

#### 做得好的
- {positive}

#### 需改进的
- {improvement}

---

## Daily Plan（{next_date} 计划）

> 由前一天的 `pulse daily-plan` 生成

### 工作任务

| 优先级 | 任务 | 对齐周目标 | 预估时间 |
|--------|------|-----------|----------|
| P0 | {task} | {weekly_goal} | {est_time} |
| P1 | | | |
| P2 | | | |

### 生活安排

| 维度 | 计划 | 时间段 |
|------|------|--------|
| 健康 | {plan} | {time_slot} |
| 个人成长 | | |
| 其他 | | |

### 时间块

| 时间段 | 安排 |
|--------|------|
| 上午 | {morning_plan} |
| 下午 | {afternoon_plan} |
| 晚上 | {evening_plan} |

---

*由 Pulse PDCA System 生成*
