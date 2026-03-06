# Prism Roadmap
**Last updated:** 2026-03-05
**Status:** Active

---

## Priority Tiers

### P0 — Architecture (do before feature work)
These shape everything else. Do them first.

| # | Item | Plan | Status |
|---|---|---|---|
| 1 | VBD refactor: decompose `installer_engine.py` | `architecture-vbd-plan.md` | Planned |
| 2 | Docs restructure + local docs server | `docs-restructure-plan.md` | Planned |
| 3 | Split `install-ui.py`: Flask API + static templates | Part of VBD plan | Planned |

### P1 — Close gaps (documented but not implemented)
Fixes that make the schema contract real.

| # | Item | Effort | Status |
|---|---|---|---|
| 4 | Wire `setup.install.files`/`.directories` copy directives in engine | S | Backlog |
| 5 | Implement `package.requires` preflight checks | S | Backlog |
| 6 | Apply `prism_config.unpkg_url` from prism config (not just env var) | XS | Backlog |
| 7 | Consume `tools_selected`/`tools_excluded` in install step | S | Backlog |
| 8 | Show `onboarding_tasks` as "Next Steps" on completion screen | S | Backlog |
| 9 | Apply `prism_config.branding` (logo, color) to UI dynamically | M | Backlog |
| 10 | Multi-select tier support in UI | M | Backlog |

### P2 — i18n
| # | Item | Plan | Status |
|---|---|---|---|
| 11 | Extract UI strings to locale files | `i18n-plan.md` | Planned |
| 12 | Wire locale loader + language switcher | i18n plan | Planned |
| 13 | Initial translations: es, fr, de, ja, zh, pt, ko, ar | i18n plan | Planned |

### P3 — UX overhaul
| # | Item | Plan | Status |
|---|---|---|---|
| 14 | UX decomposition: Experiences > Flows > Interactions | `ux-decomposition.md` | Planned |
| 15 | Extract inline CSS/JS to component files | UX plan | Planned |
| 16 | Prism marketplace / discovery UI | UX plan | Planned |
| 17 | Live install streaming (SSE) | UX plan | Planned |

### P4 — New capability
| # | Item | Effort | Status |
|---|---|---|---|
| 18 | Remote prism registry via `prism_config.sources` | L | Backlog |
| 19 | Dry-run install mode | M | Backlog |
| 20 | Prism version pinning + `--update` flag | M | Backlog |
| 21 | Prism audit/compliance report | M | Backlog |
| 22 | GitHub/GitLab SSH key upload via API token | M | Backlog |
| 23 | Rollback / uninstall via `.prism_installed` | L | Backlog |
| 24 | Prism testing framework (`prism test` command) | L | Backlog |
| 25 | VS Code extension | XL | Backlog |

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-03-05 | Apply VBD before feature work | `installer_engine.py` is a monolith; adding more features will make it worse |
| 2026-03-05 | Use `.reports/` for planning docs | Keeps planning artifacts versioned alongside code without polluting user-facing docs |
| 2026-03-05 | i18n scaffold (`locales/`) already exists; wire it rather than redesign | Saves work, schema is sound |
