---
layout: default
title: Publishing Prisms
---

# Publishing Prisms

This guide covers packaging and publishing a validated prism to npm so other teams can install it without cloning the repository.

---

## Prerequisites

- npm account with publish access to your org scope (e.g., `@mycompany`)
- A valid, locally-tested prism in `prisms/<name>/`
- `package.json` present at the prism root

---

## 1. Validate First

Always run the validator before publishing. A broken prism on npm is harder to fix than a broken local one.

```bash
python3 scripts/package_validator.py prisms/my-company
```

Fix all errors before proceeding. Warnings are acceptable but should be reviewed.

---

## 2. Prepare `package.json`

Each prism needs a `package.json` alongside its `package.yaml`:

```json
{
  "name": "@mycompany/my-company",
  "version": "1.0.0",
  "description": "My Company developer environment prism",
  "main": "package.yaml",
  "files": [
    "package.yaml",
    "base/",
    "teams/",
    "roles/",
    "docs/"
  ],
  "keywords": ["prism", "devenv", "mycompany"],
  "license": "MIT"
}
```

The `files` list controls what gets published to the npm registry. Include all sub-prism directories and any prism-level documentation.

---

## 3. Dry Run

Preview exactly what will be published without actually publishing:

```bash
python3 scripts/publish_packages.py --package my-company --dry-run
```

This runs `npm pack` internally and lists all files that would be included. Verify the output looks correct before proceeding.

---

## 4. Publish

```bash
python3 scripts/publish_packages.py --package my-company
```

To publish all packages at once:

```bash
python3 scripts/publish_packages.py --all
```

The script wraps `npm publish` and handles the registry URL from `prism_config.npm_registry` if set.

---

## 5. Versioning

Follow semantic versioning:

| Change type | Version bump |
|---|---|
| New optional tier, new tool | Patch (`1.0.x`) |
| New required tier, changed merge behavior | Minor (`1.x.0`) |
| Breaking schema change, renamed tiers | Major (`x.0.0`) |

Bump the version in `package.json` before publishing. Tag the release in git:

```bash
git tag v1.0.0
git push --tags
```

---

## 6. Installing from npm

Once published, users can install from any Prism instance pointed at your registry:

```bash
python3 install.py --prism @mycompany/my-company
```

Or select it from the web UI's prism list if `prism_config.sources` includes your registry.

---

## Private Registries

If your prism is internal-only, publish to a private registry and configure installers to use it:

```yaml
# package.yaml
prism_config:
  npm_registry: "https://npm.mycompany.com"
```

See [Custom Registries](../user-guide/custom-registries.md) for the full setup guide.

---

## See Also

- [Creating Configurations](../user-guide/creating-configurations.md) — Author a prism from scratch
- [Bad Config Examples](../reference/bad-config-examples.md) — Common validator errors
- [Configuration Schema](../reference/configuration-schema.md) — Full `package.yaml` reference
- `scripts/publish_packages.py` — Publish script implementation
