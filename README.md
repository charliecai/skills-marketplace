# Charliec's Skills Marketplace

## Skills

| Skill | 描述 | 版本 |
|-------|------|------|
| `pm-prd` | 产品经理 PRD 助手，支持方案讨论、PRD 创作/修改、文档评审、可交互 Demo 生成五种模式。 | 0.1.0 |

## 安装

### Claude Code

```bash
claude plugin marketplace add https://github.com/charliec/skills-marketplace
claude plugin install charliec-skills
```

### 手动安装

```bash
git clone https://github.com/charliec/skills-marketplace.git ~/.claude/charliec-skills
```

在 Claude Code 设置中将 skills 路径指向 `~/.claude/charliec-skills/skills/`。

## 项目结构

```
skills-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # 注册表
└── skills/                       # 所有已发布的 skill（扁平结构）
    └── <skill-name>/
        ├── SKILL.md              # Skill 定义（必需）
        ├── scripts/              # 可执行脚本（可选）
        ├── references/           # 参考文档（可选）
        └── ...
```

## License

MIT
