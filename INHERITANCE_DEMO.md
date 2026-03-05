# Hierarchical Config Inheritance Demo

## 🏢 Example: New Developer Joining Receiving Systems Team

### The Scenario

**New hire:** Sarah Johnson  
**Company:** Walmart  
**Sub-org:** Walmart US  
**Department:** Supply Chain Technology  
**Team:** Receiving Systems  

### What Happens During Onboarding

```bash
python3 install.py

🐶 Dev Onboarding Package
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Platform detected: Mac (Apple Silicon)

📋 Let's configure your environment!

? What's your name: Sarah Johnson
? Email: sarah.johnson@walmart.com

? Select your sub-organization:
  > Walmart US
    Sam's Club
    Walmart International
    None

? Select your department:
  > Supply Chain Technology
    E-commerce Engineering
    Data Engineering
    Platform & Infrastructure
    None

? Select your team:
  > Receiving Systems
    Fulfillment & Shipping
    Inventory Management
    None

⚙️  Loading configs...
  ✅ Company base (walmart.yaml)
  ✅ Sub-org (walmart-us.yaml)
  ✅ Department (supply-chain.yaml)
  ✅ Team (receiving-systems.yaml)
  ✅ User profile

🔄 Merging configurations...
  ✅ Inherited 12 company-wide tools
  ✅ Added 3 US-specific tools
  ✅ Added 4 Supply Chain tools
  ✅ Added 2 Receiving Systems tools
  📦 Total: 21 tools configured

🚀 Installing selected tools...
```

### Config Hierarchy Breakdown

#### 1️⃣ COMPANY (walmart.yaml)

**Inherited by everyone:**
```yaml
environment:
  proxy:
    http: "http://sysproxy.wal-mart.com:8080"

tools_required:
  - git
  - kubectl
  - gh
  - jq
  - yq

resources:
  - ME@Walmart
  - WMLink
  - Code Puppy
  - Artifactory
```

#### 2️⃣ SUB-ORG (walmart-us.yaml)

**Adds for US operations:**
```yaml
tools_required:
  - bq        # BigQuery (US uses GCP)
  - gcloud

cloud:
  gcp:
    project_prefix: "walmart-us"
    default_region: "us-central1"

resources:
  - GCP Console (US)
  - BigQuery (US Data Warehouse)
```

#### 3️⃣ DEPARTMENT (supply-chain.yaml)

**Adds for Supply Chain:**
```yaml
tools_required:
  - python
  - dbeaver

tech_stack:
  primary_languages: [Python, Java, TypeScript]
  frameworks: [FastAPI, Spring Boot, React]

resources:
  - Supply Chain Architecture docs
  - WMS API Documentation
  - Slack: #supply-chain-tech
  - Warehouse databases
```

#### 4️⃣ TEAM (receiving-systems.yaml)

**Adds for Receiving Systems:**
```yaml
tools_required:
  - skaffold
  - helm

repositories:
  - receiving-api (FastAPI)
  - receiving-ui (React)
  - putaway-engine (Python)

contacts:
  manager: "Jane Smith"
  tech_lead: "John Doe"

workflow:
  branching:
    format: "feat/RECV-<ticket>-<description>"
  
resources:
  - Team Slack: #receiving-systems
  - Receiving API docs
  - Grafana dashboard
```

#### 5️⃣ USER (sarah's profile)

**Personal settings:**
```yaml
user:
  name: "Sarah Johnson"
  email: "sarah.johnson@walmart.com"

tools_selected:
  ide: vscode  # Personal choice

career:
  goals:
    - "Ship first feature in Q1 2026"
    - "Learn Kubernetes deployments"
```

### 📦 Final Merged Config (Sarah's Environment)

```yaml
# MERGED RESULT - Everything Sarah gets!

company:
  name: "Walmart"

environment:
  proxy:  # From company
    http: "http://sysproxy.wal-mart.com:8080"
  
  maven:  # From company
    url: "https://maven.ci.artifacts.walmart.com"
  
  npm:  # From company
    registry: "https://npm.ci.artifacts.walmart.com"

cloud:  # From US sub-org
  gcp:
    project_prefix: "walmart-us"
    default_region: "us-central1"

tools_required:
  # Company (5):
  - git
  - kubectl
  - gh
  - jq
  - yq
  
  # US (2):
  - bq
  - gcloud
  
  # Supply Chain (2):
  - python
  - dbeaver
  
  # Receiving Systems (2):
  - skaffold
  - helm

tools_selected:
  # Sarah's choice:
  ide: vscode

tech_stack:  # From Supply Chain
  primary_languages: [Python, Java, TypeScript]
  frameworks: [FastAPI, Spring Boot, React]

repositories:  # From Receiving Systems
  - name: "receiving-api"
    url: "https://gecgithub01.walmart.com/supply-chain/receiving-api"
    language: "Python (FastAPI)"
  
  - name: "receiving-ui"
    url: "https://gecgithub01.walmart.com/supply-chain/receiving-ui"
    language: "TypeScript (React)"

resources:
  # Company:
  - ME@Walmart
  - WMLink
  - Code Puppy
  
  # US:
  - GCP Console (US)
  - BigQuery
  
  # Supply Chain:
  - Supply Chain Confluence
  - WMS API Docs
  - Slack: #supply-chain-tech
  
  # Receiving Systems:
  - Team Slack: #receiving-systems
  - Receiving API docs
  - Grafana dashboard

contacts:  # From Receiving Systems
  manager: "Jane Smith"
  tech_lead: "John Doe"
  slack_channel: "#receiving-systems"

onboarding:
  # Company first_day tasks
  - Access ME@Walmart
  - Set up VPN
  - Join Slack
  
  # US first_week tasks
  - Access GCP US projects
  - Join #us-engineering
  
  # Supply Chain first_week tasks
  - Join #supply-chain-tech
  - Request warehouse DB access
  
  # Receiving Systems first_week tasks
  - Clone receiving-api repo
  - Set up Skaffold local dev
  - Join #receiving-systems

user:  # Sarah's personal
  name: "Sarah Johnson"
  email: "sarah.johnson@walmart.com"

career:
  goals:
    - "Ship first feature in Q1 2026"
    - "Learn Kubernetes deployments"
```

### 🎯 What Sarah Gets

**Installed Tools:** 11 required + 1 optional (VSCode)  
**Resources:** 15+ links on docs homepage  
**Repositories:** 3 team repos auto-configured  
**Onboarding Tasks:** 20+ tasks from all levels  
**Team Contacts:** Manager, tech lead, PO, scrum master  
**Career Dashboard:** Ready to track goals & wins  

### 🔄 When IT Updates Company Config

**Scenario:** IT changes proxy server

```yaml
# IT edits config/base/walmart.yaml
environment:
  proxy:
    http: "http://new-proxy.wal-mart.com:9090"  # Changed!
```

**Effect:** Next time ANY developer runs install:
- ✅ Sarah (Receiving Systems) gets new proxy
- ✅ Bob (E-commerce Frontend) gets new proxy
- ✅ Alice (Data Engineering) gets new proxy
- ✅ **Everyone** inherits the change automatically!

**No need to update:**
- ❌ Sub-org configs
- ❌ Department configs
- ❌ Team configs
- ❌ User profiles

**Change propagates automatically! 🎉**

---

## Benefits Demonstrated

✅ **DRY** - Proxy defined once, inherited by 1000+ devs  
✅ **Contextual** - Sarah gets exactly what she needs (no more, no less)  
✅ **Scalable** - Add new team = 1 file, inherits everything  
✅ **Maintainable** - IT changes propagate automatically  
✅ **Flexible** - Teams customize without breaking company standards  

---

## For Other Companies

**Replace:**
1. `config/base/walmart.yaml` → `your-company.yaml`
2. `config/orgs/*` → Your divisions/sub-orgs
3. `config/departments/*` → Your departments
4. `config/teams/*` → Your teams

**Keep:**
- The inheritance system (works for any structure!)
- The merge logic
- The documentation

**You're ready to scale to thousands of developers! 🚀**
