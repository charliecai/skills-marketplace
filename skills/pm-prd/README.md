# pm-prd

一个 Claude Code 技能插件，充当专业的**产品经理 PRD 助手**，覆盖从模糊需求到可评审 PRD 和可交互 Demo 的全流程。

> 版本：0.1.1 | 作者：charliec

### 核心特性

- **全流程自动识别和切换** — 根据自然语言自动路由到对应工作流，并在合适时机主动建议切换（如讨论充分后 → PRD 创作 → 演示 Demo）
- **PRD 批量标注修改** —— 支持 `{{{...}}}` 内嵌标记批量标注修改点，方便批量修改 PRD，不用一句话一句话跟 AI 交流
- **PRD 写作质量管控** — 10 条写作规则 + 反模式检查，消除含糊、重复和 AI 味道的表达
- **可交互 Demo 生成** —— 基于 PRD 生成可交互 HTML 原型演示页面，支持用户交互和反馈
- **PRD ↔ Demo 双向同步** — 文档和原型在迭代中保持一致
- **截图自动回填** — 捕获 Demo 截图并插入 PRD 的对应章节
- **需求-代码交叉验证** — 评审时将 PRD 描述与实际代码实现进行比对

## 功能概览

支持五种工作模式，根据用户意图自动识别或手动指定：

| # | 模式 | 适用场景 | 输出物 |
|---|------|---------|--------|
| 1 | **方案讨论** | 需求澄清、方案评估、功能设计、优先级判断 | 结构化建议 |
| 2 | **PRD 创作** | 从零创作 PRD / MRD / BRD / 用户故事 | 完整产品文档 |
| 3 | **PRD 修改** | 根据反馈修改已有 PRD，支持 `{{{...}}}` 内嵌标记批量标注修改点 | 修改后文档 + 修改报告 |
| 4 | **文档评审** | 评审产品文档，支持需求-代码交叉验证 | 评审报告 |
| 5 | **演示 Demo** | 基于 PRD 生成可交互 HTML 原型演示页面 | Demo 页面集（index.html + 子页面） |

## 安装

### 方式一：通过 Charliec's Skills Marketplace 安装

```bash
claude plugin marketplace add https://github.com/charliecai/skills-marketplace
claude plugin install pm-prd
```
按提示完成安装即可。

### 方式二：通过 AI 安装

将以下内容发送给你的 AI 助手（Claude Code、Cursor、Windsurf 等）：

```
请帮我安装技能 pm-prd https://github.com/charliecai/skills-marketplace/blob/main/skills/pm-prd/
```

AI 会自动完成下载和配置。

## 项目结构

```
pm-prd/
├── SKILL.md                              # 技能主定义文件（入口）
├── .claude-plugin/
│   └── plugin.json                       # Claude 插件配置
└── references/                           # 核心方法论与工作流文档
    ├── MODE-1-DISCUSSION.md              # 方案讨论流程
    ├── MODE-2-PRD-CREATION.md            # PRD 创作流程
    ├── MODE-3-PRD-MODIFICATION.md        # PRD 修改流程
    ├── MODE-4-DOC-REVIEW.md              # 文档评审流程
    ├── MODE-5-DEMO-GENERATION.md         # 演示 Demo 生成流程
    ├── PRD-TEMPLATE.md                   # 标准 PRD 文档模板
    ├── PRD-WRITING-STYLE.md              # 10 条写作规则与反模式清单
    ├── REVIEW-CHECKLIST.md               # 系统化评审检查清单
    └── PM-BEST-PRACTICES.md              # 产品经理最佳实践与方法论
```

## 使用方式

在 AI 中用自然语言触发：

```
# 方案讨论
"分析一下这个审批催办的需求"
"帮我评估一下这个方案"

# PRD 创作
"帮我写一个 PRD"
"创建一个用户故事"

# PRD 修改
"根据评审反馈修改这个 PRD"
"更新文档中 {{{需要改的部分}}}"

# 文档评审
"评审一下这个文档"
"帮我检查这个 PRD 的质量"

# 演示 Demo
"基于这个 PRD 生成一个 demo"
"做一个可交互的原型演示"
```

也可以直接加载 PRD 文件，技能会输出文档摘要并列出可选操作。

## 参考文档

| 文档 | 用途 |
|------|------|
| `PRD-TEMPLATE.md` | 标准 PRD 结构模板，功能自包含、流程图分层 |
| `PRD-WRITING-STYLE.md` | 10 条写作规则：首句即结论、具体胜于抽象、认知递进、去 AI 味 |
| `REVIEW-CHECKLIST.md` | 按优先级分级的评审清单（必查 → 建议 → 可选），含交叉验证维度 |
| `PM-BEST-PRACTICES.md` | HR SaaS / B2B 方法论：RICE 评分、权限模型、多租户考量、异常场景清单 |

## 许可

MIT License
