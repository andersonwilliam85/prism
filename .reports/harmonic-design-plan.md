# Prism — Harmonic Design Redesign

## Overview

Full Harmonic Design application to Prism: VBD (backend), EBD (frontend), BDT (testing). Each phase delivers a vertical slice across all three harmonics.

**Current state:** Two monoliths — `install-ui.py` (2409 lines, inline HTML/CSS/JS + Flask routes + API logic) and `installer_engine.py` (662 lines, Manager + Engine + Accessor mixed). Tests use `sys.path` hacks. No component boundaries. 15 VBD communication violations identified.

**Target state:** 5 Managers, 10 Engines, 9 Accessors, 4 Utilities. 7 UI Experiences decomposed into 17 Flows and 50+ Interactions. BDT test suite aligned to architectural tiers.

---

## Target Architecture

### VBD — Backend

```
prism/
├── managers/
│   ├── interfaces.py
│   ├── installation_manager.py           # Installation pipeline orchestrator
│   │   ├── IInstallationSequence         #   (low-vol: step order)
│   │   ├── IInstallationProgress         #   (med-vol: callback format)
│   │   └── IInstallationConfig           #   (med-vol: prism config loading)
│   ├── package_discovery_manager.py      # Package browsing + validation orchestrator
│   │   ├── IPackageQuery                 #   (low-vol: list/get)
│   │   └── IPackageValidation            #   (med-vol: schema rules)
│   ├── user_info_manager.py              # User info schema + collection orchestrator
│   │   ├── IUserInfoSchema               #   (med-vol: field definitions)
│   │   └── IUserInfoValidation           #   (med-vol: validation rules)
│   └── preflight_manager.py              # Environment prerequisite orchestrator
│       └── IPreflightValidation          #   (low-vol: check sequence)
│
├── engines/
│   ├── interfaces.py
│   ├── config_merge_engine.py            # from config_merger.py — merge strategies, deep merge
│   ├── validation_engine.py              # from package_validator.py — prism schema validation
│   ├── tool_resolution_engine.py         # tools_selected/excluded filtering, platform dispatch
│   ├── scaffold_engine.py               # from package_manager.create_package_scaffold()
│   ├── preflight_engine.py              # version comparison, requires checking
│   ├── git_config_engine.py             # merge git config from prism + user info
│   ├── workspace_engine.py              # determine folder hierarchy from config
│   ├── repo_clone_engine.py             # parse repo URLs, determine clone targets
│   ├── package_sourcing_engine.py       # resolve local vs remote prism source
│   └── user_info_validation_engine.py   # validate user values against field schema (NEW)
│
├── accessors/
│   ├── interfaces.py
│   ├── config_file_accessor.py           # YAML read/write (centralized)
│   ├── filesystem_accessor.py            # mkdir, copy, rmtree, exists, write
│   ├── git_command_accessor.py           # git config, clone, install
│   ├── ssh_key_accessor.py              # ssh-keygen, key file management
│   ├── platform_package_accessor.py      # brew/choco/apt command execution
│   ├── prism_package_accessor.py         # prism directory listing + discovery
│   ├── npm_registry_accessor.py          # HTTP fetch from npm/unpkg
│   ├── system_info_accessor.py           # platform detection, /etc/os-release
│   └── environment_accessor.py           # read/write environment variables (proxy, etc.)
│
├── utilities/
│   ├── progress_logger.py                # logging callback, progress tracking
│   ├── platform_detector.py              # OS/platform detection (pure logic)
│   ├── env_substitutor.py                # ${VAR} replacement in config values
│   └── locale_renderer.py               # i18n string lookup (future)
│
├── models/
│   ├── prism_config.py                   # PrismConfig, BrandingConfig, ThemeConfig
│   ├── installation_plan.py              # what will be installed (tools, repos, dirs)
│   ├── installation_result.py            # step outcomes, success/failure
│   ├── package_info.py                   # PackageInfo, TierInfo, UserField
│   └── user_info.py                      # UserInfo dataclass
│
├── ui/                                   # EBD structure
│   ├── server.py
│   ├── api/
│   ├── static/
│   └── templates/
│
├── cli/
│   ├── install.py
│   └── install_full.py
│
└── tests/                                # BDT structure
```

### Manager Detail

#### InstallationManager
**Orchestrates:** The 11-step installation pipeline.
**Receives (constructor):** All engines + accessors as interfaces.
**Facets:**
- `IInstallationSequence` (low-vol) — `install()` pipeline, step ordering
- `IInstallationProgress` (med-vol) — progress callback, log formatting
- `IInstallationConfig` (med-vol) — prism config loading, sub-prism merging

**Pipeline:**
```
1. preflight_engine.check(requirements)
2. prism_package_accessor.get(name) → raw config
3. config_merge_engine.merge(base, selected_tiers)
4. tool_resolution_engine.resolve(merged, selections)
5. platform_package_accessor.install(tool_list)
6. git_config_engine.prepare(user_info, merged) → git_command_accessor.apply()
7. ssh_key_accessor.generate_or_verify()
8. workspace_engine.plan(merged) → filesystem_accessor.create()
9. repo_clone_engine.plan(merged) → git_command_accessor.clone_all()
10. filesystem_accessor.apply_config(prism_files)
11. filesystem_accessor.write_marker(result)
```

#### PackageDiscoveryManager
**Orchestrates:** Package browsing, metadata, validation.
**Facets:**
- `IPackageQuery` (low-vol) — `list_packages()`, `get_info(name)`, `get_tiers(name)`, `get_user_fields(name)`
- `IPackageValidation` (med-vol) — `validate(name)`, `validate_all()`

**Delegates to:** `validation_engine`, `prism_package_accessor`, `config_file_accessor`

#### UserInfoManager
**Orchestrates:** Field schema retrieval + user input validation.
**Facets:**
- `IUserInfoSchema` (med-vol) — `get_fields(package)`, `get_defaults()`
- `IUserInfoValidation` (med-vol) — `validate(data, fields)`

**Delegates to:** `user_info_validation_engine`, `config_file_accessor`

**Why separate from Installation:** User info collection changes with UI/UX (high-vol). Installation pipeline is stable (low-vol). Different volatility = different managers.

#### PreflightManager
**Orchestrates:** Environment prerequisite checking.
**Facets:**
- `IPreflightValidation` (low-vol) — `check(requirements)` → pass/fail with details

**Delegates to:** `preflight_engine` (version comparison), `system_info_accessor` (tool checks)

**Why separate from Installation:** Preflight can run independently (UI preview: "is my machine ready?"). Installation depends on preflight but preflight doesn't depend on installation.

### Engine Detail

| Engine | Source | Responsibility | Volatility |
|--------|--------|---------------|------------|
| ConfigMergeEngine | `config_merger.py` | Deep merge strategies, level merging, array strategies | High (quarterly) |
| ValidationEngine | `package_validator.py` | Prism schema validation, field checks | Medium (quarterly) |
| ToolResolutionEngine | `installer_engine.py:472-511` | tools_selected/excluded filtering, platform dispatch logic | Medium |
| ScaffoldEngine | `package_manager.py:261-462` | Template generation for new prisms | Low |
| PreflightEngine | `installer_engine.py:267-350` | Version comparison, `_version_satisfies`, `_compare_versions` | Low |
| GitConfigEngine | `installer_engine.py:426-445` | Merge git config from prism + user info into config commands | Medium |
| WorkspaceEngine | `installer_engine.py:394-410` | Determine folder hierarchy from merged config | Low |
| RepoCloneEngine | `installer_engine.py:534-565` | Parse repo URLs (string or dict), determine clone targets | Low |
| PackageSourcingEngine | `npm_package_fetcher.py` + `install-ui.py:2334-2355` | Resolve local vs remote, determine fetch strategy | Medium |
| UserInfoValidationEngine | **NEW** (gap) | Validate user values against field constraints (email, required, pattern) | Medium |

### Accessor Detail

| Accessor | Source | I/O Type |
|----------|--------|----------|
| ConfigFileAccessor | Scattered YAML reads | YAML read/write |
| FilesystemAccessor | `installer_engine.py` step methods | mkdir, copy, rmtree, exists |
| GitCommandAccessor | `installer_engine.py` step methods | `git config`, `git clone` subprocess |
| SSHKeyAccessor | `installer_engine.py:447-461` | `ssh-keygen` subprocess, key file ops |
| PlatformPackageAccessor | `installer_engine.py:463-533` | `brew`/`choco`/`apt` subprocess |
| PrismPackageAccessor | `package_manager.py:40-99` | Prism dir listing, discovery |
| NPMRegistryAccessor | `npm_package_fetcher.py` | HTTP to npm/unpkg |
| SystemInfoAccessor | `installer_engine.py:194-210` | Platform detection, `/etc/os-release` |
| EnvironmentAccessor | `installer_engine.py:151-182` | `os.environ` read/write (proxy, etc.) |

### Communication Rules

```
cli/, ui/api/  →  managers/       (routes call managers only)
managers/      →  engines/        (direct sync)
managers/      →  accessors/      (direct sync)
engines/       →  accessors/      (reference data only — e.g., read config)
engines/       →  utilities/      (direct sync)
accessors/     →  utilities/      (direct sync)
utilities/     →  nothing         (leaf nodes)

FORBIDDEN:
engines/       →  engines/        (Manager composes instead)
accessors/     →  engines/        (return raw data)
accessors/     →  accessors/      (Manager fetches from both)
routes         →  engines/        (must go through Manager)
routes         →  accessors/      (must go through Manager)
```

### Current Violations (15 identified)

| # | Violation | Location | Fix |
|---|-----------|----------|-----|
| 1 | Route → Engine (skips Manager) | `/api/packages` calls `PrismValidator` | Route → PackageDiscoveryManager → ValidationEngine |
| 2 | Route does I/O directly | `/api/package/<name>/metadata` reads YAML | Route → PackageDiscoveryManager → ConfigFileAccessor |
| 3 | Route does I/O directly | `/api/package/<name>/tiers` reads YAML | Same as above |
| 4 | Route does I/O directly | `/api/package/<name>/user-fields` reads YAML | Route → UserInfoManager → ConfigFileAccessor |
| 5 | Manager contains Engine logic | `_version_satisfies()` in InstallationEngine | Extract to PreflightEngine |
| 6 | Manager does subprocess I/O | `step_install_package_manager()` | Manager → PlatformPackageAccessor |
| 7 | Manager does subprocess I/O | `step_install_git()` | Manager → GitCommandAccessor |
| 8 | Manager does subprocess I/O | `step_configure_git()` | GitConfigEngine + GitCommandAccessor |
| 9 | Manager does subprocess I/O | `step_generate_ssh_keys()` | Manager → SSHKeyAccessor |
| 10 | Manager does subprocess I/O | `step_install_tools()` | ToolResolutionEngine + PlatformPackageAccessor |
| 11 | Manager does subprocess I/O | `step_clone_repositories()` | RepoCloneEngine + GitCommandAccessor |
| 12 | Manager does filesystem I/O | `step_create_folder_structure()` | WorkspaceEngine + FilesystemAccessor |
| 13 | Manager does filesystem I/O | `step_apply_config_package()` | FilesystemAccessor |
| 14 | Manager reads YAML | `_load_prism_config()` | ConfigFileAccessor + ConfigMergeEngine |
| 15 | Manager writes env vars | `_apply_proxy_settings()` | EnvironmentAccessor |

---

## EBD — UI Decomposition

### Experiences (7 identified)

| # | Experience | User Goal | Scope | Entry Point |
|---|-----------|-----------|-------|-------------|
| 1 | **Web Installation** | Set up dev environment via browser | Steps 1-7 wizard | `http://localhost:5555` |
| 2 | **CLI Installation** | Set up dev environment via terminal | Platform detect → tools → git → SSH | `python3 install.py` |
| 3 | **Settings Configuration** | Customize installer (theme, registries) | Hamburger menu panel | Hamburger icon (top-left) |
| 4 | **Package Discovery** | Browse and understand available prisms | View metadata, validation, sources | Step 1 of wizard |
| 5 | **Configuration Validation** | Verify prism config before install | Trigger validation, view results | Step 5 button |
| 6 | **Error Recovery** | Understand and recover from failures | Invalid packages, API errors, install failures | Cross-cutting |
| 7 | **Progress Tracking** (CLI) | Monitor multi-step setup | View completed/pending tasks | `python3 install.py --status` |

### Flows (17 identified)

**Web Installation Experience:**
1. **Prism Selection Flow** — Step 1: load packages, display cards, select one
2. **User Info Flow** — Step 2: load dynamic fields from prism, render form, validate
3. **Tier Selection Flow** — Step 3: load bundled_prisms tiers, dropdown selectors, track selections
4. **Tools Selection Flow** — Step 4: checkbox grid, required tools pre-checked, optional selectable
5. **Summary & Validation Flow** — Step 5: display collected state, optional validation button, VPN warning
6. **Installation Progress Flow** — Step 6: spinner, real-time log, emoji progress markers
7. **Completion Flow** — Step 7: success message, next steps, links, close button

**Settings Experience:**
8. **Settings Prism Selection Flow** — Select prism from settings panel list
9. **Package Sources Flow** — Manage npm registry URL, unpkg URL, test connection
10. **Theme Selection Flow** — Grid of 5 themes, visual preview, apply
11. **Advanced Settings Flow** — Export/import config, reset, about

**Package Discovery Experience:**
12. **Package Browsing Flow** — Load packages, display valid/invalid split, show metadata
13. **Custom Registry Flow** — Expandable details, registry URLs, test connection button

**Configuration Validation Experience:**
14. **Validation Results Flow** — Button → loading → green (valid) / yellow (errors) / red (API fail)

**CLI Experience:**
15. **Interactive Install Flow** — Parse args → banner → prompts → engine → next steps
16. **Resume Flow** — `--resume` flag, load checkpoint, skip completed
17. **Status Query Flow** — `--status` flag, display completed/pending table

### Interactions (50+)

**Navigation:** `nextStep()`, `prevStep()`, `goToSettingsStep()`, progress bar update

**Package:** Click card → `selectPackage()`, border highlight, checkmark display, metadata fetch

**User Input:** Dynamic text/email inputs from schema, pattern validation, required indicators

**Tiers:** Dropdown per tier, option selection, deselection, `selectedSubPrisms` tracking

**Tools:** Checkbox per tool, required=disabled+checked, optional=clickable

**Registry:** npm URL input, unpkg URL input, `testRegistry()`, inline result feedback

**Settings Panel:** `toggleSettings()` hamburger open/close, overlay, tab navigation, `loadPrismsIntoSettings()`

**Theme:** Click card → `selectTheme()`, DOM data-theme update, localStorage persist

**Sources:** `addPrismSource()`, `removePrismSource()`, source list display

**Validation:** Click button → loading state → fetch → render results with collapsible errors

**Install:** `startInstall()` → collect form data → build payload → stream progress → auto-advance or error

**Config:** `exportPrismConfig()` download, `importPrismConfig()` file picker, `resetPrismConfig()` confirm+reset

**API Calls:** 7 fetch calls to Flask backend (packages, metadata, tiers, user-fields, config, validate, install)

### Target UI Structure

```
ui/
├── server.py                          # Flask app factory, static serving
├── api/
│   ├── packages.py                    # /api/packages, /api/package/<name>/*
│   └── install.py                     # /api/install
├── templates/
│   └── index.html                     # Shell HTML (loads CSS/JS externally)
├── static/
│   ├── css/
│   │   ├── base.css                   # Layout, typography, reset, wizard structure
│   │   ├── themes.css                 # 5 theme definitions (CSS variables)
│   │   ├── settings.css               # Settings panel styles
│   │   └── components.css             # Shared interaction styles
│   └── js/
│       ├── experiences/
│       │   ├── installation.js        # Web Installation Experience (wizard root)
│       │   ├── settings.js            # Settings Configuration Experience
│       │   └── discovery.js           # Package Discovery Experience
│       ├── flows/
│       │   ├── prism-selection.js     # Step 1: select prism
│       │   ├── user-info.js           # Step 2: collect user fields
│       │   ├── tier-selection.js      # Step 3: tier dropdowns
│       │   ├── tools-selection.js     # Step 4: tool checkboxes
│       │   ├── summary.js            # Step 5: review + validate
│       │   ├── install-progress.js    # Step 6: run + stream progress
│       │   ├── completion.js          # Step 7: success + next steps
│       │   ├── settings-sources.js    # Settings: package sources
│       │   ├── settings-theme.js      # Settings: theme picker
│       │   └── settings-advanced.js   # Settings: export/import/reset
│       ├── interactions/
│       │   ├── package-card.js        # Selectable package card
│       │   ├── tier-picker.js         # Tier dropdown group
│       │   ├── tool-checkbox.js       # Tool checkbox with required state
│       │   ├── dynamic-form.js        # Render form from field schema
│       │   ├── step-indicator.js      # Wizard progress bar
│       │   ├── progress-log.js        # Scrolling install log
│       │   ├── registry-tester.js     # Registry URL input + test button
│       │   ├── theme-card.js          # Theme preview card
│       │   ├── source-manager.js      # Add/remove prism sources
│       │   ├── config-exporter.js     # Export/import/reset config
│       │   └── validation-display.js  # Validation results (collapsible errors)
│       └── utils/
│           ├── api-client.js          # Fetch wrapper with error handling
│           ├── state.js               # Wizard state machine
│           ├── branding.js            # Apply prism_config.branding to DOM
│           ├── theme.js               # Theme engine (CSS var switching)
│           ├── storage.js             # localStorage persistence
│           └── validators.js          # Client-side field validation
```

---

## BDT — Test Structure

```
tests/
├── unit/
│   ├── engines/
│   │   ├── test_config_merge_engine.py       # merge strategies, edge cases
│   │   ├── test_validation_engine.py         # valid/invalid prisms, warnings
│   │   ├── test_tool_resolution_engine.py    # whitelist/blacklist filtering
│   │   ├── test_scaffold_engine.py           # template generation
│   │   ├── test_preflight_engine.py          # version comparison
│   │   ├── test_git_config_engine.py         # git config merging
│   │   ├── test_workspace_engine.py          # folder hierarchy logic
│   │   ├── test_repo_clone_engine.py         # URL parsing, target paths
│   │   ├── test_package_sourcing_engine.py   # local vs remote resolution
│   │   └── test_user_info_validation_engine.py  # field validation
│   ├── utilities/
│   │   ├── test_platform_detector.py
│   │   ├── test_env_substitutor.py
│   │   └── test_progress_logger.py
│   └── accessors/
│       ├── test_config_file_accessor.py      # YAML parsing logic
│       └── test_prism_package_accessor.py    # discovery logic
│
├── integration/
│   ├── managers/
│   │   ├── test_installation_manager.py      # real engines, mocked accessors
│   │   ├── test_package_discovery_manager.py # real engines, mocked accessors
│   │   └── test_user_info_manager.py         # real engine, mocked accessor
│   ├── accessors/
│   │   ├── test_filesystem_accessor.py       # real filesystem (temp dirs)
│   │   ├── test_git_command_accessor.py      # real git (temp repos)
│   │   ├── test_prism_package_accessor.py    # real prism dirs
│   │   └── test_config_file_accessor.py      # real YAML files
│   └── api/
│       ├── test_packages_api.py              # Flask test client
│       └── test_install_api.py               # Flask test client
│
└── e2e/
    ├── test_cli_installation.py              # subprocess CLI run
    └── test_web_installation.py              # full Flask + engine
```

### BDT Coverage Targets

| VBD Tier | Primary Test Level | What's Mocked | Target |
|----------|-------------------|---------------|--------|
| Engine (10) | Unit 80%+ | All interfaces | 90%+ |
| Manager (4) | Unit 70% + Integration | Engines+Accessors (unit), Accessors only (integration) | 85%+ |
| Accessor (9) | Unit 60% + Integration 70% | Nothing in unit (query logic); real I/O in integration | 80%+ |
| Utility (4) | Unit 70%+ | Nothing (pure functions) | 75%+ |
| UI API | Integration (Flask test client) | Managers mocked | 80%+ |
| UI Flows | E2E | Nothing mocked | Critical paths |

---

## Phasing

### Phase 1: Foundation (S)

**Goal:** Package structure, interfaces, utilities, models. No more `sys.path` hacks.

**VBD:**
- Create `prism/` package with subpackages: `managers/`, `engines/`, `accessors/`, `utilities/`, `models/`
- Define all interfaces: `managers/interfaces.py` (4 managers, 9 facets), `engines/interfaces.py` (10 engines), `accessors/interfaces.py` (9 accessors)
- Extract utilities: `PlatformDetector`, `ProgressLogger`, `EnvSubstitutor`
- Define models: `PrismConfig`, `BrandingConfig`, `PackageInfo`, `TierInfo`, `UserField`, `UserInfo`, `InstallationPlan`, `InstallationResult`

**BDT:**
- `requirements-dev.txt` with pytest
- `conftest.py` with shared fixtures
- Unit tests for all utilities
- Proper package imports (kill `sys.path.insert` hacks)

**Delivers:** Importable package, clean test infrastructure, all 28 interfaces defined.

---

### Phase 2: Accessors (M)

**Goal:** Extract all 9 accessors. After this, nothing above accessor layer touches external systems.

**VBD:**
- `ConfigFileAccessor` — centralize all YAML read/write (currently scattered across 5 files)
- `FilesystemAccessor` — mkdir, copy, rmtree, exists, write
- `GitCommandAccessor` — git config, clone, install (all subprocess)
- `SSHKeyAccessor` — ssh-keygen, key file management
- `PlatformPackageAccessor` — brew/choco/apt subprocess
- `PrismPackageAccessor` — prism directory listing, discovery, `_find_package()`
- `NPMRegistryAccessor` — HTTP to npm/unpkg (from `npm_package_fetcher.py`)
- `SystemInfoAccessor` — platform detection, `/etc/os-release`
- `EnvironmentAccessor` — `os.environ` read/write for proxy settings

**BDT:**
- Unit tests for query-building logic
- Integration tests with real I/O

---

### Phase 3: Engines (M)

**Goal:** Extract all 10 engines. Pure functions, no I/O.

**VBD:**
- `ConfigMergeEngine` — from `config_merger.py` (merge logic only)
- `ValidationEngine` — from `package_validator.py` (validation only)
- `ToolResolutionEngine` — from `installer_engine.py:472-511`
- `PreflightEngine` — from `installer_engine.py:267-350`
- `ScaffoldEngine` — from `package_manager.py:261-462`
- `GitConfigEngine` — from `installer_engine.py:426-445`
- `WorkspaceEngine` — from `installer_engine.py:394-410`
- `RepoCloneEngine` — from `installer_engine.py:534-565`
- `PackageSourcingEngine` — from `npm_package_fetcher.py` + `install-ui.py:2334-2355`
- `UserInfoValidationEngine` — **NEW**

**BDT:**
- Unit tests for every engine (80%+ target), all mock accessor interfaces

---

### Phase 4: Managers (M)

**Goal:** 4 thin managers composing engines + accessors. No logic in managers.

**VBD:**
- `InstallationManager` — 11-step pipeline (~50 lines)
- `PackageDiscoveryManager` — package listing, metadata, validation
- `UserInfoManager` — field schema retrieval, validation
- `PreflightManager` — environment checks

**BDT:**
- Unit tests: mock all, verify call sequencing
- Integration tests: real engines, mocked accessors

---

### Phase 5: UI Separation — EBD (L)

**Goal:** Extract 1915-line `INDEX_HTML`. 7 experiences, 17 flows, 11+ interactions.

**EBD:**
- Extract CSS: `base.css`, `themes.css`, `settings.css`, `components.css`
- Extract JS: 3 experiences, 10 flows, 11 interactions, 6 utilities
- Create `index.html` shell template

**VBD:**
- Flask app factory in `ui/server.py`
- Route blueprints in `ui/api/`
- Routes call managers only

**Approach:** CSS first → JS utils → interactions → flows → experiences. Test after each.

---

### Phase 6: Wire & Polish (S)

- Constructor injection, delete old files, `pyproject.toml`, full test pass, README

---

## Dependency Graph

```
Phase 1 (Foundation) → Phase 2 (Accessors) → Phase 3 (Engines) → Phase 4 (Managers) → Phase 5 (UI/EBD) → Phase 6 (Polish)
```

Linear critical path. Each phase = one PR.

---

## Volatility Map (Post-Refactor)

| Change Type | Components Touched | Bounded? |
|-------------|-------------------|----------|
| New platform (Windows PowerShell) | `PlatformPackageAccessor`, `PlatformDetector` | Yes (2) |
| New install step (Docker setup) | `InstallationManager` + new engine/accessor | Yes (3) |
| Merge rule change | `ConfigMergeEngine` only | Yes (1) |
| New prism schema field | `ValidationEngine` ± `ConfigMergeEngine` | Yes (1-2) |
| UI theme addition | `themes.css` only | Yes (1, no Python) |
| New wizard step | New Flow JS + `state.js` | Yes (2, no Python) |
| Tool filter logic | `ToolResolutionEngine` only | Yes (1) |
| New prism source | `NPMRegistryAccessor` + `PackageSourcingEngine` | Yes (2) |
| New user field type | `UserInfoValidationEngine` + `dynamic-form.js` | Yes (2) |
| i18n wiring | `LocaleRenderer` + JS interactions | Yes (bounded) |

Every change bounded to 1-3 components. No ripple effects.

---

## Backlog Decomposition

Replace BL-006 with:

| ID | Title | Phase | Estimate | Depends On |
|----|-------|-------|----------|------------|
| BL-006a | HD Foundation — package structure, 28 interfaces, utilities, models | 1 | S | — |
| BL-006b | HD Accessors — extract 9 I/O boundaries | 2 | M | BL-006a |
| BL-006c | HD Engines — extract 10 business logic components | 3 | M | BL-006b |
| BL-006d | HD Managers — 4 thin orchestrators with facets | 4 | M | BL-006c |
| BL-006e | HD UI/EBD — 7 experiences, 17 flows, 11 interactions | 5 | L | BL-006d |
| BL-006f | HD Wire & Polish — DI, cleanup, docs | 6 | S | BL-006e |

---

## Component Counts

| Tier | Count | Status |
|------|-------|--------|
| Managers | 4 (9 facets) | 0 extracted |
| Engines | 10 | 2 partially extracted (ConfigMerger, Validator) |
| Accessors | 9 | 0 extracted |
| Utilities | 4 | 0 extracted |
| Models | 5 | 0 defined |
| UI Experiences | 7 | 0 separated |
| UI Flows | 17 | 0 separated |
| UI Interactions | 11+ | 0 separated |
| UI Utilities | 6 | 0 separated |
| **Total components** | **~73** | |
