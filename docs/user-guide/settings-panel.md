# Settings Panel

The settings drawer is accessible from the gear icon in the top-right corner of the installer UI. It lets you override default connection and registry settings without modifying any configuration files.

---

## Opening the Panel

Click the **⚙** icon in the upper-right corner of the installer. The drawer slides in from the right and can be dismissed by clicking outside it or pressing `Escape`.

---

## Available Settings

### Registry URL

Overrides the npm registry used to fetch prism packages.

```
Default: https://registry.npmjs.org
Example: https://npm.mycompany.com
```

Use this when your organization runs a private npm registry (Verdaccio, Artifactory, GitHub Packages, etc.).

> This setting takes precedence over the `prism_config.npm_registry` value in `package.yaml`. See [Custom Registries](custom-registries.md) for the full registry setup guide.

### Custom unpkg CDN URL

Overrides the CDN used to resolve prism packages by URL.

```
Default: https://unpkg.com
Example: https://cdn.mycompany.com
```

Useful in air-gapped environments where the public unpkg CDN is not reachable.

### Language

Selects the display language for the installer UI.

Available locales are listed in `locales/` — see the i18n documentation for the full list of supported languages.

The selection is stored in browser `localStorage` and persists across sessions.

---

## Persistence

Settings entered here are stored in browser `localStorage` under the key `prismSettings`. They apply to the current browser session and any future sessions from the same browser.

To reset to defaults, clear site data in your browser's developer tools (`Application → Storage → Clear site data`).

---

## Relationship to Prism Config

Settings entered in the panel override values from the prism's `prism_config` section. The precedence order is:

```
Settings panel  >  package.yaml prism_config  >  Built-in defaults
```

This means a user can always override what the prism author specified, which is intentional — enterprise users may need to point to a different registry than the author anticipated.

---

## See Also

- [Custom Registries](custom-registries.md) — Setting up a private npm registry end-to-end
- [Configuration Schema](../reference/configuration-schema.md) — `prism_config` reference
- [Local Docs Server](local-docs-server.md) — Post-install workspace discovery
