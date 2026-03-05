# NPM Package Distribution

Prism config packages are published to the **npm public registry** under the `@prism` scope.

## Why npm?

✅ **Universal Access** - Anyone can install, no custom registries  
✅ **CDN Distribution** - unpkg.com provides fast global delivery  
✅ **Versioning** - Built-in semver support  
✅ **Discovery** - Searchable on npmjs.com  
✅ **Trust** - npm's security and infrastructure  
✅ **No Dependencies** - Fetch packages without installing npm!

---

## Available Packages

All packages are published under the `@prism` scope:

- `@prism/personal-dev-config` - For freelancers & indie developers
- `@prism/startup-config` - For startups
- `@prism/fortune500-config` - For large enterprises
- `@prism/university-config` - For universities
- `@prism/consulting-config` - For consulting firms
- `@prism/opensource-config` - For open source projects
- `@prism/acme-corp-config` - Template for companies

---

## For Users: Installing Packages

### Method 1: Via Prism Installer (Recommended)

The Prism installer automatically fetches packages from npm:

```bash
python3 install.py
# Select package from the list - automatically fetched from npm!
```

### Method 2: Manual Fetch

```bash
# List available packages
python3 scripts/npm_package_fetcher.py list

# Fetch a specific package
python3 scripts/npm_package_fetcher.py fetch @prism/personal-dev-config

# Fetch specific version
python3 scripts/npm_package_fetcher.py fetch @prism/startup-config --version 1.0.0
```

### Method 3: Direct npm Install (if you have npm)

```bash
npm install @prism/personal-dev-config
```

### Method 4: Direct CDN Access (no tools needed!)

Fetch package files directly from unpkg CDN:

```bash
# Download package.yaml
curl https://unpkg.com/@prism/personal-dev-config@latest/package.yaml

# Download entire package as tarball
curl https://unpkg.com/@prism/personal-dev-config@latest/ > package.tgz
```

---

## For Maintainers: Publishing Packages

### Prerequisites

1. **npm account** - Create at [npmjs.com](https://www.npmjs.com/signup)
2. **@prism scope access** - Contact Will Anderson for access
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
# Enter your npm credentials
```

### Publish a Package

#### Test First (Dry Run)

```bash
# Test single package
python3 scripts/publish_packages.py --package personal-dev --dry-run

# Test all packages
python3 scripts/publish_packages.py --all --dry-run
```

#### Publish for Real

```bash
# Publish single package
python3 scripts/publish_packages.py --package personal-dev

# Publish all packages
python3 scripts/publish_packages.py --all
```

### Manual Publishing (if you prefer)

```bash
cd config-packages/personal-dev
npm publish --access public
```

---

## Updating Packages

### 1. Update Version

Edit `config-packages/PACKAGE_NAME/package.json`:

```json
{
  "version": "1.1.0"  // Increment version
}
```

### 2. Update Changelog

Add notes in `CHANGELOG.md` or package README

### 3. Publish

```bash
python3 scripts/publish_packages.py --package PACKAGE_NAME
```

---

## Package Structure

Each package directory should contain:

```
config-packages/personal-dev/
├── package.json      # npm metadata
├── package.yaml      # Prism config
├── README.md         # Package documentation
├── config/           # Config files
├── profiles/         # User profiles (optional)
└── assets/           # Logo, colors, etc. (optional)
```

### package.json Example

```json
{
  "name": "@prism/personal-dev-config",
  "version": "1.0.0",
  "description": "Prism config for freelancers and indie developers",
  "main": "package.yaml",
  "files": [
    "package.yaml",
    "config/",
    "profiles/",
    "assets/",
    "README.md"
  ],
  "keywords": [
    "prism",
    "config",
    "dev-environment",
    "personal",
    "freelancer"
  ],
  "author": "Will Anderson <andersonwilliam85@gmail.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/andersonwilliam85/prism.git",
    "directory": "config-packages/personal-dev"
  },
  "homepage": "https://github.com/andersonwilliam85/prism#readme"
}
```

---

## How It Works

### For Users:

1. **Prism installer starts** - User selects a package
2. **Fetcher checks npm** - Queries unpkg CDN for package
3. **Downloads package.yaml** - Fetches config from CDN
4. **Falls back to local** - If npm unavailable, uses local copy
5. **Applies config** - Installs tools, sets up environment

### For Maintainers:

1. **Create/update package** - Edit config files
2. **Update package.json** - Increment version
3. **Test locally** - Use local copy for testing
4. **Publish to npm** - Run publish script
5. **Users get updates** - Automatically available via CDN

---

## unpkg CDN URLs

All published packages are available via unpkg:

```
https://unpkg.com/@prism/PACKAGE-NAME@VERSION/FILE
```

### Examples:

```bash
# Latest version, specific file
https://unpkg.com/@prism/personal-dev-config@latest/package.yaml

# Specific version
https://unpkg.com/@prism/startup-config@1.0.0/package.yaml

# Browse entire package
https://unpkg.com/browse/@prism/fortune500-config@latest/

# Get package.json metadata
https://unpkg.com/@prism/university-config@latest/package.json
```

---
## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to package format
- **MINOR** (1.0.0 → 1.1.0): New features, new tools added
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, documentation updates

---

## Fallback Mechanism

Prism installer has robust fallback:

```
1. Try unpkg CDN (fast, global)
   ↓ if fails
2. Try npm registry directly
   ↓ if fails
3. Use local config-packages/ directory
   ↓ if fails
4. Show error, offer to download manually
```

This ensures **Prism works even without internet access** if you have the repo cloned!

---

## Benefits Summary

### For Users:
- ✅ **No npm required** - Fetch via unpkg CDN
- ✅ **Fast downloads** - Global CDN distribution
- ✅ **Always latest** - Or pin specific versions
- ✅ **Offline fallback** - Local packages work too

### For Maintainers:
- ✅ **Standard workflow** - npm publish, everyone knows it
- ✅ **No custom infrastructure** - npm handles everything
- ✅ **Easy versioning** - Built-in semver
- ✅ **Discoverable** - People can find packages on npmjs.com

### For Everyone:
- ✅ **Open ecosystem** - Anyone can publish packages
- ✅ **Trusted platform** - npm's security & infrastructure
- ✅ **No vendor lock-in** - Standard package format

---

## Troubleshooting

### "403 Forbidden" when publishing

```bash
# Check you're logged in
npm whoami

# Login if needed
npm login

# Verify @prism scope access
# Contact Will Anderson if you need access
```

### "Package already exists"

```bash
# Increment version in package.json
# Then try publishing again
```

### "unpkg CDN unavailable"

```bash
# Installer will automatically fall back to local packages
# Or manually install: python3 scripts/npm_package_fetcher.py fetch PACKAGE --local
```

---

## Questions?

Contact: **Will Anderson** <andersonwilliam85@gmail.com>  
Repo: https://github.com/andersonwilliam85/prism
