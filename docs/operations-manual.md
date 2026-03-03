# Skills Marketplace 操作手册

> charliec 个人 Claude Code Skills Marketplace 的完整操作指南。
> 适用于自己日常使用参考，也适合新用户快速上手。

---

## 目录

1. [项目概述](#1-项目概述)
2. [安装与配置](#2-安装与配置)
3. [项目结构](#3-项目结构)
4. [核心概念](#4-核心概念)
5. [CLI 命令参考](#5-cli-命令参考)
6. [日常操作流程](#6-日常操作流程)
7. [配置文件格式说明](#7-配置文件格式说明)
8. [版本管理策略](#8-版本管理策略)
9. [验证规则](#9-验证规则)
10. [错误排查指南](#10-错误排查指南)
11. [开发与测试](#11-开发与测试)
12. [速查表](#12-速查表)

---

## 1. 项目概述

Skills Marketplace 是一个个人 Claude Code Skills 管理平台。每个 skill 独立开发、独立 git 仓库，marketplace 作为统一的注册中心，存储所有 skill 的文件快照和元数据。

**核心理念：**
- 每个 skill 有自己独立的 git 仓库，位于 `/Users/charliec/Projects/` 下
- Marketplace 仓库存储所有已发布 skill 的文件副本（快照模式）
- CLI 工具 `sm` 负责初始化、验证、发布和更新操作
- 版本管理基于 Git Tags，遵循 SemVer 语义化版本

**技术栈：** Python 3.11+ / Typer / PyYAML / Rich / UV

---

## 2. 安装与配置

### 2.1 前置条件

- Python >= 3.11
- [UV](https://docs.astral.sh/uv/) 包管理器
- Git

### 2.2 安装 CLI

```bash
cd /Users/charliec/Projects/skills-marketplace/cli

# 使用 UV 安装（开发模式）
uv pip install -e .

# 验证安装
sm --help
```

### 2.3 配置 Marketplace 路径

CLI 使用 `~/.config/sm/config.json` 存储全局配置。首次运行任何命令时会自动创建默认配置文件。

**手动配置：**

```bash
mkdir -p ~/.config/sm
cat > ~/.config/sm/config.json << 'EOF'
{
  "marketplacePath": "/Users/charliec/Projects/skills-marketplace",
  "defaultAuthor": "charliec"
}
EOF
```

**配置字段：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `marketplacePath` | 是 | Marketplace 仓库的绝对路径 |
| `defaultAuthor` | 否 | 默认作者名 |

---

## 3. 项目结构

### 3.1 Marketplace 仓库结构

```
skills-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace 注册表（核心元数据）
├── plugins/                      # 所有已发布 skill 的文件快照
│   └── <skill-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin 配置
│       ├── skills/
│       │   └── <skill-name>/
│       │       ├── SKILL.md      # Skill 定义（必需）
│       │       ├── scripts/      # 可执行脚本
│       │       └── references/   # 参考文档
│       └── commands/
│           └── <skill-name>.md   # Slash 命令
├── cli/                          # sm CLI 工具源码
│   ├── pyproject.toml
│   ├── src/sm/                   # 核心模块
│   └── tests/                    # 测试套件
└── docs/                         # 文档
```

### 3.2 独立 Skill 项目结构

每个 skill 独立开发时，项目结构如下：

```
my-skill/
├── .claude-plugin/
│   └── plugin.json               # Plugin 配置（name, version, skills, commands）
├── skills/
│   └── my-skill/
│       ├── SKILL.md              # Skill 定义文件（必需）
│       ├── scripts/              # 可执行脚本目录（可选）
│       └── references/           # 参考文档目录（可选）
├── commands/
│   └── my-skill.md               # Slash 命令定义（可选）
└── .gitignore
```

---

## 4. 核心概念

### 4.1 Skill

一个 Skill 是 Claude Code 的能力扩展单元，通过 `SKILL.md` 文件定义。它告诉 Claude 何时激活以及如何执行特定任务。

### 4.2 Plugin

一个 Plugin 是 Skill 的容器，包含一个或多个 skill 和对应的 slash 命令。通过 `.claude-plugin/plugin.json` 配置。

### 4.3 Marketplace

Marketplace 是所有已发布 plugin 的注册中心，通过 `.claude-plugin/marketplace.json` 管理索引。

### 4.4 发布（Publish）

将 skill 项目的文件快照复制到 marketplace 仓库，并更新注册表元数据。

### 4.5 更新（Update）

从 skill 源仓库拉取最新代码快照到 marketplace，本质是"重新发布"。

---

## 5. CLI 命令参考

### 5.1 `sm init` — 初始化新 Skill 项目

```bash
sm init [--name <name>]
```

**用途：** 在当前目录创建标准的 skill 项目结构。

**参数：**
- `--name`：Skill 名称。不指定时默认使用当前目录名。

**创建内容：**
- `.claude-plugin/plugin.json` — 初始版本 `0.1.0`
- `skills/<name>/SKILL.md` — 带 YAML frontmatter 的模板
- `skills/<name>/scripts/` — 脚本目录
- `skills/<name>/references/` — 参考文档目录
- `commands/<name>.md` — Slash 命令模板
- `.gitignore`

**示例：**
```bash
mkdir my-new-skill && cd my-new-skill
sm init --name my-new-skill
# ✓ Initialized skill project: my-new-skill
```

---

### 5.2 `sm validate` — 验证 Skill 结构

```bash
sm validate [path]
```

**用途：** 检查 skill 项目结构是否符合规范。

**参数：**
- `path`：Skill 项目路径，默认为当前目录 `.`

**验证内容：**
1. `.claude-plugin/plugin.json` 存在且是合法 JSON
2. `plugin.json` 有 `name` 字段
3. 每个 skill 定义都有对应的 `SKILL.md` 文件
4. 每个 `SKILL.md` 都有合法的 YAML frontmatter（含 `name` 和 `description`）
5. 每个 command 定义都有对应的文件

**示例：**
```bash
sm validate
# ✓ Skill structure is valid

sm validate /path/to/other-skill
# ✗ SKILL.md in skills/other-skill has no valid YAML frontmatter
```

---

### 5.3 `sm publish` — 发布 Skill 到 Marketplace

```bash
sm publish [--version x.y.z] [-m "message"]
```

**用途：** 将当前目录的 skill 发布到 marketplace。必须在 skill 项目根目录执行。

**参数：**
- `--version`：指定发布版本号。不指定时从最新 git tag 读取。
- `-m`：发布消息（保留字段，暂未使用）。

**完整执行流程：**

```
1. 验证 skill 结构 (validate_skill)
   ↓ 失败 → 打印错误并退出
2. 从 plugin.json 读取 skill 名称
3. 确定版本号
   ├─ 有 --version → 使用指定版本
   ├─ 有 git tag → 使用最新 tag（去掉 v 前缀）
   └─ 都没有 → 报错退出
4. 检查 git 未提交变更 → 黄色警告，确认后继续
5. 创建 git tag（如果当前 tag 不匹配）
6. 复制文件到 marketplace/plugins/<name>/
   └─ 排除: .git, .venv, __pycache__, node_modules, .DS_Store, .pytest_cache
7. 更新元数据
   ├─ plugins/<name>/.claude-plugin/plugin.json → version
   └─ marketplace.json → plugin entry + version PATCH+1
8. 输出结果
```

**示例：**
```bash
cd /Users/charliec/Projects/my-skill

# 指定版本发布
sm publish --version 1.0.0
# ✓ Published my-skill v1.0.0 to marketplace

# 从 git tag 自动读取版本
git tag v1.1.0
sm publish
# ✓ Published my-skill v1.1.0 to marketplace
```

> **注意：** publish 命令不会自动 git commit/push marketplace 仓库。需要手动提交。

---

### 5.4 `sm update` — 更新已发布的 Skill

```bash
sm update <skill-name> [--version x.y.z]
```

**用途：** 从源仓库拉取 skill 的最新代码到 marketplace。可在任意目录执行。

**参数：**
- `<skill-name>`：（必需）要更新的 skill 名称
- `--version`：目标版本号

**执行流程：**

```
1. 从 marketplace.json 查找 skill 记录
   ↓ 未找到 → 报错退出
2. 从 _meta.sourceRepo 获取源仓库路径
   ↓ 路径不存在 → 报错退出
3. 比较 git HEAD SHA
   ├─ SHA 相同 且 无指定版本 → "已是最新" 并退出
   └─ SHA 不同 或 有指定版本 → 调用 publish_skill() 重新发布
```

**示例：**
```bash
# 更新到最新版本（自动检测变更）
sm update my-skill
# ✓ Updated my-skill to v1.2.0

# 指定版本更新
sm update my-skill --version 2.0.0
# ✓ Updated my-skill to v2.0.0

# 无变更时
sm update my-skill
# ✓ my-skill is already up to date
```

---

### 5.5 `sm list` — 列出所有 Skills

```bash
sm list
```

**用途：** 列出 marketplace 中所有已发布的 skills。

**输出格式：**
```
NAME                      VERSION      SOURCE
----------------------------------------------------------------------
my-skill                  1.2.0        /Users/charliec/Projects/my-skill
another-skill             2.0.0        /Users/charliec/Projects/another-skill
```

---

### 5.6 `sm status` — 检查更新状态

```bash
sm status
```

**用途：** 检查每个已发布 skill 是否有未发布的变更。

**状态符号：**
| 符号 | 含义 |
|------|------|
| `✓` | 最新，无变更 |
| `⚠` | 源仓库有未发布的变更 |
| `?` | 源仓库路径不存在 |

**输出示例：**
```
  ✓ my-skill              1.2.0      up to date
  ⚠ another-skill         2.0.0      has unpublished changes
  ? deprecated-skill      0.5.0      source not found
```

---

## 6. 日常操作流程

### 6.1 创建并发布一个新 Skill（完整流程）

```bash
# Step 1: 创建项目目录
mkdir ~/Projects/my-awesome-skill
cd ~/Projects/my-awesome-skill

# Step 2: 初始化 skill 结构
sm init --name my-awesome-skill

# Step 3: 编辑 SKILL.md（核心定义）
$EDITOR skills/my-awesome-skill/SKILL.md
# 修改 frontmatter 中的 description
# 编写 skill 的指令内容

# Step 4: 编辑 plugin.json（补充描述）
$EDITOR .claude-plugin/plugin.json
# 填写 description 字段

# Step 5: 编辑 slash 命令
$EDITOR commands/my-awesome-skill.md
# 填写命令的触发说明

# Step 6: 验证结构
sm validate
# ✓ Skill structure is valid

# Step 7: 初始化 git 并提交
git init
git add .
git commit -m "initial: create my-awesome-skill"

# Step 8: 发布到 marketplace
sm publish --version 1.0.0
# ✓ Published my-awesome-skill v1.0.0 to marketplace

# Step 9: 提交 marketplace 变更
cd ~/Projects/skills-marketplace
git add .
git commit -m "publish: my-awesome-skill v1.0.0"
git push
```

### 6.2 更新已有 Skill

```bash
# Step 1: 修改 skill 源码
cd ~/Projects/my-awesome-skill
$EDITOR skills/my-awesome-skill/SKILL.md

# Step 2: 提交变更
git add .
git commit -m "improve: add error handling examples"

# Step 3: 更新到 marketplace
sm update my-awesome-skill --version 1.1.0
# ✓ Updated my-awesome-skill to v1.1.0

# Step 4: 提交 marketplace 变更
cd ~/Projects/skills-marketplace
git add .
git commit -m "update: my-awesome-skill v1.1.0"
git push
```

### 6.3 日常检查

```bash
# 查看所有已发布的 skills
sm list

# 检查哪些 skill 有未发布的变更
sm status

# 批量更新有变更的 skills
sm status  # 查看 ⚠ 标记的 skills
sm update skill-a --version x.y.z
sm update skill-b --version x.y.z
```

---

## 7. 配置文件格式说明

### 7.1 marketplace.json

**位置：** `<marketplace>/.claude-plugin/marketplace.json`

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "charliec-skills",
  "version": "1.0.3",
  "description": "charliec personal Skills Marketplace",
  "owner": { "name": "charliec" },
  "plugins": [
    {
      "name": "my-skill",
      "description": "What this skill does",
      "version": "1.2.0",
      "source": "./plugins/my-skill",
      "_meta": {
        "sourceRepo": "/Users/charliec/Projects/my-skill",
        "gitCommitSha": "abc123def456789...",
        "publishedAt": "2026-03-03T12:00:00+00:00"
      }
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | Marketplace 名称 |
| `version` | string | Marketplace 版本（每次发布/更新自动 PATCH+1） |
| `plugins[].name` | string | Skill 名称 |
| `plugins[].version` | string | Skill 当前版本 |
| `plugins[].source` | string | Marketplace 内的相对路径 |
| `plugins[]._meta.sourceRepo` | string | 源仓库绝对路径 |
| `plugins[]._meta.gitCommitSha` | string | 发布时的 git commit SHA |
| `plugins[]._meta.publishedAt` | string | 发布时间（ISO 8601 UTC） |

### 7.2 plugin.json

**位置：** `<skill-project>/.claude-plugin/plugin.json`

```json
{
  "name": "my-skill",
  "version": "0.1.0",
  "description": "Detailed description of what the skill does",
  "skills": [
    {
      "name": "my-skill",
      "description": "When to activate this skill",
      "path": "skills/my-skill"
    }
  ],
  "commands": [
    {
      "name": "my-skill",
      "description": "What this command does",
      "path": "commands/my-skill.md"
    }
  ]
}
```

### 7.3 SKILL.md

**位置：** `skills/<name>/SKILL.md`

```markdown
---
name: my-skill
description: Use when the user asks to do X, triggers on keywords Y and Z
---

# My Skill

## Overview
What this skill does and when it should be activated.

## Instructions
Step-by-step instructions for Claude to follow.

## Examples
Usage examples.
```

**Frontmatter 必填字段：**
- `name` — Skill 标识符
- `description` — 激活条件描述

### 7.4 Slash 命令文件

**位置：** `commands/<name>.md`

```markdown
---
name: my-skill
description: What this command does
---

Activate the my-skill skill and follow its instructions.
```

---

## 8. 版本管理策略

### 8.1 Skill 版本

使用 Git Tags，遵循 [Semantic Versioning](https://semver.org/)：

| 变更类型 | 版本变更 | 示例 |
|---------|---------|------|
| 修正 SKILL.md 措辞、小 bug 修复 | **PATCH** | 1.0.0 → 1.0.1 |
| 新增 scripts、references、新功能 | **MINOR** | 1.0.1 → 1.1.0 |
| SKILL.md 大幅改写、破坏性变更 | **MAJOR** | 1.1.0 → 2.0.0 |

### 8.2 Marketplace 版本

| 变更类型 | 版本变更 |
|---------|---------|
| 添加新 plugin | PATCH +1 |
| 更新任何 plugin | PATCH +1 |
| Marketplace 结构变更 | MINOR +1 |

### 8.3 版本一致性

以下三处版本号由 CLI 自动保持同步：
1. Skill 仓库的 **git tag**（如 `v1.2.0`）
2. `plugins/<name>/.claude-plugin/plugin.json` → `version` 字段
3. `marketplace.json` → 对应 plugin 的 `version` 字段

### 8.4 版本确定优先级

发布时版本号的确定顺序：
1. `--version` 参数指定的版本（最高优先级）
2. 当前 HEAD 最近的 git tag
3. 均无 → 报错退出

---

## 9. 验证规则

`sm validate` 执行以下检查：

| # | 检查项 | 错误信息 |
|---|--------|---------|
| 1 | `.claude-plugin/plugin.json` 文件存在 | Missing: .claude-plugin/plugin.json |
| 2 | plugin.json 是合法 JSON | Invalid JSON in plugin.json: ... |
| 3 | plugin.json 有 `name` 字段 | plugin.json missing 'name' field |
| 4 | 每个 skill 有对应的 SKILL.md | Missing: skills/\<name>/SKILL.md |
| 5 | SKILL.md 有合法 YAML frontmatter | SKILL.md in ... has no valid YAML frontmatter |
| 6 | frontmatter 有 `name` 字段 | SKILL.md in ... frontmatter missing 'name' |
| 7 | frontmatter 有 `description` 字段 | SKILL.md in ... frontmatter missing 'description' |
| 8 | 每个 command 有对应文件 | Missing command file: ... |

---

## 10. 错误排查指南

### 常见错误及解决方法

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `✗ marketplacePath not configured` | 配置文件中 marketplacePath 为空 | 编辑 `~/.config/sm/config.json`，填写正确路径 |
| `No version specified and no git tag found` | 未指定版本且 git 仓库没有 tag | 使用 `--version` 参数或先 `git tag v1.0.0` |
| `Skill 'xxx' not found in marketplace` | update 时 skill 未在 marketplace 中注册 | 确认 skill 名称正确，或先用 `sm publish` 发布 |
| `Source repo not found: ...` | 源仓库路径已变更或被删除 | 手动修改 marketplace.json 中的 `_meta.sourceRepo` |
| `⚠ Uncommitted changes detected` | 有未提交的代码变更 | 先 `git add && git commit`，或确认后继续 |
| `Missing: .claude-plugin/plugin.json` | 不在 skill 项目根目录 | 确认当前目录是 skill 项目根目录 |
| `SKILL.md has no valid YAML frontmatter` | SKILL.md 开头缺少 `---` 分隔的 YAML 块 | 添加 frontmatter（见 7.3 节格式） |

### 排查步骤

**发布失败时：**
```bash
# 1. 先验证结构
sm validate

# 2. 检查 git 状态
git status
git tag -l

# 3. 确认配置
cat ~/.config/sm/config.json

# 4. 确认 marketplace 目录存在
ls -la $(cat ~/.config/sm/config.json | python3 -c "import sys,json; print(json.load(sys.stdin)['marketplacePath'])")
```

**更新失败时：**
```bash
# 1. 确认 skill 名称
sm list

# 2. 检查源仓库是否可访问
# 查看 marketplace.json 中记录的 sourceRepo 路径

# 3. 检查是否有实际变更
sm status
```

---

## 11. 开发与测试

### 11.1 开发环境搭建

```bash
cd /Users/charliec/Projects/skills-marketplace/cli

# 安装开发依赖
uv sync --group dev

# 安装为可编辑模式
uv pip install -e .
```

### 11.2 运行测试

```bash
cd /Users/charliec/Projects/skills-marketplace/cli

# 运行全部测试
uv run pytest -v

# 运行特定测试文件
uv run pytest tests/test_publish.py -v

# 运行特定测试
uv run pytest tests/test_publish.py::test_publish_happy_path -v
```

### 11.3 测试覆盖

| 测试文件 | 覆盖模块 |
|---------|---------|
| `test_config.py` | 配置加载/保存 |
| `test_validator.py` | Skill 结构验证 |
| `test_init.py` | init 命令 |
| `test_git_utils.py` | Git 操作工具 |
| `test_publish.py` | publish 命令 |
| `test_update.py` | update 命令 |
| `test_list_status.py` | list/status 命令 |
| `test_e2e.py` | 端到端生命周期测试 |

### 11.4 项目源码结构

```
cli/src/sm/
├── __init__.py          # 包初始化
├── main.py              # Typer CLI 入口，定义所有命令
├── config.py            # ~/.config/sm/config.json 读写
├── git_utils.py         # Git 操作封装（SHA、tag、status）
├── validator.py         # Skill 结构验证 + YAML frontmatter 解析
├── init_cmd.py          # sm init 实现
├── publish_cmd.py       # sm publish 实现（核心）
└── update_cmd.py        # sm update 实现
```

---

## 12. 速查表

### 命令速查

```bash
# 创建新 skill
mkdir my-skill && cd my-skill && sm init --name my-skill

# 验证结构
sm validate

# 首次发布
sm publish --version 1.0.0

# 更新已发布的 skill
sm update my-skill --version 1.1.0

# 查看所有 skills
sm list

# 检查更新状态
sm status
```

### 文件位置速查

| 文件 | 路径 |
|------|------|
| CLI 全局配置 | `~/.config/sm/config.json` |
| Marketplace 注册表 | `<marketplace>/.claude-plugin/marketplace.json` |
| Skill 定义 | `skills/<name>/SKILL.md` |
| Plugin 配置 | `.claude-plugin/plugin.json` |
| Slash 命令 | `commands/<name>.md` |

### 发布流程速查

```
编辑 SKILL.md → git commit → sm publish --version x.y.z → cd marketplace → git add . → git commit → git push
```

### 文件排除列表（发布时跳过）

`.git`, `.venv`, `__pycache__`, `node_modules`, `.DS_Store`, `.pytest_cache`
