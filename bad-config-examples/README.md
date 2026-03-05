# Bad Configuration Examples

These examples demonstrate common configuration errors and how the validator catches them.

## Example 1: Missing Company Name

**File:** `bad-company-no-name.yaml`

**Error:** Missing required 'name' field in company section

```yaml
company:
  domain: "example.com"
  # Missing 'name' field!

environment:
  proxy:
    http: "http://proxy.example.com:8080"
```

**Validation Output:**
```
❌ base/bad-company-no-name.yaml:
  - Company field 'name' cannot be empty
```

---

## Example 2: Invalid YAML Syntax

**File:** `bad-syntax.yaml`

**Error:** Invalid YAML syntax (missing quotes, bad indentation)

```yaml
company:
  name: My Company
  domain: example.com
    invalid_indentation: true  # Bad indentation!
git:
  url: https://github.com
  missing: quote here"  # Unmatched quote!
```

**Validation Output:**
```
❌ base/bad-syntax.yaml:
  - Invalid YAML syntax: while scanning a simple key...
```

---

## Example 3: Invalid Git URL

**File:** `bad-git-url.yaml`

**Error:** Git URL doesn't start with http://, https://, or git@

```yaml
company:
  name: "My Company"
  domain: "example.com"

git:
  url: "ftp://invalid-protocol.com"  # Invalid protocol!
  enterprise:
    enterprise_url: "not-a-url"  # Invalid URL format!
```

**Validation Output:**
```
❌ base/bad-git-url.yaml:
  - Invalid git URL format: ftp://invalid-protocol.com
  - Invalid GitHub Enterprise URL: not-a-url
```

---

## Example 4: Wrong Data Type

**File:** `bad-types.yaml`

**Error:** Configuration sections must be dictionaries, not strings/lists

```yaml
company: "This should be a dictionary!"  # Wrong type!
```

**Validation Output:**
```
❌ base/bad-types.yaml:
  - 'company' must be a dictionary
```

---

## Example 5: Empty Configuration

**File:** `empty.yaml`

**Error:** Configuration file is empty

```yaml
# File is empty!
```

**Validation Output:**
```
❌ base/empty.yaml:
  - Configuration file is empty: empty.yaml
```

---

## Example 6: Missing Organization Name

**File:** `bad-org.yaml` (in orgs/ directory)

**Error:** Organization missing required 'name' field

```yaml
organization:
  id: "eng-org"
  # Missing 'name' field!
  description: "Engineering Organization"
```

**Validation Output:**
```
❌ orgs/bad-org.yaml:
  - Organization missing required 'name' field
```

---

## Example 7: Invalid Proxy URL

**File:** `bad-proxy.yaml`

**Error:** Proxy URLs must start with http:// or https://

```yaml
company:
  name: "My Company"

environment:
  proxy:
    http: "proxy.example.com:8080"  # Missing protocol!
    https: "socks5://proxy.example.com:1080"  # Wrong protocol!
```

**Validation Output:**
```
❌ base/bad-proxy.yaml:
  - Invalid http proxy URL: proxy.example.com:8080
  - Invalid https proxy URL: socks5://proxy.example.com:1080
```

---

## How to Test

### Using CLI:

```bash
# Create a test package with bad configs
mkdir -p test-package/base
cp bad-company-no-name.yaml test-package/base/

# Run validation
python3 scripts/config_validator.py test-package
```

### Using Web UI:

1. Add bad config files to any package's base/ directory
2. Select that package in the installer
3. Navigate to the "Confirmation" step
4. Click "🔍 Validate Configurations"
5. See detailed error messages!

---

## Common Validation Errors

### Structure Errors:
- ❌ Missing required sections (company, org, team, etc.)
- ❌ Wrong data types (string instead of dict)
- ❌ Empty files
- ❌ Invalid YAML syntax

### Content Errors:
- ❌ Missing required fields (name, etc.)
- ❌ Empty required fields
- ❌ Invalid URL formats
- ❌ Invalid protocol schemes

### Warnings (non-blocking):
- ⚠️ Missing recommended fields (email, etc.)
- ⚠️ No user section in user config
- ⚠️ Missing README.md

---

## Validation Workflow

```
User clicks "Validate Configurations"
          ↓
   Load all config files
   (base/, orgs/, departments/, teams/)
          ↓
   Parse YAML syntax
          ↓
   Validate structure
          ↓
   Validate content
          ↓
   Generate summary
          ↓
   Display results in UI
```

**Benefits:**
- ✅ Catch errors before installation
- ✅ Clear, actionable error messages
- ✅ Helps package authors fix issues
- ✅ Prevents broken installations

---

## See Also

- `scripts/config_validator.py` - Validation implementation
- `scripts/package_validator.py` - Package structure validation
- Web UI `/api/package/<id>/validate-configs` - Validation endpoint
