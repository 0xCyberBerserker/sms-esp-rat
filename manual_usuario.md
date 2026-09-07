# User manual

Invoke `sms-esp-rat` after `token-rat-esp`. Default to `normal`; use `safe` when conditions, uncertainty, or high-stakes details dominate, and `max` only when compactness cannot alter meaning.

Read `references/codebook.md` once to learn aliases. A macro asserts its complete canonical meaning. Keep commands, code, paths, identifiers, versions, numbers, errors, negations, and copy-paste text literal.

Reproduce measurements:

```bash
python scripts/bench_sms_esp_rat.py --phase probe --max-calls 30
python scripts/bench_sms_esp_rat.py --phase smoke --max-calls 30
python scripts/bench_sms_esp_rat.py --phase dev --max-calls 150
python scripts/bench_sms_esp_rat.py --phase final --max-calls 500
```

The cache is `results/cache.jsonl`; interrupted runs resume without repeating unchanged calls.

---

# Manual de usuario

Invoca `sms-esp-rat` después de `token-rat-esp`. Usa `normal` por defecto, `safe` cuando dominen condiciones, incertidumbre o datos críticos, y `max` únicamente si la compresión conserva todo el significado.

Lee una vez `references/codebook.md`. Cada macro afirma todo su significado canónico. Conserva literalmente comandos, código, rutas, identificadores, versiones, números, errores, negaciones y texto para copiar.

Los comandos anteriores reproducen las mediciones. La caché permite reanudar sin repetir llamadas intactas.
