# Skills Marketplace CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool `sm` that manages publishing and versioning of Claude Code skills in a personal marketplace.

**Architecture:** Python CLI using Typer, organized as a single package under `cli/`. Each command (init, validate, publish, update, list, status) is a function in the main module. Git operations use subprocess. Config stored at `~/.config/sm/config.json`.

**Tech Stack:** Python 3.11+, Typer, PyYAML, UV (package manager)

---

### Task 1: Scaffold marketplace repo structure

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/.gitkeep`
- Create: `CLAUDE.md`

**Step 1: Create marketplace.json**

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "charliec-skills",
  "version": "1.0.0",
  "description": "charliec personal Skills Marketplace",
  "owner": {
    "name": "charliec"
  },
  "plugins": []
}
```

**Step 2: Create plugins directory with .gitkeep**

```bash
mkdir -p plugins
touch plugins/.gitkeep
```

**Step 3: Create CLAUDE.md**

Write a CLAUDE.md documenting this marketplace's structure and conventions (reference the design doc).

**Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json plugins/.gitkeep CLAUDE.md
git commit -m "feat: scaffold marketplace repo structure"
```

---

### Task 2: Scaffold CLI project with UV and Typer

**Files:**
- Create: `cli/pyproject.toml`
- Create: `cli/src/sm/__init__.py`
- Create: `cli/src/sm/main.py`

**Step 1: Initialize UV project**

```bash
cd cli
uv init --name sm --lib
```

**Step 2: Write pyproject.toml**

```toml
[project]
name = "sm"
version = "0.1.0"
description = "Skills Marketplace CLI"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.15.0",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.scripts]
sm = "sm.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Write main.py with app skeleton**

```python
import typer

app = typer.Typer(help="Skills Marketplace CLI - manage Claude Code skills")


@app.command()
def init(name: str = typer.Option(None, help="Skill name")):
    """Initialize a new skill project with standard structure."""
    typer.echo("TODO: init")


@app.command()
def validate(path: str = typer.Argument(".", help="Path to skill project")):
    """Validate skill structure against spec."""
    typer.echo("TODO: validate")


@app.command()
def publish(
    version: str = typer.Option(None, help="Version to publish"),
    message: str = typer.Option(None, "-m", help="Publish message"),
):
    """Publish skill to marketplace."""
    typer.echo("TODO: publish")


@app.command()
def update(
    skill_name: str = typer.Argument(..., help="Skill name to update"),
    version: str = typer.Option(None, help="Target version"),
):
    """Pull latest version of a skill into marketplace."""
    typer.echo("TODO: update")


@app.command()
def list():
    """List all skills in marketplace."""
    typer.echo("TODO: list")


@app.command()
def status():
    """Check which skills have pending updates."""
    typer.echo("TODO: status")


if __name__ == "__main__":
    app()
```

**Step 4: Install in editable mode and verify**

```bash
cd cli
uv pip install -e .
sm --help
```

Expected: Help output showing all 6 commands.

**Step 5: Commit**

```bash
git add cli/
git commit -m "feat: scaffold CLI project with Typer skeleton"
```

---

### Task 3: Implement config module

**Files:**
- Create: `cli/src/sm/config.py`
- Test: `cli/tests/test_config.py`

**Step 1: Write failing test**

```python
import json
import pytest
from pathlib import Path
from sm.config import load_config, save_config, DEFAULT_CONFIG_PATH


def test_load_config_creates_default(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr("sm.config.DEFAULT_CONFIG_PATH", config_path)
    config = load_config()
    assert config["marketplacePath"] == ""
    assert config["defaultAuthor"] == ""
    assert config_path.exists()


def test_load_config_reads_existing(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "marketplacePath": "/some/path",
        "defaultAuthor": "testuser"
    }))
    monkeypatch.setattr("sm.config.DEFAULT_CONFIG_PATH", config_path)
    config = load_config()
    assert config["marketplacePath"] == "/some/path"
    assert config["defaultAuthor"] == "testuser"


def test_save_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr("sm.config.DEFAULT_CONFIG_PATH", config_path)
    save_config({"marketplacePath": "/new/path", "defaultAuthor": "me"})
    data = json.loads(config_path.read_text())
    assert data["marketplacePath"] == "/new/path"
```

**Step 2: Run test to verify it fails**

```bash
cd cli && uv run pytest tests/test_config.py -v
```

Expected: FAIL (module not found)

**Step 3: Write implementation**

```python
import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "sm" / "config.json"

DEFAULT_CONFIG = {
    "marketplacePath": "",
    "defaultAuthor": "",
}


def load_config(config_path: Path = None) -> dict:
    path = config_path or DEFAULT_CONFIG_PATH
    if path.exists():
        return json.loads(path.read_text())
    config = DEFAULT_CONFIG.copy()
    save_config(config, path)
    return config


def save_config(config: dict, config_path: Path = None) -> None:
    path = config_path or DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n")
```

**Step 4: Run test to verify it passes**

```bash
cd cli && uv run pytest tests/test_config.py -v
```

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add cli/src/sm/config.py cli/tests/test_config.py
git commit -m "feat: add config module for CLI settings"
```

---

### Task 4: Implement validate command

**Files:**
- Create: `cli/src/sm/validator.py`
- Test: `cli/tests/test_validator.py`

**Step 1: Write failing tests**

```python
import pytest
from pathlib import Path
from sm.validator import validate_skill


def _create_valid_skill(base: Path, name: str = "test-skill"):
    """Helper to create a valid skill structure."""
    skill_dir = base / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill\n---\n\n# Test Skill\n"
    )
    plugin_dir = base / ".claude-plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text(
        '{"name":"test-skill","version":"0.1.0","skills":[{"name":"test-skill","path":"skills/test-skill"}],"commands":[{"name":"test-skill","path":"commands/test-skill.md"}]}'
    )
    cmd_dir = base / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "test-skill.md").write_text(
        "---\nname: test-skill\ndescription: Test\n---\nActivate test-skill.\n"
    )
    return base


def test_validate_valid_skill(tmp_path):
    _create_valid_skill(tmp_path)
    errors = validate_skill(tmp_path)
    assert errors == []


def test_validate_missing_skill_md(tmp_path):
    _create_valid_skill(tmp_path)
    (tmp_path / "skills" / "test-skill" / "SKILL.md").unlink()
    errors = validate_skill(tmp_path)
    assert any("SKILL.md" in e for e in errors)


def test_validate_missing_frontmatter(tmp_path):
    _create_valid_skill(tmp_path)
    (tmp_path / "skills" / "test-skill" / "SKILL.md").write_text("# No frontmatter\n")
    errors = validate_skill(tmp_path)
    assert any("frontmatter" in e.lower() or "name" in e.lower() for e in errors)


def test_validate_missing_plugin_json(tmp_path):
    _create_valid_skill(tmp_path)
    (tmp_path / ".claude-plugin" / "plugin.json").unlink()
    errors = validate_skill(tmp_path)
    assert any("plugin.json" in e for e in errors)


def test_validate_missing_command(tmp_path):
    _create_valid_skill(tmp_path)
    (tmp_path / "commands" / "test-skill.md").unlink()
    errors = validate_skill(tmp_path)
    assert any("command" in e.lower() for e in errors)
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_validator.py -v
```

Expected: FAIL (module not found)

**Step 3: Write implementation**

```python
import json
import yaml
from pathlib import Path


def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from SKILL.md content."""
    content = content.strip()
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def validate_skill(skill_path: Path) -> list[str]:
    """Validate a skill project structure. Returns list of error messages."""
    errors = []
    skill_path = Path(skill_path)

    # Check plugin.json
    plugin_json_path = skill_path / ".claude-plugin" / "plugin.json"
    if not plugin_json_path.exists():
        errors.append(f"Missing: .claude-plugin/plugin.json")
        return errors

    try:
        plugin_data = json.loads(plugin_json_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in plugin.json: {e}")
        return errors

    plugin_name = plugin_data.get("name", "")
    if not plugin_name:
        errors.append("plugin.json missing 'name' field")

    # Check skills defined in plugin.json
    skills = plugin_data.get("skills", [])
    for skill_def in skills:
        skill_rel_path = skill_def.get("path", "")
        skill_md_path = skill_path / skill_rel_path / "SKILL.md"
        if not skill_md_path.exists():
            errors.append(f"Missing: {skill_rel_path}/SKILL.md")
            continue

        # Validate frontmatter
        content = skill_md_path.read_text()
        fm = parse_frontmatter(content)
        if fm is None:
            errors.append(f"SKILL.md in {skill_rel_path} has no valid YAML frontmatter")
        elif not fm.get("name"):
            errors.append(f"SKILL.md in {skill_rel_path} frontmatter missing 'name'")
        elif not fm.get("description"):
            errors.append(f"SKILL.md in {skill_rel_path} frontmatter missing 'description'")

    # Check commands defined in plugin.json
    commands = plugin_data.get("commands", [])
    for cmd_def in commands:
        cmd_path = skill_path / cmd_def.get("path", "")
        if not cmd_path.exists():
            errors.append(f"Missing command file: {cmd_def.get('path', '?')}")

    return errors
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_validator.py -v
```

Expected: All 5 tests PASS

**Step 5: Wire validate command in main.py**

Update `main.py` to import and call `validate_skill`:

```python
@app.command()
def validate(path: str = typer.Argument(".", help="Path to skill project")):
    """Validate skill structure against spec."""
    from sm.validator import validate_skill
    errors = validate_skill(Path(path))
    if errors:
        for e in errors:
            typer.echo(f"  ✗ {e}", err=True)
        raise typer.Exit(1)
    typer.echo("✓ Skill structure is valid")
```

**Step 6: Commit**

```bash
git add cli/src/sm/validator.py cli/tests/test_validator.py cli/src/sm/main.py
git commit -m "feat: implement validate command with frontmatter and structure checks"
```

---

### Task 5: Implement init command

**Files:**
- Create: `cli/src/sm/init_cmd.py`
- Test: `cli/tests/test_init.py`

**Step 1: Write failing tests**

```python
import json
import pytest
from pathlib import Path
from sm.init_cmd import init_skill


def test_init_creates_structure(tmp_path):
    init_skill(tmp_path, "my-skill")
    assert (tmp_path / "skills" / "my-skill" / "SKILL.md").exists()
    assert (tmp_path / ".claude-plugin" / "plugin.json").exists()
    assert (tmp_path / "commands" / "my-skill.md").exists()
    assert (tmp_path / ".gitignore").exists()


def test_init_plugin_json_content(tmp_path):
    init_skill(tmp_path, "my-skill")
    data = json.loads((tmp_path / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "my-skill"
    assert data["version"] == "0.1.0"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["name"] == "my-skill"


def test_init_skill_md_has_frontmatter(tmp_path):
    init_skill(tmp_path, "my-skill")
    content = (tmp_path / "skills" / "my-skill" / "SKILL.md").read_text()
    assert "---" in content
    assert "name: my-skill" in content
    assert "description:" in content


def test_init_uses_dirname_as_default_name(tmp_path):
    skill_dir = tmp_path / "cool-tool"
    skill_dir.mkdir()
    init_skill(skill_dir, None)
    data = json.loads((skill_dir / ".claude-plugin" / "plugin.json").read_text())
    assert data["name"] == "cool-tool"
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_init.py -v
```

Expected: FAIL

**Step 3: Write implementation**

```python
import json
from pathlib import Path

SKILL_MD_TEMPLATE = """---
name: {name}
description: TODO - describe when this skill should be triggered
---

# {title}

TODO - write skill instructions here
"""

COMMAND_TEMPLATE = """---
name: {name}
description: TODO - describe this command
---

Activate the {name} skill and follow its instructions.
"""

PLUGIN_JSON_TEMPLATE = {
    "name": "",
    "version": "0.1.0",
    "description": "",
    "skills": [],
    "commands": [],
}

GITIGNORE_CONTENT = """.venv/
__pycache__/
*.pyc
.DS_Store
node_modules/
"""


def init_skill(base_path: Path, name: str | None) -> str:
    """Initialize a new skill project. Returns the skill name used."""
    if name is None:
        name = base_path.name

    title = name.replace("-", " ").title()

    # Create directories
    (base_path / "skills" / name).mkdir(parents=True, exist_ok=True)
    (base_path / "skills" / name / "scripts").mkdir(exist_ok=True)
    (base_path / "skills" / name / "references").mkdir(exist_ok=True)
    (base_path / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (base_path / "commands").mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    (base_path / "skills" / name / "SKILL.md").write_text(
        SKILL_MD_TEMPLATE.format(name=name, title=title)
    )

    # Write command
    (base_path / "commands" / f"{name}.md").write_text(
        COMMAND_TEMPLATE.format(name=name)
    )

    # Write plugin.json
    plugin_data = PLUGIN_JSON_TEMPLATE.copy()
    plugin_data["name"] = name
    plugin_data["skills"] = [{"name": name, "description": "", "path": f"skills/{name}"}]
    plugin_data["commands"] = [{"name": name, "description": "", "path": f"commands/{name}.md"}]
    (base_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_data, indent=2) + "\n"
    )

    # Write .gitignore
    (base_path / ".gitignore").write_text(GITIGNORE_CONTENT)

    return name
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_init.py -v
```

Expected: All 4 tests PASS

**Step 5: Wire init command in main.py**

```python
@app.command()
def init(name: str = typer.Option(None, help="Skill name (defaults to directory name)")):
    """Initialize a new skill project with standard structure."""
    from sm.init_cmd import init_skill
    used_name = init_skill(Path.cwd(), name)
    typer.echo(f"✓ Initialized skill project: {used_name}")
```

**Step 6: Commit**

```bash
git add cli/src/sm/init_cmd.py cli/tests/test_init.py cli/src/sm/main.py
git commit -m "feat: implement init command with skill project scaffolding"
```

---

### Task 6: Implement git helper utilities

**Files:**
- Create: `cli/src/sm/git_utils.py`
- Test: `cli/tests/test_git_utils.py`

**Step 1: Write failing tests**

```python
import subprocess
import pytest
from pathlib import Path
from sm.git_utils import get_head_sha, get_latest_tag, create_tag, has_uncommitted_changes


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repo with one commit."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    (tmp_path / "file.txt").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
    return tmp_path


def test_get_head_sha(git_repo):
    sha = get_head_sha(git_repo)
    assert len(sha) == 40


def test_get_latest_tag_none(git_repo):
    tag = get_latest_tag(git_repo)
    assert tag is None


def test_get_latest_tag_exists(git_repo):
    subprocess.run(["git", "tag", "v1.0.0"], cwd=git_repo, capture_output=True)
    tag = get_latest_tag(git_repo)
    assert tag == "v1.0.0"


def test_create_tag(git_repo):
    create_tag(git_repo, "v2.0.0")
    tag = get_latest_tag(git_repo)
    assert tag == "v2.0.0"


def test_has_uncommitted_changes_clean(git_repo):
    assert has_uncommitted_changes(git_repo) is False


def test_has_uncommitted_changes_dirty(git_repo):
    (git_repo / "new.txt").write_text("dirty")
    assert has_uncommitted_changes(git_repo) is True
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_git_utils.py -v
```

Expected: FAIL

**Step 3: Write implementation**

```python
import subprocess
from pathlib import Path


def _run_git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_head_sha(repo_path: Path) -> str:
    return _run_git(repo_path, "rev-parse", "HEAD")


def get_latest_tag(repo_path: Path) -> str | None:
    result = _run_git(repo_path, "describe", "--tags", "--abbrev=0")
    return result if result else None


def create_tag(repo_path: Path, tag: str) -> None:
    _run_git(repo_path, "tag", tag)


def has_uncommitted_changes(repo_path: Path) -> bool:
    status = _run_git(repo_path, "status", "--porcelain")
    return len(status) > 0
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_git_utils.py -v
```

Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add cli/src/sm/git_utils.py cli/tests/test_git_utils.py
git commit -m "feat: add git utility functions for tag and sha operations"
```

---

### Task 7: Implement publish command

**Files:**
- Create: `cli/src/sm/publish_cmd.py`
- Test: `cli/tests/test_publish.py`

**Step 1: Write failing tests**

```python
import json
import subprocess
import pytest
from pathlib import Path
from sm.publish_cmd import publish_skill


@pytest.fixture
def marketplace_repo(tmp_path):
    """Create a mock marketplace repo."""
    mp = tmp_path / "marketplace"
    mp.mkdir()
    (mp / ".claude-plugin").mkdir()
    (mp / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "test-marketplace",
        "version": "1.0.0",
        "plugins": []
    }, indent=2))
    (mp / "plugins").mkdir()
    subprocess.run(["git", "init"], cwd=mp, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=mp, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=mp, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=mp, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=mp, capture_output=True)
    return mp


@pytest.fixture
def skill_repo(tmp_path):
    """Create a valid skill repo."""
    sk = tmp_path / "my-skill"
    sk.mkdir()
    from sm.init_cmd import init_skill
    init_skill(sk, "my-skill")
    subprocess.run(["git", "init"], cwd=sk, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=sk, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=sk, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=sk, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=sk, capture_output=True)
    return sk


def test_publish_new_skill(skill_repo, marketplace_repo):
    result = publish_skill(skill_repo, marketplace_repo, version="1.0.0")
    assert result["success"] is True
    # Check files were copied
    assert (marketplace_repo / "plugins" / "my-skill" / "skills" / "my-skill" / "SKILL.md").exists()
    # Check marketplace.json updated
    mp_data = json.loads((marketplace_repo / ".claude-plugin" / "marketplace.json").read_text())
    assert len(mp_data["plugins"]) == 1
    assert mp_data["plugins"][0]["name"] == "my-skill"
    assert mp_data["plugins"][0]["version"] == "1.0.0"


def test_publish_updates_existing_skill(skill_repo, marketplace_repo):
    publish_skill(skill_repo, marketplace_repo, version="1.0.0")
    publish_skill(skill_repo, marketplace_repo, version="1.1.0")
    mp_data = json.loads((marketplace_repo / ".claude-plugin" / "marketplace.json").read_text())
    assert len(mp_data["plugins"]) == 1
    assert mp_data["plugins"][0]["version"] == "1.1.0"


def test_publish_creates_git_tag(skill_repo, marketplace_repo):
    publish_skill(skill_repo, marketplace_repo, version="1.0.0")
    from sm.git_utils import get_latest_tag
    assert get_latest_tag(skill_repo) == "v1.0.0"


def test_publish_records_meta(skill_repo, marketplace_repo):
    publish_skill(skill_repo, marketplace_repo, version="1.0.0")
    mp_data = json.loads((marketplace_repo / ".claude-plugin" / "marketplace.json").read_text())
    meta = mp_data["plugins"][0]["_meta"]
    assert meta["sourceRepo"] == str(skill_repo)
    assert len(meta["gitCommitSha"]) == 40
    assert "publishedAt" in meta
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_publish.py -v
```

Expected: FAIL

**Step 3: Write implementation**

```python
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from sm.git_utils import get_head_sha, get_latest_tag, create_tag
from sm.validator import validate_skill

EXCLUDE_PATTERNS = {".git", ".venv", "__pycache__", "node_modules", ".DS_Store", ".pytest_cache"}


def _copy_skill_files(src: Path, dest: Path) -> None:
    """Copy skill files excluding unwanted directories."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src, dest,
        ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS),
    )


def _bump_patch(version: str) -> str:
    """Bump the patch version: 1.0.0 -> 1.0.1"""
    parts = version.split(".")
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def publish_skill(
    skill_path: Path,
    marketplace_path: Path,
    version: str | None = None,
) -> dict:
    """Publish a skill to the marketplace. Returns a result dict."""
    # Validate
    errors = validate_skill(skill_path)
    if errors:
        return {"success": False, "errors": errors}

    # Read plugin.json for skill name
    plugin_data = json.loads(
        (skill_path / ".claude-plugin" / "plugin.json").read_text()
    )
    skill_name = plugin_data["name"]

    # Determine version
    if version is None:
        tag = get_latest_tag(skill_path)
        if tag:
            version = tag.lstrip("v")
        else:
            return {"success": False, "errors": ["No version specified and no git tag found"]}

    # Create git tag if not exists
    tag_name = f"v{version}"
    existing_tag = get_latest_tag(skill_path)
    if existing_tag != tag_name:
        create_tag(skill_path, tag_name)

    # Copy files
    dest = marketplace_path / "plugins" / skill_name
    _copy_skill_files(skill_path, dest)

    # Update plugin.json version in marketplace copy
    dest_plugin_json = dest / ".claude-plugin" / "plugin.json"
    dest_plugin_data = json.loads(dest_plugin_json.read_text())
    dest_plugin_data["version"] = version
    dest_plugin_json.write_text(json.dumps(dest_plugin_data, indent=2) + "\n")

    # Update marketplace.json
    mp_json_path = marketplace_path / ".claude-plugin" / "marketplace.json"
    mp_data = json.loads(mp_json_path.read_text())

    meta = {
        "sourceRepo": str(skill_path),
        "gitCommitSha": get_head_sha(skill_path),
        "publishedAt": datetime.now(timezone.utc).isoformat(),
    }

    plugin_entry = {
        "name": skill_name,
        "description": plugin_data.get("description", ""),
        "version": version,
        "source": f"./plugins/{skill_name}",
        "_meta": meta,
    }

    # Update or append
    found = False
    for i, p in enumerate(mp_data["plugins"]):
        if p["name"] == skill_name:
            mp_data["plugins"][i] = plugin_entry
            found = True
            break
    if not found:
        mp_data["plugins"].append(plugin_entry)

    # Bump marketplace version
    mp_data["version"] = _bump_patch(mp_data["version"])

    mp_json_path.write_text(json.dumps(mp_data, indent=2) + "\n")

    return {"success": True, "name": skill_name, "version": version}
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_publish.py -v
```

Expected: All 4 tests PASS

**Step 5: Wire publish command in main.py**

```python
@app.command()
def publish(
    version: str = typer.Option(None, help="Version to publish"),
    message: str = typer.Option(None, "-m", help="Publish message"),
):
    """Publish skill to marketplace."""
    from sm.config import load_config
    from sm.publish_cmd import publish_skill
    from sm.git_utils import has_uncommitted_changes

    config = load_config()
    if not config["marketplacePath"]:
        typer.echo("✗ marketplacePath not configured. Run: sm config", err=True)
        raise typer.Exit(1)

    skill_path = Path.cwd()
    marketplace_path = Path(config["marketplacePath"])

    if has_uncommitted_changes(skill_path):
        if not typer.confirm("⚠ Uncommitted changes detected. Continue?"):
            raise typer.Abort()

    result = publish_skill(skill_path, marketplace_path, version)
    if not result["success"]:
        for e in result["errors"]:
            typer.echo(f"  ✗ {e}", err=True)
        raise typer.Exit(1)

    typer.echo(f"✓ Published {result['name']} v{result['version']} to marketplace")
```

**Step 6: Commit**

```bash
git add cli/src/sm/publish_cmd.py cli/tests/test_publish.py cli/src/sm/main.py
git commit -m "feat: implement publish command with file copy and metadata update"
```

---

### Task 8: Implement list and status commands

**Files:**
- Modify: `cli/src/sm/main.py`
- Test: `cli/tests/test_list_status.py`

**Step 1: Write failing tests**

```python
import json
import pytest
from pathlib import Path
from sm.main import _load_marketplace_data, _check_skill_status


def test_load_marketplace_data(tmp_path):
    mp = tmp_path / ".claude-plugin"
    mp.mkdir()
    (mp / "marketplace.json").write_text(json.dumps({
        "name": "test",
        "version": "1.0.0",
        "plugins": [
            {"name": "skill-a", "version": "1.0.0", "source": "./plugins/skill-a",
             "_meta": {"sourceRepo": "/tmp/a", "gitCommitSha": "abc123"}}
        ]
    }))
    data = _load_marketplace_data(tmp_path)
    assert len(data["plugins"]) == 1
    assert data["plugins"][0]["name"] == "skill-a"
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_list_status.py -v
```

Expected: FAIL

**Step 3: Implement list and status in main.py**

Add helper function `_load_marketplace_data` and update `list` and `status` commands:

```python
def _load_marketplace_data(marketplace_path: Path) -> dict:
    mp_json = marketplace_path / ".claude-plugin" / "marketplace.json"
    return json.loads(mp_json.read_text())


@app.command("list")
def list_skills():
    """List all skills in marketplace."""
    from sm.config import load_config
    config = load_config()
    mp_path = Path(config["marketplacePath"])
    data = _load_marketplace_data(mp_path)

    if not data["plugins"]:
        typer.echo("No skills published yet.")
        return

    typer.echo(f"{'NAME':<25} {'VERSION':<12} {'SOURCE'}")
    typer.echo("-" * 70)
    for p in data["plugins"]:
        source = p.get("_meta", {}).get("sourceRepo", "?")
        typer.echo(f"{p['name']:<25} {p['version']:<12} {source}")


@app.command()
def status():
    """Check which skills have pending updates."""
    from sm.config import load_config
    from sm.git_utils import get_head_sha
    config = load_config()
    mp_path = Path(config["marketplacePath"])
    data = _load_marketplace_data(mp_path)

    if not data["plugins"]:
        typer.echo("No skills published yet.")
        return

    for p in data["plugins"]:
        meta = p.get("_meta", {})
        source_repo = meta.get("sourceRepo", "")
        recorded_sha = meta.get("gitCommitSha", "")
        source_path = Path(source_repo)

        if not source_path.exists():
            typer.echo(f"  ? {p['name']:<20} {p['version']:<10} source not found")
            continue

        current_sha = get_head_sha(source_path)
        if current_sha == recorded_sha:
            typer.echo(f"  ✓ {p['name']:<20} {p['version']:<10} up to date")
        else:
            typer.echo(f"  ⚠ {p['name']:<20} {p['version']:<10} has unpublished changes")
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_list_status.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add cli/src/sm/main.py cli/tests/test_list_status.py
git commit -m "feat: implement list and status commands"
```

---

### Task 9: Implement update command

**Files:**
- Create: `cli/src/sm/update_cmd.py`
- Test: `cli/tests/test_update.py`

**Step 1: Write failing tests**

```python
import json
import subprocess
import pytest
from pathlib import Path
from sm.publish_cmd import publish_skill
from sm.update_cmd import update_skill
from sm.init_cmd import init_skill


@pytest.fixture
def setup(tmp_path):
    """Create skill repo + marketplace, publish v1.0.0, then modify skill."""
    # Skill repo
    sk = tmp_path / "my-skill"
    sk.mkdir()
    init_skill(sk, "my-skill")
    subprocess.run(["git", "init"], cwd=sk, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=sk, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=sk, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=sk, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=sk, capture_output=True)

    # Marketplace
    mp = tmp_path / "marketplace"
    mp.mkdir()
    (mp / ".claude-plugin").mkdir()
    (mp / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "test", "version": "1.0.0", "plugins": []
    }))
    (mp / "plugins").mkdir()
    subprocess.run(["git", "init"], cwd=mp, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=mp, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=mp, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=mp, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=mp, capture_output=True)

    # Publish v1.0.0
    publish_skill(sk, mp, "1.0.0")

    # Make a change in skill repo
    (sk / "skills" / "my-skill" / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: Updated\n---\n# Updated\n"
    )
    subprocess.run(["git", "add", "."], cwd=sk, capture_output=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=sk, capture_output=True)

    return {"skill": sk, "marketplace": mp}


def test_update_detects_changes(setup):
    result = update_skill("my-skill", setup["marketplace"], version="1.1.0")
    assert result["success"] is True
    assert result["version"] == "1.1.0"


def test_update_copies_new_content(setup):
    update_skill("my-skill", setup["marketplace"], version="1.1.0")
    content = (setup["marketplace"] / "plugins" / "my-skill" / "skills" / "my-skill" / "SKILL.md").read_text()
    assert "Updated" in content


def test_update_already_up_to_date(setup):
    update_skill("my-skill", setup["marketplace"], version="1.1.0")
    result = update_skill("my-skill", setup["marketplace"])
    assert result["success"] is True
    assert result.get("skipped") is True
```

**Step 2: Run tests to verify they fail**

```bash
cd cli && uv run pytest tests/test_update.py -v
```

Expected: FAIL

**Step 3: Write implementation**

```python
import json
from pathlib import Path

from sm.git_utils import get_head_sha
from sm.publish_cmd import publish_skill


def update_skill(
    skill_name: str,
    marketplace_path: Path,
    version: str | None = None,
) -> dict:
    """Update a skill in the marketplace from its source repo."""
    mp_json_path = marketplace_path / ".claude-plugin" / "marketplace.json"
    mp_data = json.loads(mp_json_path.read_text())

    # Find the skill
    plugin = None
    for p in mp_data["plugins"]:
        if p["name"] == skill_name:
            plugin = p
            break

    if plugin is None:
        return {"success": False, "errors": [f"Skill '{skill_name}' not found in marketplace"]}

    source_repo = Path(plugin["_meta"]["sourceRepo"])
    if not source_repo.exists():
        return {"success": False, "errors": [f"Source repo not found: {source_repo}"]}

    # Check if update needed
    recorded_sha = plugin["_meta"]["gitCommitSha"]
    current_sha = get_head_sha(source_repo)

    if recorded_sha == current_sha and version is None:
        return {"success": True, "skipped": True, "name": skill_name, "version": plugin["version"]}

    # Re-publish
    return publish_skill(source_repo, marketplace_path, version)
```

**Step 4: Run tests to verify they pass**

```bash
cd cli && uv run pytest tests/test_update.py -v
```

Expected: All 3 tests PASS

**Step 5: Wire update command in main.py**

```python
@app.command()
def update(
    skill_name: str = typer.Argument(..., help="Skill name to update"),
    version: str = typer.Option(None, help="Target version"),
):
    """Pull latest version of a skill into marketplace."""
    from sm.config import load_config
    from sm.update_cmd import update_skill
    config = load_config()
    mp_path = Path(config["marketplacePath"])
    result = update_skill(skill_name, mp_path, version)
    if not result["success"]:
        for e in result["errors"]:
            typer.echo(f"  ✗ {e}", err=True)
        raise typer.Exit(1)
    if result.get("skipped"):
        typer.echo(f"✓ {skill_name} is already up to date")
    else:
        typer.echo(f"✓ Updated {result['name']} to v{result['version']}")
```

**Step 6: Commit**

```bash
git add cli/src/sm/update_cmd.py cli/tests/test_update.py cli/src/sm/main.py
git commit -m "feat: implement update command"
```

---

### Task 10: Integration test — end-to-end workflow

**Files:**
- Create: `cli/tests/test_e2e.py`

**Step 1: Write end-to-end test**

```python
import json
import subprocess
import pytest
from pathlib import Path
from sm.init_cmd import init_skill
from sm.validator import validate_skill
from sm.publish_cmd import publish_skill
from sm.update_cmd import update_skill


def _git_init(path):
    subprocess.run(["git", "init"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, capture_output=True)


def _create_marketplace(tmp_path):
    mp = tmp_path / "marketplace"
    mp.mkdir()
    (mp / ".claude-plugin").mkdir()
    (mp / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "test", "version": "1.0.0", "plugins": []
    }))
    (mp / "plugins").mkdir()
    _git_init(mp)
    return mp


def test_full_lifecycle(tmp_path):
    """Test: init → validate → publish → modify → update"""
    mp = _create_marketplace(tmp_path)

    # 1. Init a new skill
    sk = tmp_path / "cool-skill"
    sk.mkdir()
    name = init_skill(sk, "cool-skill")
    assert name == "cool-skill"

    # 2. Validate
    errors = validate_skill(sk)
    assert errors == []

    # 3. Git init and publish
    _git_init(sk)
    result = publish_skill(sk, mp, "1.0.0")
    assert result["success"] is True
    assert (mp / "plugins" / "cool-skill" / "skills" / "cool-skill" / "SKILL.md").exists()

    # 4. Modify skill
    (sk / "skills" / "cool-skill" / "SKILL.md").write_text(
        "---\nname: cool-skill\ndescription: Now with more cool\n---\n# V2\n"
    )
    subprocess.run(["git", "add", "."], cwd=sk, capture_output=True)
    subprocess.run(["git", "commit", "-m", "v2"], cwd=sk, capture_output=True)

    # 5. Update
    result = update_skill("cool-skill", mp, "1.1.0")
    assert result["success"] is True
    assert result["version"] == "1.1.0"

    # Verify final state
    mp_data = json.loads((mp / ".claude-plugin" / "marketplace.json").read_text())
    assert len(mp_data["plugins"]) == 1
    assert mp_data["plugins"][0]["version"] == "1.1.0"
    content = (mp / "plugins" / "cool-skill" / "skills" / "cool-skill" / "SKILL.md").read_text()
    assert "V2" in content
```

**Step 2: Run the test**

```bash
cd cli && uv run pytest tests/test_e2e.py -v
```

Expected: PASS

**Step 3: Run all tests**

```bash
cd cli && uv run pytest -v
```

Expected: All tests PASS

**Step 4: Commit**

```bash
git add cli/tests/test_e2e.py
git commit -m "test: add end-to-end lifecycle test"
```

---

### Task 11: Final wiring — install CLI globally and verify

**Step 1: Install with UV**

```bash
cd /Users/charliec/Projects/skills-marketplace/cli
uv pip install -e .
```

**Step 2: Set up config**

```bash
mkdir -p ~/.config/sm
echo '{"marketplacePath": "/Users/charliec/Projects/skills-marketplace", "defaultAuthor": "charliec"}' > ~/.config/sm/config.json
```

**Step 3: Verify all commands work**

```bash
sm --help
sm list
sm status
```

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete skills marketplace CLI v0.1.0"
```
