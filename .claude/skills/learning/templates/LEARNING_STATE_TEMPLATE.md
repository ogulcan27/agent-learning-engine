# Learning State

> Template: `.claude/skills/learning/templates/LEARNING_STATE_TEMPLATE.md`
> Target: `docs/learning/state/LEARNING_STATE.md`
> Role: **Derived runtime summary.** Elle düzenlenmez. Her ledger commit'inden sonra yeniden üretilir.

**Coverage truth lives in COVERAGE_LEDGER.** Bu dosya ile ledger çelişirse ledger kazanır ve bu dosya yeniden üretilir.

```yaml
schema_version: 1
status: INITIALIZED          # INITIALIZED | OK | REBUILT | INTEGRITY_FAIL
last_run: <YYYY-MM-DD>
last_learning_pass: -        # LP-YYYYMMDD-NN veya -
configured_work_unit_source: auto
resolved_work_unit_source: -  # auto mode sonucu; bilgi amaçlı
ledger_path: docs/learning/state/COVERAGE_LEDGER.md

open_coverage_count: 0       # UNCOVERED + PARTIAL + DEFERRED
uncovered_count: 0
deferred_count: 0
partial_count: 0
skipped_count: 0

# Bilgi amaçlı. Gap kaynağı DEĞİLDİR.
last_covered_boundary: -
```
