# Bad Configuration Examples

The `bad-config-examples/` directory in the repository root contains YAML files that intentionally trigger validation errors. They are used to test and demonstrate the validator — each one illustrates a specific failure mode.

---

## How to Use

### Trigger validation via the web UI

1. Copy one of the example files into a prism's sub-prism directory
2. Select that prism in the installer
3. Navigate to the **Confirmation** step
4. Click **Validate Configurations**
5. The validator will report the exact error

### Trigger validation via CLI

```bash
python3 scripts/package_validator.py prisms/my-company
```

---

## Error Reference

### Missing required field — `bad-company-no-name.yaml`

The `company.name` field is absent.

```yaml
company:
  domain: "example.com"
  # Missing 'name' field
```

**Output:**
```
❌  Company field 'name' cannot be empty
```

---

### Invalid YAML syntax — `bad-syntax.yaml`

Mismatched indentation and an unmatched quote.

```yaml
company:
  name: My Company
    invalid_indentation: true   # bad indent
git:
  url: https://github.com
  missing: quote here"          # unmatched quote
```

**Output:**
```
❌  Invalid YAML syntax: while scanning a simple key...
```

---

### Invalid git URL — `bad-git-url.yaml`

The git URL uses an unsupported protocol.

```yaml
git:
  url: "ftp://invalid-protocol.com"
  enterprise:
    enterprise_url: "not-a-url"
```

**Output:**
```
❌  Invalid git URL format: ftp://invalid-protocol.com
❌  Invalid GitHub Enterprise URL: not-a-url
```

Valid protocols: `https://`, `http://`, `git@`

---

### Wrong data type — `bad-types.yaml`

A section that must be a dictionary is a string instead.

```yaml
company: "This should be a dictionary!"
```

**Output:**
```
❌  'company' must be a dictionary
```

---

### Empty configuration — `empty.yaml`

A completely empty file.

```yaml
# (no content)
```

**Output:**
```
❌  Configuration file is empty: empty.yaml
```

---

### Missing organization name — `bad-org.yaml`

An organization entry is missing its `name` field.

```yaml
organization:
  id: "eng-org"
  description: "Engineering Organization"
  # Missing 'name'
```

**Output:**
```
❌  Organization missing required 'name' field
```

---

### Invalid proxy URL — `bad-proxy.yaml`

Proxy URLs must use `http://` or `https://`.

```yaml
environment:
  proxy:
    http: "proxy.example.com:8080"         # Missing protocol
    https: "socks5://proxy.example.com"    # Wrong protocol
```

**Output:**
```
❌  Invalid http proxy URL: proxy.example.com:8080
❌  Invalid https proxy URL: socks5://proxy.example.com
```

---

## Warnings vs. Errors

The validator distinguishes between hard errors (installation blocked) and warnings (installation proceeds with a note):

| Severity | Examples |
|---|---|
| Error | Missing required field, invalid URL, empty file, bad YAML syntax |
| Warning | Missing recommended field (`email`), no `README.md` in prism, no user section in user config |

Warnings appear in the validation output but do not prevent installation.

---

## See Also

- [Creating Configurations](../user-guide/creating-configurations.md) — Author a valid prism
- [Configuration Schema](configuration-schema.md) — Full schema reference
- `scripts/package_validator.py` — Validator implementation
