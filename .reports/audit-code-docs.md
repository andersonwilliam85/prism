# Code vs. Documentation Audit
**Date:** 2026-03-05
**Status:** Done — superseded by roadmap.md for action items

---

## In Code, Not Documented

| Feature | Location | Gap |
|---|---|---|
| `install_full.py` | Root | Full interactive CLI with `--resume`, `--config`, `--status`. Not mentioned in any doc. |
| `scripts/config_validator.py` / `PackageConfigValidator` | Scripts | Used by `/api/validate-configs`. Neither class documented. |
| `scripts/npm_package_fetcher.py` CLI | Scripts | `list` / `fetch` subcommands with `--registry`/`--unpkg`. Not in quickstart. |
| `scripts/publish_packages.py` | Scripts | Publish prisms to npm. Nowhere in docs. |
| `scripts/auto-deploy-docs.py` | Scripts | Doc site generator. Referenced in Makefile only. |
| UI Settings panel | `install-ui.py:393` | Full drawer: source URL, npm registry, export/import JSON. Not in user guide. |
| Export/Import config JSON | `install-ui.py:1106` | Users can snapshot/restore wizard state. Not documented. |
| `.prism_installed` marker file | `installer_engine.py:495` | JSON record of completed install. Not referenced in docs. |
| `selected-sub-prisms.yaml` artifact | `installer_engine.py:490` | Saved alongside merged-config. No docs. |
| `install.py --status` | `install.py` | Shows install state. Exists, not documented. |
| `locales/en_US/ui.yaml` | `locales/` | i18n strings exist but wiring is Phase 2. |
| `bad-config-examples/` | Root | Useful for prism authors. Not linked from anywhere. |
| `prism_config.sources` | Validator checks it | Never acted on by engine. |

---

## Documented, Not (Fully) Implemented

| Feature | Where Documented | Reality |
|---|---|---|
| `setup.install.files` / `.directories` | Config schema | Engine does blanket `copytree`, never reads the directive. |
| `package.requires` (network, python version) | Config schema | Not validated or checked before install. |
| `prism_config.sources` (remote registry) | Schema + validator | Validated but never used for discovery or fetching. |
| `prism_config.unpkg_url` (inside prism) | Schema | Engine only reads `npm_registry`; `unpkg_url` requires env var. |
| `prism_config.branding` (logo, color, tagline) | Schema | Only `branding.name` is logged. UI ignores it. |
| `tools_selected` / `tools_excluded` | Merger rules | Merged correctly but engine only reads `tools_required`. |
| `onboarding_tasks` | Merger rules | Merged but never executed or shown. |
| `resources` | Merger rules + schema | Merged but not consumed. |
| `career` (user_only strategy) | Merger rules | Strategy implemented, never consumed. |
| Multi-select tiers | `config-inheritance.md` | UI renders single `<select>` per tier. No multi-select support. |
| i18n locale switching | `locales/README.md` | Scaffold exists, no extraction or switching logic. |
