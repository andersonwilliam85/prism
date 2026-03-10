---
layout: default
title: Themes
---

# Themes

Prism ships with 5 built-in themes that control the gradient colors used throughout the installer UI. You can also define custom themes.

---

## Built-in Themes

| ID | Name | Colors |
|---|---|---|
| `ocean` | Ocean Blue | Blues and teals (`#0093E9`, `#80D0C7`, `#13547a`, `#009ffd`, `#2a2a72`) |
| `purple` | Purple Haze | Purples and blues (`#667eea`, `#764ba2`, `#f093fb`, `#4facfe`, `#00f2fe`) |
| `forest` | Forest Green | Greens (`#134E5E`, `#71B280`, `#56ab2f`, `#a8e063`, `#0f9b0f`) |
| `sunset` | Sunset Orange | Reds and oranges (`#f12711`, `#f5af19`, `#ff6a00`, `#ee0979`, `#ff512f`) |
| `midnight` | Midnight Dark | Dark blues and teals (`#2c3e50`, `#3498db`, `#34495e`, `#2980b9`, `#1abc9c`) |

The default theme is `ocean`.

---

## Selecting a Theme

### Via `prism_config` in `package.yaml`

```yaml
prism_config:
  theme: "midnight"
```

This sets the theme for everyone who installs the prism.

### Via the Settings Panel

Click the gear icon in the top-right of the installer UI. The theme selector is available in the settings drawer. The selection is saved to `localStorage` and persists across sessions.

Settings panel overrides take precedence over `prism_config`:

```
Settings panel  >  package.yaml prism_config  >  Built-in default (ocean)
```

---

## Restricting Available Themes

Use `theme_options` to limit which themes appear in the settings panel:

```yaml
prism_config:
  theme: "midnight"
  theme_options:
    - midnight
    - ocean
    - forest
```

Only the listed themes will be selectable. If omitted, all 5 built-in themes are available.

---

## Custom Themes

Define custom themes in `prism_config.custom_themes`. Each theme needs an `id`, `name`, and 5 gradient color slots:

```yaml
prism_config:
  theme: "brand"
  custom_themes:
    - id: "brand"
      name: "Company Brand"
      gradient_1: "#1e3a8a"
      gradient_2: "#3b82f6"
      gradient_3: "#2563eb"
      gradient_4: "#1d4ed8"
      gradient_5: "#1e40af"

    - id: "holiday"
      name: "Holiday Special"
      gradient_1: "#dc2626"
      gradient_2: "#16a34a"
      gradient_3: "#b91c1c"
      gradient_4: "#15803d"
      gradient_5: "#991b1b"
```

Custom themes are appended to the built-in list. You can reference a custom theme ID in the `theme` field.

### Gradient Color Slots

Each theme defines 5 gradient colors used across the UI:

| Slot | Typical Usage |
|---|---|
| `gradient_1` | Primary header gradient start |
| `gradient_2` | Primary header gradient end |
| `gradient_3` | Accent and progress bar |
| `gradient_4` | Secondary highlights |
| `gradient_5` | Tertiary / background accents |

---

## Persistence

- **Prism author setting** (`prism_config.theme`) — baked into the prism, applies to all users
- **User override** (settings panel) — stored in browser `localStorage` under `prismSettings`, applies to the current browser only

To reset to the prism default, clear site data in your browser's developer tools.

---

## Setting a Default Theme for Custom Prisms

```yaml
prism_config:
  theme: "brand"                    # default theme
  theme_options: ["brand", "ocean"] # available choices
  custom_themes:
    - id: "brand"
      name: "ACME Corp"
      gradient_1: "#1e3a8a"
      gradient_2: "#3b82f6"
      gradient_3: "#2563eb"
      gradient_4: "#1d4ed8"
      gradient_5: "#1e40af"
```

---

## See Also

- [Settings Panel](settings-panel.md) — How the settings drawer works
- [Configuration Schema](../reference/configuration-schema.md) — Full `prism_config` reference
- [Creating Prisms](creating-configurations.md) — Authoring a custom prism
