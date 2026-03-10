---
layout: default
title: Cascading Dropdowns
---

# Cascading Dropdowns

Cascading dropdowns let you create dependent select fields where the options in a child field are filtered based on the selected value in a parent field. For example, selecting a division automatically narrows the available teams.

---

## How It Works

1. A parent field (e.g., `division`) is a standard `select` with a fixed `options` list.
2. A child field (e.g., `team`) declares `depends_on: "division"` and provides an `option_map` keyed by parent values.
3. When the user selects a parent value, the ConfigEngine filters the child's options to only those matching the selected parent.
4. If the parent value has no entry in `option_map`, the full `options` list is shown as a fallback.

---

## Configuration

### Parent Field

A normal select field — no special configuration needed:

```yaml
user_info_fields:
  - id: "division"
    label: "Division"
    type: "select"
    required: true
    options:
      - "Technology"
      - "Digital"
      - "Operations"
```

### Child Field

Add `depends_on` and `option_map`:

```yaml
  - id: "team"
    label: "Team"
    type: "select"
    required: true
    depends_on: "division"
    options:
      - "Platform"
      - "Frontend"
      - "Backend"
      - "Data"
      - "DevOps"
      - "Mobile"
      - "QA"
    option_map:
      Technology:
        - "Platform"
        - "Backend"
        - "DevOps"
      Digital:
        - "Frontend"
        - "Mobile"
        - "Data"
      Operations:
        - "QA"
        - "DevOps"
```

### Multi-Level Cascading

You can chain dependencies across multiple levels:

```yaml
user_info_fields:
  - id: "region"
    label: "Region"
    type: "select"
    options: ["Americas", "EMEA", "APAC"]

  - id: "country"
    label: "Country"
    type: "select"
    depends_on: "region"
    options: ["US", "Canada", "UK", "Germany", "Japan", "Australia"]
    option_map:
      Americas: ["US", "Canada"]
      EMEA: ["UK", "Germany"]
      APAC: ["Japan", "Australia"]

  - id: "office"
    label: "Office"
    type: "select"
    depends_on: "country"
    options: ["NYC", "Toronto", "London", "Berlin", "Tokyo", "Sydney"]
    option_map:
      US: ["NYC"]
      Canada: ["Toronto"]
      UK: ["London"]
      Germany: ["Berlin"]
      Japan: ["Tokyo"]
      Australia: ["Sydney"]
```

---

## Dependency Resolution

The ConfigEngine uses topological sort to determine the correct rendering order for fields. Fields without dependencies appear first, followed by their dependents.

Given fields `[team, division, name]` where `team` depends on `division`:

```
Input order:   team, division, name
Resolved order: name, division, team
```

This ensures parent fields are always rendered before their children, regardless of declaration order in `package.yaml`.

---

## UI Behavior

- When a parent value changes, all dependent child fields reset to empty.
- If a child field's filtered options contain only one item, it is not auto-selected — the user must explicitly choose.
- Disabled state: child fields appear disabled until their parent has a selected value.

---

## Fallback Behavior

If `option_map` does not contain a key for the selected parent value, the child field shows its full `options` list. This lets you define a broad fallback while still filtering for known parent values.

```yaml
  - id: "team"
    depends_on: "division"
    options: ["General"]          # fallback if division not in option_map
    option_map:
      Technology: ["Platform", "Backend"]
      Digital: ["Frontend", "Mobile"]
```

Selecting "Operations" (not in `option_map`) would show `["General"]`.

---

## See Also

- [Configuration Schema](../reference/configuration-schema.md) — `user_info_fields` reference
- [Creating Prisms](creating-configurations.md) — Full prism authoring guide
- [Architecture](../reference/architecture.md) — ConfigEngine in the system design
