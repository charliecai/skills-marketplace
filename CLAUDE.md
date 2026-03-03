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
├── cli/                      # CLI tool (sm) for publish/update/list
└── docs/plans/               # Design and implementation plans
```

## Version Management

- Skills use Git Tags (SemVer): `v1.0.0`, `v1.1.0`, `v2.0.0`
- Marketplace version bumps PATCH on any plugin add/update
- Three version sync points: git tag, plugin.json, marketplace.json

## CLI Commands

```bash
sm init [--name <name>]       # Initialize new skill project
sm validate [path]            # Validate skill structure
sm publish [--version x.y.z]  # Publish skill to marketplace
sm update <skill-name>        # Pull latest version into marketplace
sm list                       # List all skills
sm status                     # Check for pending updates
```
