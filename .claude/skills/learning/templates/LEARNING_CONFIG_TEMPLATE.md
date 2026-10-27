# Learning Config

> Template: `.claude/skills/learning/templates/LEARNING_CONFIG_TEMPLATE.md`
> Target: `docs/learning/state/LEARNING_CONFIG.md`
> Role: Project preferences. Kullanıcı düzenler. `/learning` yalnız kullanıcı onayı ile değiştirir.

```yaml
learning_config_version: 1

# Kalıcı project identity. Format: PRJ-xxxxxxxx (8 hex, opaque).
# UNCONFIGURED ise persistence ilk çalıştığında ID üretir; kullanıcı onayı ile yazılır.
# Project rename olursa değişmez.
project_id: UNCONFIGURED

# Okunabilir ad. Değişebilir. Identity değildir.
project_name: UNCONFIGURED

# auto | jira | git | phase-doc
# Bilinmeyen değer: CONFIG ERROR. Fallback yapılmaz.
work_unit_source: auto

# Personal Technical Library konumu. Skill hard-code etmez.
# UNCONFIGURED ise persistence kullanıcıya sorar: yapılandır / LOCAL_TEMPORARY / ertele.
personal_library_path: UNCONFIGURED
```

## Notes

- Kurallar: `references/02_COVERAGE_PROTOCOL.md` Bölüm 3; persistence alanları `references/06_KNOWLEDGE_PERSISTENCE.md` §2.
- Bu dosya coverage truth taşımaz. Coverage truth: `COVERAGE_LEDGER.md`.
