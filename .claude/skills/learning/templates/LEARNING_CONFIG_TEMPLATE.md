# Learning Config

> Template: `.claude/skills/learning/templates/LEARNING_CONFIG_TEMPLATE.md`
> Target: `docs/learning/state/LEARNING_CONFIG.md`
> Role: Project preferences. Kullanıcı düzenler. `/learning` yalnız kullanıcı onayı ile değiştirir.

```yaml
learning_config_version: 1

# auto | jira | git | phase-doc
# Bilinmeyen değer: CONFIG ERROR. Fallback yapılmaz.
work_unit_source: auto

# Personal Technical Library konumu. UNCONFIGURED ise concept geçici olarak
# docs/learning/concepts/ içinde tutulur.
personal_library_path: UNCONFIGURED
```

## Notes

- Kurallar: `references/02_COVERAGE_PROTOCOL.md` Bölüm 3.
- Bu dosya coverage truth taşımaz. Coverage truth: `COVERAGE_LEDGER.md`.
