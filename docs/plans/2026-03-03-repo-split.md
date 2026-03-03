# Repository Split Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the monorepo `skills-marketplace` into two sub-directories: `skills-marketplace/` (marketplace content) and `sm-cli/` (CLI tool), both under the same parent project directory.

**Architecture:** Move marketplace content (`.claude-plugin/`, `plugins/`, `CLAUDE.md`, docs) into a new `skills-marketplace/` subdirectory as its own git repo. Move CLI code (`cli/`) into a new `sm-cli/` subdirectory as its own git repo. Update all paths and configs accordingly.

**Tech Stack:** Git, UV, Python, shell

---

### Current State

```
/Users/charliec/Projects/skills-marketplace/    ← single git repo
├── .claude-plugin/marketplace.json
├── .claude/settings.local.json
├── plugins/
├── cli/                                        ← sm CLI source
│   ├── pyproject.toml
│   ├── src/sm/
│   └── tests/
├── docs/
│   ├── plans/
│   └── operations-manual.md
├── CLAUDE.md
└── .gitignore
```

### Target State

```
/Users/charliec/Projects/skills-marketplace/    ← parent directory (NOT a git repo)
├── skills-marketplace/                         ← git repo 1: marketplace content
│   ├── .claude-plugin/marketplace.json
│   ├── .claude/settings.local.json
│   ├── plugins/
│   ├── docs/
│   │   ├── plans/
│   │   └── operations-manual.md
│   ├── CLAUDE.md
│   └── .gitignore
└── sm-cli/                                     ← git repo 2: CLI tool
    ├── pyproject.toml
    ├── src/sm/
    ├── tests/
    └── .gitignore
```

### Key Facts

- `sm` is installed via `uv tool install --editable /Users/charliec/Projects/skills-marketplace/cli`
- `sm` binary at `/Users/charliec/.local/bin/sm`, venv at `/Users/charliec/.local/share/uv/tools/sm/`
- Global config at `~/.config/sm/config.json` currently points `marketplacePath` to `/Users/charliec/Projects/skills-marketplace`
- The `.claude/settings.local.json` belongs with the marketplace repo

---

### Task 1: Create the two sub-directories and move files

**Step 1: Create target directories**

```bash
cd /Users/charliec/Projects/skills-marketplace
mkdir -p skills-marketplace
mkdir -p sm-cli
```

**Step 2: Move marketplace content into `skills-marketplace/`**

```bash
cd /Users/charliec/Projects/skills-marketplace

# Move marketplace content
mv .claude-plugin skills-marketplace/
mv plugins skills-marketplace/
mv CLAUDE.md skills-marketplace/
mv docs skills-marketplace/
mv .claude skills-marketplace/

# Copy .gitignore (both repos need one)
cp .gitignore skills-marketplace/.gitignore
```

**Step 3: Move CLI into `sm-cli/`**

```bash
cd /Users/charliec/Projects/skills-marketplace

# Move CLI content (contents of cli/, not the cli/ dir itself)
mv cli/pyproject.toml sm-cli/
mv cli/src sm-cli/
mv cli/tests sm-cli/
mv .gitignore sm-cli/.gitignore

# Clean up empty cli/ directory
rmdir cli
```

**Step 4: Remove old git repo and init new ones**

```bash
cd /Users/charliec/Projects/skills-marketplace

# Remove old git history
rm -rf .git

# Init marketplace repo
cd skills-marketplace
git init
git add .
git commit -m "init: skills-marketplace repo (split from monorepo)"

# Init CLI repo
cd ../sm-cli
git init
git add .
git commit -m "init: sm-cli repo (split from monorepo)"
```

**Step 5: Verify directory structure**

```bash
cd /Users/charliec/Projects/skills-marketplace
ls -la skills-marketplace/
ls -la sm-cli/
```

Expected: `skills-marketplace/` has `.claude-plugin/`, `plugins/`, `CLAUDE.md`, `docs/`, `.claude/`, `.gitignore`. `sm-cli/` has `pyproject.toml`, `src/`, `tests/`, `.gitignore`.

---

### Task 2: Update CLAUDE.md for the marketplace repo

**Files:**
- Modify: `skills-marketplace/CLAUDE.md`

**Step 1: Update CLAUDE.md to reflect new structure**

Replace the full content of `skills-marketplace/CLAUDE.md` with:

```markdown
# charliec Skills Marketplace

Personal marketplace for managing Claude Code skills.

## Structure

```
/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace config with all available plugins
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin config (skills + commands registration)
│       ├── skills/
│       │   └── <skill-name>/
│       │       ├── SKILL.md  # Skill definition (required)
│       │       ├── scripts/  # Executable scripts
│       │       └── references/ # Reference documents
│       └── commands/
│           └── <skill-name>.md # Slash command
└── docs/                     # Documentation and design plans
```

## Version Management

- Skills use Git Tags (SemVer): `v1.0.0`, `v1.1.0`, `v2.0.0`
- Marketplace version bumps PATCH on any plugin add/update
- Three version sync points: git tag, plugin.json, marketplace.json

## CLI Tool

The `sm` CLI tool lives in a separate repository: `../sm-cli/`

```bash
sm init [--name <name>]       # Initialize new skill project
sm validate [path]            # Validate skill structure
sm publish [--version x.y.z]  # Publish skill to marketplace
sm update <skill-name>        # Pull latest version into marketplace
sm list                       # List all skills
sm status                     # Check for pending updates
```
```

**Step 2: Commit**

```bash
cd /Users/charliec/Projects/skills-marketplace/skills-marketplace
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for split repo structure"
```

---

### Task 3: Add CLAUDE.md to the sm-cli repo

**Files:**
- Create: `sm-cli/CLAUDE.md`

**Step 1: Create CLAUDE.md**

```markdown
# sm - Skills Marketplace CLI

CLI tool for managing Claude Code skills in the charliec Skills Marketplace.

## Structure

```
/
├── pyproject.toml              # UV-managed Python project
├── src/sm/
│   ├── main.py                 # Typer CLI entry point
│   ├── config.py               # Config management (~/.config/sm/config.json)
│   ├── git_utils.py            # Git operations (SHA, tags, status)
│   ├── validator.py            # Skill structure validation
│   ├── init_cmd.py             # sm init implementation
│   ├── publish_cmd.py          # sm publish implementation
│   └── update_cmd.py           # sm update implementation
└── tests/                      # pytest test suite
```

## Development

```bash
uv sync --group dev             # Install dependencies
uv run pytest -v                # Run tests
```

## Installation

```bash
uv tool install --editable .    # Install as global CLI tool
```
```

**Step 2: Commit**

```bash
cd /Users/charliec/Projects/skills-marketplace/sm-cli
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md for sm-cli repo"
```

---

### Task 4: Reinstall sm CLI with new path

**Step 1: Uninstall old sm**

```bash
uv tool uninstall sm
```

**Step 2: Reinstall from new location**

```bash
uv tool install --editable /Users/charliec/Projects/skills-marketplace/sm-cli
```

**Step 3: Verify installation**

```bash
which sm
sm --help
```

Expected: `/Users/charliec/.local/bin/sm` exists, `sm --help` shows all commands.

---

### Task 5: Update global config

**Files:**
- Modify: `~/.config/sm/config.json`

**Step 1: Update marketplacePath**

Change `~/.config/sm/config.json` from:
```json
{"marketplacePath": "/Users/charliec/Projects/skills-marketplace", "defaultAuthor": "charliec"}
```
To:
```json
{
  "marketplacePath": "/Users/charliec/Projects/skills-marketplace/skills-marketplace",
  "defaultAuthor": "charliec"
}
```

**Step 2: Verify sm commands work**

```bash
sm list
sm status
```

Expected: Both commands work without error (showing empty list since no plugins published yet).

---

### Task 6: Update operations-manual.md

**Files:**
- Modify: `skills-marketplace/docs/operations-manual.md`

Update the operations manual to reflect the new split structure. Key changes:

1. **Section 2 (安装与配置)**: Update CLI install path from `cli/` to `sm-cli/`
2. **Section 3 (项目结构)**: Show two-repo structure instead of monorepo
3. **Section 6 (日常操作流程)**: Update any paths referencing old structure
4. **Section 7 (配置文件格式说明)**: Update `marketplacePath` example
5. **Section 11 (开发与测试)**: Update dev setup paths
6. **Section 12 (速查表)**: Update file location table

**Step 1: Apply all path and structure updates**

(See detailed content in implementation)

**Step 2: Commit**

```bash
cd /Users/charliec/Projects/skills-marketplace/skills-marketplace
git add docs/operations-manual.md
git commit -m "docs: update operations manual for split repo structure"
```

---

### Task 7: Update Serena memories

Update Serena memory files to reflect the new project structure and paths.

---

### Task 8: Clean up parent directory

**Step 1: Remove any leftover files from parent**

```bash
cd /Users/charliec/Projects/skills-marketplace
# Check for any remaining files that should have been moved
ls -la
```

**Step 2: Verify both repos are clean**

```bash
cd /Users/charliec/Projects/skills-marketplace/skills-marketplace && git status
cd /Users/charliec/Projects/skills-marketplace/sm-cli && git status
```

Expected: Both repos show clean working tree.
