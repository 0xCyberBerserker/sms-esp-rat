# Architecture

```mermaid
flowchart LR
    A[Raw answer] --> B[token-rat-esp semantic pruning]
    B --> C[sms-esp-rat protected-region scan]
    C --> D[Telegraphic layer]
    D --> E[Semantic codebook]
    E --> F[Integrity and fidelity check]
    F --> G[Final answer]
```

`SKILL.md` contains routing and safety invariants. `references/codebook.md` is the shared vocabulary. The stdlib benchmark invokes Astra through `codex exec --json`, caches content-addressed results, and writes measured raw rows plus a summary. Corpus splits are immutable inputs; holdout is used only in `final`.

The equations behind savings, fidelity, integrity, ablation, and break-even are defined in [docs/modelo-matematico.md](docs/modelo-matematico.md).

Trust boundary: generated natural language may change; protected technical literals may not. Any missing protected item is an integrity failure.

---

# Arquitectura

`SKILL.md` contiene el enrutado y los invariantes. `references/codebook.md` define el vocabulario compartido. El benchmark stdlib invoca Astra mediante `codex exec --json`, cachea por contenido y genera resultados brutos medidos y un resumen. El holdout solo se usa en `final`.

Las ecuaciones de ahorro, fidelidad, integridad, ablación y break-even se explican en [docs/modelo-matematico.md](docs/modelo-matematico.md).

El lenguaje natural puede comprimirse; los literales técnicos protegidos no pueden cambiar. La ausencia de uno implica fallo de integridad.
