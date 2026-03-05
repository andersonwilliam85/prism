# Custom Registry Configuration

Prism supports using custom npm registries and unpkg CDN URLs for air-gapped environments, corporate proxies, or custom package hosting.

## Configuration Methods

### 1. Environment Variables (Recommended)

Set environment variables before running the installer:

```bash
# Custom npm registry
export PRISM_NPM_REGISTRY=https://npm.mycompany.com

# Custom unpkg CDN
export PRISM_UNPKG_URL=https://cdn.mycompany.com/npm

# Now run installer
python3 install.py
```

### 2. CLI Arguments

Specify registries directly when running commands:

```bash
# List packages from custom registry
python3 scripts/npm_package_fetcher.py list \
  --registry https://npm.mycompany.com

# Fetch package from custom CDN
python3 scripts/npm_package_fetcher.py fetch @prism/personal-dev-config \
  --unpkg https://cdn.mycompany.com/npm

# Run installer with custom registry
python3 install.py \
  --npm-registry https://npm.mycompany.com \
  --unpkg-url https://cdn.mycompany.com/npm
```

### 3. Combined Approach

CLI arguments override environment variables:

```bash
# Set defaults via env vars
export PRISM_NPM_REGISTRY=https://npm.mycompany.com

# Override for specific command
python3 install.py --npm-registry https://registry.npmjs.org
```

---

## Use Cases

### Corporate Environments

Many companies use private npm registries (Artifactory, Nexus, Verdaccio):

```bash
# Point to corporate Artifactory
export PRISM_NPM_REGISTRY=https://artifactory.company.com/artifactory/api/npm/npm-virtual
export PRISM_UNPKG_URL=https://artifactory.company.com/artifactory/npm-virtual

python3 install.py
```

### Air-Gapped Environments

For environments without internet access, host packages internally:

```bash
# Point to internal mirror
export PRISM_NPM_REGISTRY=https://internal-npm.company.local
export PRISM_UNPKG_URL=https://internal-cdn.company.local

python3 install.py
```

### Development/Testing

Test with local registry during development:

```bash
# Use local Verdaccio instance
export PRISM_NPM_REGISTRY=http://localhost:4873
export PRISM_UNPKG_URL=http://localhost:4873

python3 scripts/npm_package_fetcher.py list
```

---

## Registry Requirements

### npm Registry

Must support standard npm registry API:

- **Metadata endpoint**: `GET /{package}` returns package.json
- **Dist-tags**: Support `latest` tag
- **Scope support**: Handle `@prism/*` scoped packages

**Compatible registries:**
- npm public registry (default)
- JFrog Artifactory
- Sonatype Nexus
- Verdaccio
- Azure Artifacts
- GitHub Packages
- GitLab Package Registry

### unpkg CDN

Must serve package files at:

```
{CDN_URL}/{package}@{version}/{file}
```

**Examples:**
- `https://unpkg.com/@prism/personal-dev-config@1.0.0/package.yaml`
- `https://cdn.company.com/npm/@prism/personal-dev-config@1.0.0/package.yaml`

**Compatible CDNs:**
- unpkg.com (default)
- jsDelivr
- Custom CDN mirrors
- Artifactory (with npm remote repository)

---

## Setting Up Custom Registry

### Option 1: Artifactory

1. **Create npm repository** in Artifactory
2. **Configure proxy** to npmjs.org (or use local only)
3. **Publish Prism packages** to your instance:

```bash
# Configure npm to use Artifactory
npm config set registry https://artifactory.company.com/artifactory/api/npm/npm-local/

# Login
npm login

# Publish packages
cd config-packages/personal-dev
npm publish
```

4. **Point Prism installer** to Artifactory:

```bash
export PRISM_NPM_REGISTRY=https://artifactory.company.com/artifactory/api/npm/npm-local
export PRISM_UNPKG_URL=https://artifactory.company.com/artifactory/npm-local
```

### Option 2: Verdaccio (Lightweight)

1. **Install Verdaccio:**

```bash
npm install -g verdaccio
verdaccio
```

2. **Configure npm:**

```bash
npm set registry http://localhost:4873
```

3. **Publish packages:**

```bash
cd config-packages/personal-dev
npm publish
```

4. **Use with Prism:**

```bash
export PRISM_NPM_REGISTRY=http://localhost:4873
export PRISM_UNPKG_URL=http://localhost:4873
```

### Option 3: GitHub Packages

1. **Configure npm:**

```bash
echo "@prism:registry=https://npm.pkg.github.com" >> .npmrc
echo "//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}" >> .npmrc
```

2. **Publish packages:**

```bash
cd config-packages/personal-dev
npm publish
```

3. **Use with Prism:**

```bash
export PRISM_NPM_REGISTRY=https://npm.pkg.github.com
# GitHub Packages doesn't provide unpkg-style CDN, use fallback
python3 install.py --local  # Use local packages
```

---

## Fallback Behavior

Prism has robust fallback:

1. **Try custom unpkg CDN** (if configured)
2. **Try custom npm registry** (if configured)
3. **Try public unpkg.com** (if custom fails)
4. **Try public registry.npmjs.org** (if custom fails)
5. **Use local packages** (if all network fetches fail)

This ensures Prism works even with partial network failures!

---

## Troubleshooting

### Check Current Configuration

```bash
# Show what Prism will use
python3 scripts/npm_package_fetcher.py list
# First line shows: "Registry Configuration: ..."
```

### Test Registry Connection

```bash
# Test npm registry
curl https://npm.mycompany.com/@prism/personal-dev-config

# Test unpkg CDN
curl https://cdn.mycompany.com/npm/@prism/personal-dev-config@latest/package.yaml
```

### Common Issues

**"Connection refused"**
- Check registry URL is accessible
- Verify VPN/network connectivity
- Check firewall rules

**"401 Unauthorized"**
- Configure npm authentication
- Check `~/.npmrc` has auth token
- Verify token hasn't expired

**"404 Not Found"**
- Ensure packages are published to your registry
- Check package names match `@prism/*` scope
- Verify registry supports scoped packages

**"Package not found, using local"**
- Expected behavior! Falls back to local packages
- Ensures offline/air-gapped setups work

---

## Environment Variable Reference

| Variable | Description | Default |
|----------|-------------|----------|
| `PRISM_NPM_REGISTRY` | npm registry URL for package metadata | `https://registry.npmjs.org` |
| `PRISM_UNPKG_URL` | unpkg CDN URL for package files | `https://unpkg.com` |

---

## Complete Example: Corporate Setup

```bash
#!/bin/bash
# File: setup_prism_corporate.sh

# Corporate registry configuration
export PRISM_NPM_REGISTRY="https://artifactory.mycompany.com/artifactory/api/npm/npm-virtual"
export PRISM_UNPKG_URL="https://artifactory.mycompany.com/artifactory/npm-virtual"

# Optional: Set proxy if needed
export HTTP_PROXY="http://proxy.mycompany.com:8080"
export HTTPS_PROXY="http://proxy.mycompany.com:8080"

# Install Prism
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# List available packages (will use corporate registry)
python3 scripts/npm_package_fetcher.py list

# Run installer
python3 install.py --package @prism/fortune500-config
```

---

## Security Considerations

### HTTPS Only

Always use HTTPS for production registries:

```bash
# Good
export PRISM_NPM_REGISTRY=https://npm.company.com

# Bad (only for local dev!)
export PRISM_NPM_REGISTRY=http://localhost:4873
```

### Authentication

For private registries requiring auth:

```bash
# Configure npm authentication first
npm login --registry https://npm.company.com

# Then run Prism (inherits npm auth)
python3 install.py
```

### Certificate Validation

For self-signed certs, you may need:

```bash
# Disable SSL verification (not recommended for production!)
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Better: Add CA cert to system trust store
```

---

## Questions?

Contact: **Will Anderson** <andersonwilliam85@gmail.com>  
Repo: https://github.com/andersonwilliam85/prism  
Issues: https://github.com/andersonwilliam85/prism/issues
