# Astra benchmark report / Informe del benchmark Astra

This is an exploratory result, not evidence of semantic equivalence or lower end-to-end cost. En este corpus sintético, las salidas registradas de E consumieron un 10,92 % menos tokens que B; la preservación semántica y el ahorro neto requieren validación adicional.

## Setup / Configuración

- Model / modelo: `gpt-6-astra`; reasoning: `low`.
- Invocation / invocación: `codex exec --ignore-user-config --ephemeral --skip-git-repo-check --sandbox read-only --model gpt-6-astra -c 'model_reasoning_effort="low"' --json -`.
- Official `turn.completed` fields: `input_tokens`, `output_tokens`, `cached_input_tokens`.
- Variants: A baseline; B `token-rat-esp`; C B + SMS; D B + codebook; E full pipeline.
- Corpus: 100 synthetic prompts: 50 training, 25 validation, and 25 legacy holdout cases. The first 80 share repeated operational templates; four labelled conversations are simulated as single prompts, not real multi-turn sessions.

The historical rows did not record an explicit baseline commit or retain the full event stream. A forensic check recomputed the harness-v1 content-addressed keys using the corpus at public project commit `77de242f3e0af56f2aac3395b8e5af17a26b88a9` and the `token-rat-esp` instruction at public commit `55f78f1d2f599bd73727f75ae04adfe564859bae`: all 100 B keys matched. This indirectly ties B to that exact instruction content, but it does not recover the missing original events. Future runs use the [pinned public snapshot](../references/baselines/README.md) directly and record the complete instruction hash in every new row.

## Recorded outputs / Salidas registradas

| Variant | Output tokens | vs A | vs B | Heuristic coverage | Integrity failures | Semantic-rule violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A baseline | 9,550 | 0.0% | -23.8% | 0.930 | 0 | 0 |
| B token-rat | 7,714 | 19.2% | 0.0% | 0.933 | 2 | 0 |
| C token-rat + SMS | 7,223 | 24.4% | 6.4% | 0.963 | 0 | 0 |
| D token-rat + codebook | 6,760 | 29.2% | 12.4% | 0.973 | 0 | 0 |
| E full | 6,872 | 28.0% | 10.9% | 1.000 | 0 | 0 |

For B→E, the recorded output difference is 842 tokens, or 8.42 per response. E median/p90 output was 67/85 tokens. Eleven cases became longer.

The evaluator is deliberately labelled **heuristic coverage**. It checks protected literals, required lexical groups, canonical macro expansions, and a small set of explicit semantic relations. A score of 1.000 is not proof that meaning was preserved.

B also has two protected-literal integrity failures, so B and E are not demonstrated quality-matched systems. The 10.92% figure is strictly a comparison of their recorded output-token totals.

## Split analysis / Análisis por partición

| Split | B output | E output | B→E reduction |
| --- | ---: | ---: | ---: |
| Training | 4,385 | 3,876 | 11.61% |
| Validation | 2,114 | 1,846 | 12.68% |
| Legacy holdout | 1,215 | 1,150 | 5.35% |
| Combined | 7,714 | 6,872 | 10.92% |

The legacy holdout was inspected and used while tuning evaluator rules and prompts. It is therefore contaminated and cannot support a confirmatory generalization claim. The 10.92% headline combines all three splits; 5.35% is the descriptive result for the legacy holdout alone.

## Input and total tokens / Tokens de entrada y totales

| Variant | Input tokens | Total tokens | Characters | Words |
| --- | ---: | ---: | ---: | ---: |
| A | 2,580,124 | 2,589,674 | 23,541 | 2,798 |
| B | 2,530,508 | 2,538,222 | 22,250 | 2,665 |
| C | 2,535,969 | 2,543,192 | 20,441 | 2,236 |
| D | 2,568,441 | 2,575,201 | 19,556 | 2,174 |
| E | 2,607,555 | 2,614,427 | 18,029 | 1,993 |

In the independent-call benchmark, E used 77,047 more input tokens than B. After subtracting the 842-output-token saving, E used 76,205 more total tokens, a 3.00% increase over B. Monetary cost cannot be inferred without input/output prices and cache-billing rules:

$$
C_v=p_I I_v+p_O O_v
$$

## Conditional break-even model / Modelo condicional de break-even

If instruction overhead were paid once and reused unchanged across a session, a hypothetical model would be:

$$
N_v^*=\frac{h_v}{s_v}
$$

For E, $770.47/8.42=91.50$, conventionally rounded up to 92 responses. This is not an empirical benchmark result: every recorded case was an independent invocation that included the instructions again. Actual multi-turn context reuse, caching, latency, and billing were not tested.

## Ablation interpretation / Interpretación de la ablación

C, D, and E use different prompts and only one recorded generation per case. D produced 112 fewer output tokens than E in this sample. This is descriptive, not a causal estimate that isolates SMS, codebook, or their interaction; there are no repetitions, confidence intervals, or uncertainty estimates.

## Evaluator correction / Corrección del evaluador

Four counterexamples showed that the earlier lexical evaluator could award a perfect score to incorrect meaning: inverted configuration status, an executed rollback, a prohibited installation recommendation, and `101ms < 100ms`. The harness now includes explicit regression tests for these relations and rescored all saved result files with zero new Astra calls. Natural Spanish formulations are also accepted without requiring benchmark-specific aliases.

Remaining limitation: the new checks cover the known counterexamples, not unrestricted semantic equivalence. A future confirmatory run needs an unseen frozen corpus, real multi-turn conversations, repeated samples, retained raw events, and semantic assessment independent of prompt tuning.

## Codebook probe / Probe del codebook

Exact-echo pairs estimate alias-versus-expansion token differences; fixed framing cancels only in the paired subtraction. These estimates rank candidates but do not prove end-to-end savings. `lorem` remains reserved for “minimal requested change, everything else intact, no extra refactor or scope.” The rollback macro means tested **and** available, and not executed.

## Experiment accounting / Contabilidad del experimento

- Harness Astra calls: 794; initial linkage calls: 2; reported total: 796.
- Final cache: 794 entries; historical final replay: 495 hits and 5 calls.
- Harness usage: 20,380,580 input tokens and 58,748 output tokens; 12,696,192 input tokens reported cached.
- The corrective rescore made zero Astra calls.

## Verdict / Veredicto

**Evidence-bounded claim:** In this synthetic corpus, the recorded E outputs used 10.92% fewer tokens than B. Semantic preservation and net savings require additional validation.

**Afirmación acotada por la evidencia:** En este corpus sintético, las salidas registradas de E consumieron un 10,92 % menos tokens que B. La preservación semántica y el ahorro neto requieren validación adicional.

## Reproduction / Reproducción

```bash
python scripts/build_corpus.py
python -m unittest discover -s tests -v
python scripts/bench_sms_esp_rat.py --rescore results/final.jsonl
python scripts/bench_sms_esp_rat.py --phase smoke --max-calls 30 --reasoning low
python scripts/bench_sms_esp_rat.py --phase dev --max-calls 150 --reasoning low
python scripts/bench_sms_esp_rat.py --phase final --max-calls 500 --reasoning low
```

The equations and assumptions are explained in [the mathematical model](../docs/modelo-matematico.md).
