# NPM Package Distribution

Prism packages can be published to the **npm public registry** under the `@prism` scope, making them available to anyone via CDN without needing npm installed.

## Why npm?

✅ **Universal Access** — Anyone can install, no custom registries
✅ **CDN Distribution** — unpkg.com provides fast global delivery
✅ **Versioning** — Built-in semver support
✅ **Discovery** — Searchable on npmjs.com
✅ **No Dependencies** — Fetch packages without installing npm!

---

## Available Packages

All packages are published under the `@prism` scope:

- `@prism/personal-dev` — For freelancers & indie developers
- `@prism/startup` — For startups (10–50 people)
- `@prism/fortune500` — For large enterprises
- `@prism/university` — For universities
- `@prism/consulting-firm` — For consulting firms
- `@prism/opensource` — For open source projects
- `@prism/acme-corp` — Template for small companies

---

## For Users: Installing Prisms

### Method 1: Via Prism Installer (Recommended)

The Prism installer automatically fetches prisms from npm:

```bash
python3 install.py
# Select a prism from the list — automatically fetched from npm!

# Or specify directly:
python3 install.py --prism fortune500
```

### Method 2: Manual fetch

```bash
# List available prisms
python3 scripts/npm_package_fetcher.py list

# Fetch a specific prism
python3 scripts/npm_package_fetcher.py fetch @prism/personal-dev

# Fetch specific version
python3 scripts/npm_package_fetcher.py fetch @prism/startup --version 1.0.0
```

### Method 3: Direct npm install (if you have npm)

```bash
npm install @prism/personal-dev
```

### Method 4: Direct CDN access (no tools needed)

```bash
# Download package.yaml
curl https://unpkg.com/@prism/personal-dev@latest/package.yaml
```

---

## For Maintainers: Publishing Prisms

### Prerequisites

1. **npm account** — Create at [npmjs.com](https://www.npmjs.com/signup)
2. **@prism scope access** — Request access via GitHub issues
3. **npm CLI installed**:
   ```bash
   # Mac
   brew install node

   # Linux
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # Windows
   winget install OpenJS.NodeJS
   ```

### Login to npm

```bash
npm login
```

### Publish a prism

#### Test first (dry run)

```bash
python3 scripts/publish_packages.py --package personal-dev --dry-run
python3 scripts/publish_packages.py --all --dry-run
```

#### Publish

```bash
python3 scripts/publish_packages.py --package personal-dev
python3 scripts/publish_packages.py --all
```

### Manual publishing

```bash
cd prisms/personal-dev
npm publish --access public
```

---

## Updating Prisms

### 1. Update version

Edit `prisms/PRISM_NAME/package.yaml`:
```yaml
package:
  version: "1.1.0"   # increment version
```

### 2. Update changelog

Add notes in the prism's `README.md`.

### 3. Publish

```bash
python3 scripts/publish_packages.py --package PRISM_NAME
```

---

## Package Structure for npm

Each prism directory published to npm:

```
prisms/personal-dev/
├── package.json      # npm metadata (required for publishing)
├── package.yaml      # Prism manifest
├── README.md         # Prism documentation
├── base/             # Base sub-prism configs
├── profiles/         # Profile sub-prism configs (optional)
└── welcome.yaml      # Welcome content (optional)
```

### package.json example

```json
{
  "name": "@prism/personal-dev",
  "version": "1.0.0",
  "description": "Prism for freelancers and indie developers",
  "main": "package.yaml",
  "files": [
    "package.yaml",
    "base/",
    "profiles/",
    "welcome.yaml",
    "resources.yaml",
    "README.md"
  ],
  "keywords": ["prism", "dev-environment", "personal", "freelancer"],
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/andersonwilliam85/prism.git",
    "directory": "prisms/personal-dev"
  }
}
```

---

## How It Works

### For users

1. Prism installer starts — user selects a prism
2. Fetcher queries unpkg CDN for the prism's `package.yaml`
3. Downloads and caches the prism locally
4. Falls back to local `prisms/` directory if npm is unavailable
5. Engine merges selected sub-prisms and installs the environment

### For maintainers

1. Create or update the prism in `prisms/PRISM_NAME/`
2. Increment `package.yaml` version and `package.json` version
3. Test locally
4. Run publish script → automatically available via CDN

---

## unpkg CDN URLs

```
https://unpkg.com/@prism/PRISM-NAME@VERSION/FILE
```

Examples:
```bash
# Latest version
https://unpkg.com/@prism/personal-dev@latest/package.yaml

# Specific version
https://unpkg.com/@prism/startup@1.0.0/package.yaml

# Browse entire prism
https://unpkg.com/browse/@prism/fortune500@latest/
```

---

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0) — Breaking changes (restructured tiers, renamed fields)
- **MINOR** (1.0.0 → 1.1.0) — New sub-prisms or tiers added
- **PATCH** (1.0.0 → 1.0.1) — Bug fixes, typos, broken links

---

## Fallback Mechanism

```
1. Try unpkg CDN (fast, global)
   ↓ if fails
2. Try npm registry directly
   ↓ if fails
3. Use local prisms/ directory
   ↓ if fails
4. Show error with manual download instructions
```

Prism works even without internet access if you have the repo cloned locally.

---

## Troubleshooting

**"403 Forbidden" when publishing**
```bash
npm whoami    # check you're logged in
npm login     # login if needed
```

**"Package already exists"** — increment the version in `package.json` and `package.yaml`.

**"unpkg CDN unavailable"** — the installer automatically falls back to local prisms.

---

## Resources

- [Custom Registries](../user-guide/custom-registries.md) — private/air-gapped registry setup
- [Prism System](package-system.md) — system internals
- [GitHub Issues](https://github.com/andersonwilliam85/prism/issues) — report bugs
