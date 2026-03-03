# Skill Publishing & Version Management Design

## Overview

A personal Skills Marketplace for charliec to manage independently developed Claude Code skills. Each skill lives in its own Git repository under `/Users/charliec/Projects/`, and the marketplace serves as a registry with file snapshots (Approach B).

## 1. Marketplace Repository Structure

```
charliec-skills-marketplace/
├── .claude-plugin/
│   └── marketplace.json              # marketplace metadata + plugin index
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json           # plugin config (skills + commands registration)
│       ├── skills/
│       │   └── <skill-name>/
│       │       ├── SKILL.md           # Skill definition (required)
│       │       ├── scripts/           # Executable scripts
│       │       └── references/        # Reference documents
│       └── commands/
│           └── <skill-name>.md        # Slash command
├── cli/
│   ├── pyproject.toml                 # UV-managed Python project
│   └── sm.py                          # CLI entry point (sm = skills marketplace)
├── .claude/
│   └── settings.json
├── CLAUDE.md
└── README.md
```

### marketplace.json

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "charliec-skills",
  "version": "1.0.0",
  "description": "charliec personal Skills Marketplace",
  "owner": {
    "name": "charliec"
  },
  "plugins": [
    {
      "name": "my-skill",
      "description": "Skill description",
      "version": "1.0.0",
      "source": "./plugins/my-skill",
      "_meta": {
        "sourceRepo": "/Users/charliec/Projects/my-skill",
        "gitCommitSha": "abc123...",
        "publishedAt": "2026-03-03T12:00:00Z"
      }
    }
  ]
}
```

## 2. Version Management

### Skill Repository Versioning

Each skill project uses **Git Tags** as version identifiers, following Semantic Versioning (SemVer):

| Change Type | Version Bump | Example |
|------------|-------------|---------|
| SKILL.md wording, bug fixes | PATCH | 1.0.0 → 1.0.1 |
| New scripts, references, features | MINOR | 1.0.1 → 1.1.0 |
| SKILL.md rewrite, breaking changes | MAJOR | 1.1.0 → 2.0.0 |

### Marketplace Versioning

| Change Type | marketplace.json version |
|------------|------------------------|
| Add a new plugin | PATCH +1 |
| Any plugin version update | PATCH +1 |
| Marketplace structure change | MINOR +1 |

### Version Consistency Constraint

Three places must stay in sync (enforced by CLI):
1. Skill repo **git tag** (e.g., `v1.2.0`)
2. `plugins/<name>/.claude-plugin/plugin.json` → `version`
3. `marketplace.json` → corresponding plugin's `version`

## 3. CLI Tool: `sm`

Built with Python + Typer, managed by UV.

### Commands

```bash
sm init [--name <name>]       # Initialize a new skill project with standard structure
sm validate [path]            # Validate skill structure against spec
sm publish [--version x.y.z] [--message "msg"]  # Publish skill to marketplace
sm update <skill-name> [--version x.y.z]        # Pull latest version into marketplace
sm list                       # List all skills in marketplace
sm status                     # Check which skills have pending updates
```

### Configuration

`~/.config/sm/config.json`:
```json
{
  "marketplacePath": "/Users/charliec/Projects/skills-marketplace",
  "defaultAuthor": "charliec"
}
```

## 4. Publish Flow (`sm publish`)

```
Step 1  Detect current directory
        ├── Confirm SKILL.md exists
        └── Read .claude-plugin/plugin.json for skill name

Step 2  Validate skill structure
        ├── SKILL.md frontmatter valid?
        ├── plugin.json format correct?
        ├── commands/ has corresponding command file?
        └── Fail → print errors and exit

Step 3  Determine version
        ├── --version flag → use specified version
        ├── Current HEAD has tag → use that tag
        ├── Neither → prompt user for version
        └── Create git tag (e.g., v1.0.0) and push tag

Step 4  Check git status
        ├── Uncommitted changes → warn and ask to continue
        └── Pass → record current commit sha

Step 5  Copy files to marketplace
        ├── Target: marketplace/plugins/<skill-name>/
        ├── Directory exists → clean and re-copy (full replace)
        ├── Copy: SKILL.md, scripts/, references/, commands/, .claude-plugin/
        └── Exclude: .git/, .venv/, __pycache__, node_modules, .DS_Store

Step 6  Update marketplace metadata
        ├── Update plugins/<name>/.claude-plugin/plugin.json version
        ├── Update marketplace.json:
        │   ├── New skill → append to plugins array
        │   ├── Existing skill → update version + _meta
        │   └── Marketplace version PATCH +1
        └── Write _meta: sourceRepo, gitCommitSha, publishedAt

Step 7  Commit and push marketplace
        ├── git add plugins/<skill-name>/ .claude-plugin/marketplace.json
        ├── git commit -m "publish: <skill-name> v1.0.0"
        └── git push

Step 8  Output result
        └── ✓ Published <skill-name> v1.0.0 to charliec-skills marketplace
```

## 5. Update Flow (`sm update`)

```
Step 1  Execute in marketplace repo
Step 2  Find sourceRepo from marketplace.json _meta
Step 3  cd to source repo, git pull, get latest tag or HEAD
Step 4  Compare _meta.gitCommitSha with current HEAD
        ├── Same → "Already up to date" and exit
        └── Different → continue
Step 5  Execute publish steps 5-8
```

## 6. Error Handling

| Error | Handling |
|-------|---------|
| No SKILL.md in current dir | Error exit, suggest `sm init` |
| Invalid marketplace path | Error exit, suggest checking config.json |
| Uncommitted changes | Yellow warning, ask to continue |
| Duplicate version tag | Error exit, suggest new version |
| Marketplace push failure | Error but keep local commit, suggest manual push |

## 7. Skill Project Template (`sm init`)

Generated structure:

```
my-skill/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── my-skill/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── commands/
│   └── my-skill.md
├── .gitignore
└── README.md
```

## 8. Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| CLI framework | Typer | Lightweight, type-hint friendly |
| Package manager | UV | User preference |
| File operations | shutil + pathlib | Standard library |
| JSON operations | json (stdlib) | Sufficient |
| Git operations | subprocess calling git | Simple and reliable |
| YAML parsing | PyYAML | Parse SKILL.md frontmatter |
