# Concept Registry

> Template: `.claude/skills/stay-in-the-loop/templates/CONCEPT_REGISTRY_TEMPLATE.md`
> Target: `<personal_library_path>/registry/CONCEPT_REGISTRY.md`
> Rules: `references/06_KNOWLEDGE_PERSISTENCE.md` §7, §18.1
> Role: **AUTHORITATIVE** identity registry. Teori taşımaz. Satır silinmez.
> Registry ve Concept Home Identity aynı transaction ile yazılır. Çelişki → integrity FAIL.

## Concepts

| Concept ID | Canonical Name | Aliases | Short Meaning | Home | Status |
|---|---|---|---|---|---|

## Field Reference

| Alan | Değerler |
|---|---|
| `Concept ID` | `CH-` + 8 lowercase hex |
| `Aliases` | `; ` listesi veya `-` |
| `Home` | `concepts/<concept-id>.md` veya `merged:<concept-id>` |
| `Status` | `ACTIVE` · `MERGED` |
