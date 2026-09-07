# Repository guidance

## Scope

This repository contains the `sms-esp-rat` Codex skill and its reproducible Astra benchmark. Keep it complementary to `token-rat-esp`; do not change that upstream skill.

## Stack and commands

- Python 3 standard library only.
- Build corpus: `python scripts/build_corpus.py`
- Tests: `python -m unittest discover -s tests -v`
- Validate skill: `python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .`
- Probe Astra: `python scripts/bench_sms_esp_rat.py --phase probe --max-calls 30`
- Smoke: `python scripts/bench_sms_esp_rat.py --phase smoke --max-calls 30`

## Constraints

- Preserve technical literals exactly.
- Keep code and comments in English; documentation is bilingual, English first.
- Use UTF-8.
- Do not log credentials or environment dumps.
- Do not exceed the requested Astra call budget; rely on the content-addressed cache.
- Holdout data must not influence codebook selection before the final run.
- Prefer small stdlib patches and targeted tests.
