# Benchmark summary

Counts marked MEASURED come from Astra/Codex CLI usage.

| Variant | Calls | Output tokens | vs A | vs B | Median | p90 | Heuristic coverage | Integrity fails | Semantic violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 100 | 9550 | 0.0% | -23.8% | 86.0 | 151 | 0.930 | 0 | 0 |
| B | 100 | 7714 | 19.2% | 0.0% | 80.5 | 92 | 0.933 | 2 | 0 |
| C | 100 | 7223 | 24.4% | 6.4% | 75.0 | 89 | 0.963 | 0 | 0 |
| D | 100 | 6760 | 29.2% | 12.4% | 71.0 | 81 | 0.973 | 0 | 0 |
| E | 100 | 6872 | 28.0% | 10.9% | 67.0 | 85 | 1.000 | 0 | 0 |

Primary metric: B -> E output-token reduction on this synthetic corpus. Heuristic coverage is diagnostic only and does not prove semantic equivalence.
