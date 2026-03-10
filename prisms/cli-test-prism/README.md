# 💎 CLI Test Co Prism

**Version:** 1.0.0

Development environment prism for CLI Test Co.

## Installation

```bash
python3 install.py --prism cli-test-prism
# or via Web UI:
python3 install-ui.py
```

## Customization

Edit the files in this directory to customize for your company:

- `base/cli-test-prism.yaml` — Company-wide settings (applied to everyone)
- `teams/*.yaml` — Team-specific tool sets and repositories
- `welcome.yaml` — Customize the welcome page
- `resources.yaml` — Add your internal links and tools

## Validate

```bash
python3 scripts/package_manager.py validate cli-test-prism
```
