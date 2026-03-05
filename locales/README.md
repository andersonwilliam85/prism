# i18n Locales

**Internationalization support for Dev Onboarding**

## Structure

```
locales/
├── en_US/           # English (US) - default
│   ├── messages.yaml
│   └── ui.yaml
│
├── es_ES/           # Spanish (Spain) - future
├── fr_FR/           # French (France) - future
├── de_DE/           # German (Germany) - future
├── ja_JP/           # Japanese (Japan) - future
└── zh_CN/           # Chinese (Simplified) - future
```

## Status

**Current:** English only
**Future:** Multi-language support via locale files

## Implementation Plan

1. **Phase 1** (Current)
   - All strings in English
   - Structure prepared for i18n

2. **Phase 2** (Future)
   - Extract all UI strings to `locales/en_US/`
   - Add translation framework
   - Support locale switching

3. **Phase 3** (Future)
   - Community translations
   - Locale detection
   - RTL language support

## Contributing Translations

**Not yet available** - coming soon!

When ready, translations will be community-driven via pull requests.
