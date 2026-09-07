# Astra benchmark report / Informe benchmark Astra

English: `sms-esp-rat` is a safe output-token win over `token-rat-esp`; the codebook-only ablation is the most efficient configuration. Full E remains useful when both requested mechanisms are enabled. All counts below are measured by Astra/Codex CLI unless stated otherwise.

Español: `sms-esp-rat` reduce con seguridad los output tokens respecto a `token-rat-esp`; la ablación solo-codebook es la configuración más eficiente. E completo sigue siendo útil cuando se activan ambos mecanismos solicitados. Todos los conteos son medidos por Astra/Codex CLI salvo indicación.

## Implemented / Implementado

- `SKILL.md`: pipeline, modos `safe/normal/max`, telegraphy y protección estricta.
- `references/codebook.md`: nueve macros composables; `lorem` mantiene su significado reservado.
- `scripts/bench_sms_esp_rat.py`: A/B/C/D/E, usage oficial, caché/reanudación, integrity y fidelity.
- `scripts/build_corpus.py`: 100 prompts únicos; 50 training, 25 validation, 25 holdout; 20 adversariales y 4 conversaciones encadenadas.
- `data/*.jsonl`, `results/final.jsonl`, probes CSV y tests de regresión/integridad.

## Astra

- Comando detectado: `codex exec`; no existe binario/alias independiente `astra`.
- Modelo: `gpt-6-astra`; reasoning: `low`.
- Invocación: `codex exec --ignore-user-config --ephemeral --skip-git-repo-check --sandbox read-only --model gpt-6-astra -c 'model_reasoning_effort="low"' --json -`.
- Medición: `input_tokens`, `output_tokens` y `cached_input_tokens` oficiales del evento `turn.completed`: `MEASURED`.

## Codebook

Los tokens de expansión/alias proceden de exact-echo. El framing fijo afecta a ambas columnas; `ahorro/u` es la diferencia fiable.

| Alias | Significado abreviado | Exp tokens | Alias tokens | Freq E | Ahorro estimado |
| --- | --- | ---: | ---: | ---: | ---: |
| `lorem` | cambio mínimo; resto intacto; sin refactor/scope extra | 25 | 6 | 9 | 171 |
| `testok` | todas las pruebas indicadas OK | 16 | 6 | 10 | 100 |
| `buildok` | build indicado OK | 13 | 6 | 2 | 14 |
| `partial` | resultado incompleto/parcial | 14 | 5 | 10 | 90 |
| `runtime?` | checks estáticos; runtime sin validar | 18 | 6 | 9 | 108 |
| `evidence?` | evidencia insuficiente | 15 | 7 | 8 | 64 |
| `blocked:<causa>` | progreso bloqueado por causa literal | 14 | 5 | 6 | 54 |
| `cause?` | causa probable, no confirmada | 14 | 6 | 4 | 32 |
| `rollback` | rollback disponible/probado; no implica ejecución | 19 | 5 | 7 | 98 |

Rechazadas tras desarrollo: `fail:<causa>`, `cause!`, `skip:<motivo>`, `same`; frecuencia observada 0.

## SMS

| Transformación | Antes | Después | Decisión |
| --- | ---: | ---: | --- |
| `configuración -> config` | 6 | 5 | ACCEPT |
| `correcto -> ok` | 6 | 5 | ACCEPT |
| `comprobar -> check` | 7 | 5 | ACCEPT |
| `siguiente -> next` | 6 | 5 | ACCEPT |
| `porque -> pq/xq` | 5 | 5/6 | REJECT |
| `también -> tmb` | 6 | 6 | REJECT |
| `también -> tb` | 6 | 5 | REJECT: mejor omitir; legibilidad |
| `para -> pa` | 5 | 5 | REJECT |
| `configuración -> cfg` | 6 | 5 | REJECT: `config` empata y es más claro |
| `comportamiento -> beh` | 7 | 5 | REJECT: reconstrucción pobre |
| `error -> fail` | 5 | 5 | REJECT |

## Benchmark

| Variante | Output tokens | vs A | vs B | Fidelity | Integrity fails |
| --- | ---: | ---: | ---: | ---: | ---: |
| A baseline | 9.550 | 0,0% | -23,8% | 0,920 | 0 |
| B token-rat | 7.714 | 19,2% | 0,0% | 0,923 | 2 |
| C token-rat + SMS | 7.223 | 24,4% | 6,4% | 0,953 | 0 |
| D token-rat + codebook | 6.760 | 29,2% | 12,4% | 0,973 | 0 |
| E full | 6.872 | 28,0% | 10,9% | 1,000 | 0 |

Mediana/p90 E: 67/85 tokens. Ahorro absoluto B→E: 842 tokens, 8,42 por respuesta. Hubo 11 regresiones de longitud; la peor fue `case-047-confirmed` (-76) por información causal ausente en el propio prompt. No hubo pérdida semántica o técnica en E tras revisión determinista y muestreo externo de máximos ahorros/regresiones.

| Variante | Input tokens | Total tokens | Caracteres | Palabras | Latencia media/p50/p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 2.580.124 | 2.589.674 | 23.541 | 2.798 | 9,206 / 8,448 / 12,557 s |
| B | 2.530.508 | 2.538.222 | 22.250 | 2.665 | 8,355 / 7,835 / 10,735 s |
| C | 2.535.969 | 2.543.192 | 20.441 | 2.236 | 8,168 / 7,795 / 10,002 s |
| D | 2.568.441 | 2.575.201 | 19.556 | 2.174 | 7,693 / 7,497 / 9,059 s |
| E | 2.607.555 | 2.614.427 | 18.029 | 1.993 | 8,077 / 7,739 / 10,343 s |

Ahorro B→E por categoría: mejores `scope` 35,3%, `technical-docs` 30,8%, `numeric-boundary` 26,5%; peores `filesystem` -88,2% (B omitió hechos), `tests` -4,5%, `units` -4,3%. Estas regresiones miden longitud, no fidelidad: E conservó hechos que las variantes más cortas omitieron.

## Experiment cost / Coste del experimento

- Llamadas Astra del harness: 794; enlace inicial: 2; total: 796.
- Caché final: 794 entradas; replay final: 495 hits y 5 llamadas.
- Cache hits acumulados observados durante iteraciones: 2.806; llamadas evitadas equivalentes.
- Usage harness: 20.380.580 input tokens, 58.748 output tokens; 12.696.192 input tokens cacheados.
- Fases: probe, smoke, development, final, una poda y dos iteraciones E; último ajuste adversarial limitado a 5 llamadas.

## Break-even

Las ecuaciones completas de ahorro, fidelidad, integridad, ablación, overhead, break-even y caché están explicadas en el [modelo matemático](../docs/modelo-matematico.md).

| Configuración | Overhead input medio | Ahorro output medio | Break-even |
| --- | ---: | ---: | ---: |
| C SMS | 54,61 | 4,91 | 11,1 respuestas |
| D codebook | 379,33 | 9,54 | 39,8 respuestas |
| E full | 770,47 | 8,42 | 91,5 respuestas |

El overhead se calcula por diferencia pareada de `input_tokens` frente a B. El valor teórico E es 91,5; el primer número entero que supera el equilibrio es aproximadamente 92 respuestas. En sesiones cortas D o C tienen mejor efecto neto; si el contexto de skill queda cacheado entre turnos, el coste efectivo puede bajar.

## Winner / Ganador

`D — token-rat + codebook` maximiza ahorro (12,4%) y reduce overhead. `E — full` es el resultado integrado solicitado: 10,9%, fidelidad 1,000, integridad 100%. SMS aporta 6,4% por separado, pero no potencia el codebook; debe mantenerse simple.

## Findings / Hallazgos

- Menos caracteres no implica menos tokens: `pq`, `pa`, `tmb` y `fail` no mejoran.
- `cfg` no supera `config`; `beh` ahorra, pero no compensa la pérdida de lectura.
- Codebook concentra la mayor parte del beneficio.
- El holdout adversarial expuso omisiones de literales en B; E conservó todos tras reforzar una instrucción ambigua.
- Limitación: 80 casos usan estados operativos controlados para medir frecuencia; los 20 holdout diversos reducen overfitting, pero no sustituyen conversaciones reales largas.

## Examples / Ejemplos

1. Normal: `solo se realizó el ajuste solicitado... comportamiento previo intacto; no hubo refactor...`  
   Token-rat: `solo se realizó el ajuste solicitado... comportamiento previo permanece intacto...`  
   SMS: `lorem`

2. Normal: `el cambio solicitado está completo y todas las pruebas nombradas han pasado`  
   Token-rat: `cambio solicitado completado. Todos los tests indicados pasaron.`  
   SMS: `Cambio completado. testok`

3. Normal: `validación estática pasó; falta validación en ejecución; resultado parcial`  
   Token-rat: `resultado parcial... falta validación runtime`  
   SMS: `partial runtime?`

4. Normal: `evidencia insuficiente para una conclusión con confianza`  
   Token-rat: `evidencia insuficiente...`  
   SMS: `evidence?`

5. Normal: `trabajo bloqueado porque la dependencia indicada no está disponible`  
   Token-rat: `trabajo bloqueado... dependencia no disponible`  
   SMS: `blocked:dependencia no disponible`

6. Normal: `hay una vía de rollback probada disponible, pero no se ejecutó`  
   Token-rat: `rollback probado y disponible, pero no ejecutado`  
   SMS: `rollback; no ejecutado`

## Verdict / Veredicto

`WIN`: E reduce 10,9% adicional sobre B, con fidelity 1,000 e integridad técnica 100%; D es la opción óptima cuando importa también el overhead de entrada.

## Reproduction / Repetición

```bash
python scripts/bench_sms_esp_rat.py --phase smoke --max-calls 30 --reasoning low
python scripts/bench_sms_esp_rat.py --phase dev --max-calls 150 --reasoning low
python scripts/bench_sms_esp_rat.py --phase final --max-calls 500 --reasoning low
```
