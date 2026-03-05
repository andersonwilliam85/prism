# Hierarchical Config Inheritance System

## Overview

This onboarding package supports **multi-level config inheritance** for enterprise organizations with complex structures:

```
Company (Walmart)
  ↓
Sub-Organization (Walmart US, Sam's Club, Walmart International)
  ↓
Department (Supply Chain, E-commerce, Data Engineering)
  ↓
Team (Receiving Systems, Checkout Frontend, Analytics Platform)
  ↓
Individual Developer
```

Each level **inherits and extends** from the previous level, allowing:
- ✅ Company-wide standards (proxy, security, compliance)
- ✅ Sub-org specific tools (region-specific cloud accounts)
- ✅ Department tech stacks (Java vs Python vs Node)
- ✅ Team conventions (specific repos, workflows, contacts)
- ✅ Personal preferences (IDE, career tracking)

---

## How It Works

### 1. Define Your Hierarchy

Edit `config/inheritance.yaml`:

```yaml
chain:
  company:
    file: "config/base/walmart.yaml"  # Required
  
  sub_org:
    file: null  # Will prompt during install
  
  department:
    file: null  # Will prompt during install
  
  team:
    file: null  # Will prompt during install
  
  user:
    file: "config/user-profile.yaml"  # Required
```

### 2. Create Configs for Each Level

**Company Base** (`config/base/walmart.yaml`):
```yaml
company:
  name: "Walmart"

environment:
  proxy:
    http: "http://sysproxy.wal-mart.com:8080"

tools_required:
  - git
  - kubectl
```

**Sub-Org** (`config/orgs/walmart-us.yaml`):
```yaml
sub_org:
  id: "walmart-us"
  name: "Walmart US"

# Inherits: proxy, git, kubectl
# Adds:
tools_required:
  - bq        # BigQuery for US analytics
  - gcloud
```

**Department** (`config/departments/supply-chain.yaml`):
```yaml
department:
  id: "supply-chain"
  name: "Supply Chain Technology"

# Inherits: proxy, git, kubectl, bq, gcloud
# Adds:
tools_required:
  - python    # Primary language
  - dbeaver   # Database client
```

**Team** (`config/teams/receiving-systems.yaml`):
```yaml
team:
  id: "receiving-systems"
  name: "Receiving Systems Team"

# Inherits all previous tools
# Adds:
tools_required:
  - skaffold  # Team uses K8s dev workflow

repositories:
  - name: "receiving-api"
    url: "https://github.walmart.com/supply-chain/receiving-api"
```

### 3. Configs Get Merged Automatically

When you run `install.py`, the system:

1. Loads company base
2. Loads and merges sub-org (inherits company)
3. Loads and merges department (inherits company + sub-org)
4. Loads and merges team (inherits all previous)
5. Loads and merges user profile (inherits all)

**Result:** A single merged config with all inherited settings!

---

## Merge Strategies

Defin in `config/inheritance.yaml`:

### Arrays (Lists)

```yaml
merge_strategy:
  arrays:
    tools_selected: "union"      # Combine, remove duplicates
    resources: "append"          # Keep all, in order
    onboarding_tasks: "append"   # All tasks from all levels
```

**Example:**
```yaml
# Company
tools_required: [git, kubectl]

# Department
tools_required: [python, dbeaver]

# Merged (union):
tools_required: [git, kubectl, python, dbeaver]
```

### Objects (Dictionaries)

```yaml
merge_strategy:
  objects:
    environment: "deep_merge"    # Recursively merge
    git: "override"              # Later config wins
    career: "user_only"          # Only user can set
```

**Example (deep_merge):**
```yaml
# Company
environment:
  proxy:
    http: "http://proxy.com:8080"
  maven:
    url: "https://maven.company.com"

# Department
environment:
  npm:
    registry: "https://npm.company.com"

# Merged (deep_merge):
environment:
  proxy:
    http: "http://proxy.com:8080"
  maven:
    url: "https://maven.company.com"
  npm:
    registry: "https://npm.company.com"
```

---

## Real-World Example

### Scenario: New Developer Joins Receiving Systems Team

**During install:**
```bash
python3 install.py

? Select your sub-organization: Walmart US
? Select your department: Supply Chain Technology
? Select your team: Receiving Systems
```

**Configs loaded:**
1. `config/base/walmart.yaml` (company)
2. `config/orgs/walmart-us.yaml` (sub-org)
3. `config/departments/supply-chain.yaml` (dept)
4. `config/teams/receiving-systems.yaml` (team)
5. `config/user-profile.yaml` (user)

**Merged result:**

```yaml
# From Company:
environment:
  proxy:
    http: "http://sysproxy.wal-mart.com:8080"

tools_required:
  - git
  - kubectl
  - gh

# From Walmart US:
tools_required:
  - bq
  - gcloud

cloud:
  gcp:
    project_prefix: "walmart-us"

# From Supply Chain:
tools_required:
  - python
  - dbeaver

tech_stack:
  primary_languages: [Python, Java, TypeScript]

# From Receiving Systems Team:
tools_required:
  - skaffold
  - helm

repositories:
  - name: "receiving-api"
    url: "https://github.walmart.com/supply-chain/receiving-api"

team:
  manager: "Jane Smith"
  slack_channel: "#receiving-systems"

# From User Profile:
git:
  user:
    name: "John Developer"
    email: "john.developer@walmart.com"

career:
  goals:
    - "Ship first feature in Q1"
```

**Tools installed:**
- Company required: `git`, `kubectl`, `gh`
- US required: `bq`, `gcloud`
- Dept required: `python`, `dbeaver`
- Team required: `skaffold`, `helm`
- **Total: 9 tools** (all inherited and merged!)

**Documentation homepage shows:**
- Company resources (DX, ME@Walmart, Code Puppy)
- US resources (GCP Console, BigQuery)
- Dept resources (Supply Chain Confluence, WMS Docs)
- Team resources (Receiving API docs, Team Slack)

---

## Environment Variables

Use `${VAR}` placeholders in configs:

```yaml
# In config file:
repositories:
  - url: "https://github.walmart.com/${TEAM}/my-repo"

# At runtime:
# export TEAM=receiving-systems
# Result: https://github.walmart.com/receiving-systems/my-repo
```

With defaults:
```yaml
cloud:
  region: "${REGION:-us-central1}"  # Defaults to us-central1
```

---

## Benefits

✅ **DRY** - Define once at company level, inherit everywhere  
✅ **Flexible** - Teams can add/override as needed  
✅ **Scalable** - Add new teams/depts without duplicating config  
✅ **Maintainable** - Update company proxy once, affects everyone  
✅ **Contextual** - Each dev gets exactly what they need  

---

## For Enterprise Admins

### Setting Up Your Company

1. **Fork this repo**
2. **Edit `config/base/your-company.yaml`** (replace Walmart)
3. **Create sub-org configs** in `config/orgs/`
4. **Create department configs** in `config/departments/`
5. **Create team configs** in `config/teams/`
6. **Update `config/inheritance.yaml`** with your structure
7. **Distribute to teams!**

### Managing Teams

Each team can **maintain their own config**:

```bash
# Team owns their config file
config/teams/my-team.yaml

# Team updates:
- Repositories
- Contacts
- Workflows
- Conventions

# Company IT owns:
config/base/company.yaml

# IT updates:
- Proxy
- Artifact repos
- Security tools
- Compliance
```

**IT changes propagate automatically!**

---

## API

### Python

```python
from scripts.config_merger import load_merged_config

# Load merged config
config = load_merged_config(
    company="config/base/walmart.yaml",
    sub_org="config/orgs/walmart-us.yaml",
    department="config/departments/supply-chain.yaml",
    team="config/teams/receiving-systems.yaml",
    user="config/user-profile.yaml"
)

# Access merged settings
proxy = config["environment"]["proxy"]["http"]
tools = config["tools_required"]
repos = config.get("repositories", [])
```

### CLI

```bash
# Test config merging
python3 scripts/config_merger.py

# Outputs merged JSON to stdout
```

---

## Examples

See:
- `config/base/walmart.yaml` - Company example
- `config/orgs/walmart-us.yaml` - Sub-org example
- `config/departments/supply-chain.yaml` - Department example
- `config/teams/receiving-systems.yaml` - Team example

Replace with your company structure!
