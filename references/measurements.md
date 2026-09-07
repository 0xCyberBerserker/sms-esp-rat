# Measurement record

Generated benchmark facts belong in `results/summary.md` and `results/token_probe.csv`. This file records only the policy derived from those measurements.

- Token counts from `codex exec --json` are `MEASURED` model usage.
- Per-string tokenizer probes use Astra exact-echo output usage; fixed response framing is removed by paired comparison when possible.
- If exact per-string isolation is unavailable, mark the number `ESTIMATED`; never mix it with measured totals.
- Keep an abbreviation only when it saves output tokens on Astra and remains readable.
- Remove a macro when observed total gain does not offset ambiguity or prompt overhead.

The benchmark updates the accepted/rejected tables after each completed phase.

## Final selection / Selección final

Accepted abbreviations: `config`, `ok`, `check`, `next`.

Rejected: `pq`, `xq`, `pa`, `tmb`, and `fail` saved no tokens; `tb` saved one token but is normally better omitted; `cfg` tied `config` with worse readability; `beh` saved tokens but harmed reconstructability.

Abreviaturas aceptadas: `config`, `ok`, `check`, `next`.

Rechazadas: `pq`, `xq`, `pa`, `tmb` y `fail` no ahorraron tokens; `tb` ahorró uno, pero normalmente conviene omitir el conector; `cfg` empató con `config` y es menos legible; `beh` ahorró tokens a costa de la reconstrucción.

Accepted macros are the nine entries in `codebook.md`. Rejected after development mining: `fail:<cause>`, `cause!`, `skip:<reason>`, and `same` (zero observed uses).

Las nueve entradas de `codebook.md` quedan aceptadas. Rechazadas tras minería de desarrollo: `fail:<causa>`, `cause!`, `skip:<motivo>` y `same` (cero usos observados).
