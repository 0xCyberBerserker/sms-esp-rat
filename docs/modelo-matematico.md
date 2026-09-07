# Mathematical model

This document defines the equations used to interpret the `sms-esp-rat` benchmark. Measured values come from Astra through the official `codex exec --json` usage fields.

## 1. Symbols

For case (i) and variant (v):

| Symbol | Meaning |
| --- | --- |
| (I_{i,v}) | Input tokens |
| (O_{i,v}) | Output tokens |
| (T_{i,v}) | Total tokens: input plus output |
| (C_{i,v}) | Output characters |
| (W_{i,v}) | Output words |
| (L_{i,v}) | Latency in seconds |
| (F_{i,v}) | Semantic fidelity score in ([0,1]) |
| (H_{i,v}) | Technical integrity indicator: 1 if preserved, 0 otherwise |

The benchmark variants are:

- (A): baseline.
- (B): `token-rat-esp`.
- (C): (B) plus telegraphic SMS rules.
- (D): (B) plus semantic codebook.
- (E): full pipeline, SMS plus codebook.

## 2. Token totals

For one result:

$$
T_{i,v}=I_{i,v}+O_{i,v}
$$

For (n) cases, the aggregate output is:

$$
O_v^{\mathrm{total}}=\sum_{i=1}^{n}O_{i,v}
$$

The arithmetic mean is:

$$
\bar O_v=\frac{1}{n}\sum_{i=1}^{n}O_{i,v}
$$

The median, or p50, is the central ordered value. The p90 is the value below which 90% of observations fall. Percentiles show typical and high-output behavior without allowing a few long answers to dominate the result.

## 3. Absolute and percentage savings

Using reference variant (r), the absolute output-token saving is:

$$
\Delta O_{i,r\rightarrow v}=O_{i,r}-O_{i,v}
$$

- Positive: variant (v) saves tokens.
- Zero: no change.
- Negative: variant (v) produces more tokens.

The aggregate reduction percentage is:

$$
R_{r\rightarrow v}=100\times
\frac{O_r^{\mathrm{total}}-O_v^{\mathrm{total}}}
{O_r^{\mathrm{total}}}
$$

The output ratio is:

$$
Q_{r\rightarrow v}=\frac{O_v^{\mathrm{total}}}{O_r^{\mathrm{total}}}
$$

A ratio of (0.80) means the candidate uses 80% of the reference output tokens, equivalent to a 20% reduction.

### Measured example: B to E

$$
R_{B\rightarrow E}=100\times\frac{7714-6872}{7714}
=10.915\%\approx10.9\%
$$

Thus, full `sms-esp-rat` saved 842 output tokens over 100 responses, or 8.42 tokens per response on average.

### Measured example: A to E

$$
R_{A\rightarrow E}=100\times\frac{9550-6872}{9550}
=28.042\%\approx28.0\%
$$

This measures the full pipeline reduction rather than the incremental contribution of `sms-esp-rat`.

## 4. Fidelity

Each case defines (m_i) required semantic groups. If (h_{i,v}) groups are represented correctly:

$$
F_{i,v}=\frac{h_{i,v}}{m_i}
$$

If no explicit semantic groups exist, fidelity defaults to 1 after technical integrity passes. Known macros are evaluated using their canonical expansion, so `lorem` counts as its complete meaning rather than as an unexplained word.

Aggregate fidelity is the arithmetic mean:

$$
\bar F_v=\frac{1}{n}\sum_{i=1}^{n}F_{i,v}
$$

This is a deterministic reconstruction proxy, not a universal semantic metric. GPT-5.6 review of anomalies complements it.

## 5. Technical integrity

Let (P_i) be the set of protected literals in case (i), and (Y_{i,v}) the generated output. Then:

$$
H_{i,v}=
\begin{cases}
1,& \text{if every }p\in P_i\text{ appears unchanged in }Y_{i,v}\\
0,& \text{otherwise}
\end{cases}
$$

An integrity failure is a hard failure regardless of token savings:

$$
H_{i,v}=0\Longrightarrow\mathrm{result}_{i,v}=\mathrm{FAIL}
$$

Protected values include commands, flags, paths, URLs, hashes, versions, IDs, addresses, ports, numbers, code, and structured literals.

## 6. Macro gain

For macro (j):

| Symbol | Meaning |
| --- | --- |
| (e_j) | Tokens in the canonical expansion |
| (a_j) | Tokens in the alias |
| (f_j) | Observed frequency |

Unit gain:

$$
g_j=e_j-a_j
$$

Estimated total gain:

$$
G_j=f_j\times g_j
$$

For `lorem`, (e=25), (a=6), and (f=9):

$$
g_{\text{lorem}}=25-6=19
$$

$$
G_{\text{lorem}}=9\times19=171\text{ tokens}
$$

The estimate ranks candidates; actual end-to-end savings remain authoritative because model phrasing is not perfectly additive.

### Exact-echo framing

The probe observes a fixed response overhead (k):

$$
M(x)=k+\tau(x)
$$

where (	au(x)) is the model token cost of string (x). Paired subtraction cancels that framing:

$$
M(\mathrm{expansion})-M(\mathrm{alias})
=\tau(\mathrm{expansion})-\tau(\mathrm{alias})
$$

Therefore the measured unit gain is reliable even if displayed exact-echo totals include fixed framing.

## 7. Ablation study

The isolated component savings are:

$$
S_{\mathrm{SMS}}=O_B^{\mathrm{total}}-O_C^{\mathrm{total}}
=7714-7223=491
$$

$$
S_{\mathrm{codebook}}=O_B^{\mathrm{total}}-O_D^{\mathrm{total}}
=7714-6760=954
$$

$$
S_{\mathrm{full}}=O_B^{\mathrm{total}}-O_E^{\mathrm{total}}
=7714-6872=842
$$

Percentage contributions over B are 6.4%, 12.4%, and 10.9%, respectively. Because D beats E by 112 output tokens, the mechanisms do not combine additively in this corpus.

A descriptive interaction term is:

$$
J=S_{\mathrm{full}}-(S_{\mathrm{SMS}}+S_{\mathrm{codebook}})
$$

$$
J=842-(491+954)=-603
$$

The negative value indicates overlap or interference, not that SMS adds 603 tokens directly. Model generation is nonlinear, so this term is diagnostic rather than causal.

## 8. Input overhead and break-even

For candidate (v) relative to B, mean input overhead is:

$$
h_v=\frac{1}{n}\sum_{i=1}^{n}(I_{i,v}-I_{i,B})
$$

Mean output saving is:

$$
s_v=\frac{1}{n}\sum_{i=1}^{n}(O_{i,B}-O_{i,v})
$$

If the codebook is loaded once and reused across a session, approximate net saving after (N) responses is:

$$
\mathrm{Net}_v(N)=N\times s_v-h_v
$$

Break-even occurs when net saving becomes positive:

$$
N_v^{*}=\frac{h_v}{s_v}
$$

For full E:

$$
N_E^{*}=\frac{770.47}{8.42}=91.50
$$

The first whole response beyond break-even is approximately 92 responses. Corresponding measured thresholds are approximately 12 responses for C and 40 for D.

This session model is an approximation. The CLI benchmark reloads context per invocation; real multi-turn caching may lower effective overhead.

## 9. Cache and call budget

Planned calls before cache reuse are:

$$
N_{\mathrm{planned}}=N_{\mathrm{cases}}\times
N_{\mathrm{variants}}\times N_{\mathrm{repetitions}}
$$

Actual calls are:

$$
N_{\mathrm{actual}}=N_{\mathrm{planned}}-N_{\mathrm{cache\ hits}}
$$

For the final replay:

$$
N_{\mathrm{actual}}=500-500=0
$$

The cache key is conceptually:

$$
K=\mathrm{SHA256}(\mathrm{case},\mathrm{variant},\mathrm{instruction},
\mathrm{model},\mathrm{reasoning},\mathrm{harness\ version})
$$

Changing any model-relevant component invalidates only its affected entries.

---

# Modelo matemático

Este documento define las ecuaciones empleadas para interpretar el benchmark de `sms-esp-rat`. Los valores medidos proceden de Astra mediante los campos oficiales de usage de `codex exec --json`.

## 1. Símbolos

Para el caso (i) y la variante (v):

| Símbolo | Significado |
| --- | --- |
| (I_{i,v}) | Tokens de entrada |
| (O_{i,v}) | Tokens de salida |
| (T_{i,v}) | Tokens totales: entrada más salida |
| (C_{i,v}) | Caracteres de salida |
| (W_{i,v}) | Palabras de salida |
| (L_{i,v}) | Latencia en segundos |
| (F_{i,v}) | Fidelidad semántica en ([0,1]) |
| (H_{i,v}) | Integridad técnica: 1 si se preserva, 0 si falla |

Las variantes son (A) baseline, (B) `token-rat-esp`, (C) SMS, (D) codebook y (E) pipeline completo.

## 2. Totales y distribución

$$
T_{i,v}=I_{i,v}+O_{i,v}
$$

$$
O_v^{\mathrm{total}}=\sum_{i=1}^{n}O_{i,v}
\qquad
\bar O_v=\frac{1}{n}\sum_{i=1}^{n}O_{i,v}
$$

La mediana o p50 es el valor central ordenado. El p90 deja por debajo al 90% de las observaciones. Estos percentiles describen el comportamiento típico y la cola alta sin dejar que unas pocas respuestas largas dominen el resultado.

## 3. Ahorro absoluto, ratio y porcentaje

$$
\Delta O_{i,r\rightarrow v}=O_{i,r}-O_{i,v}
$$

Un valor positivo ahorra tokens; cero significa empate; uno negativo indica regresión.

$$
R_{r\rightarrow v}=100\times
\frac{O_r^{\mathrm{total}}-O_v^{\mathrm{total}}}
{O_r^{\mathrm{total}}}
$$

$$
Q_{r\rightarrow v}=\frac{O_v^{\mathrm{total}}}{O_r^{\mathrm{total}}}
$$

Ejemplo principal:

$$
R_{B\rightarrow E}=100\times\frac{7714-6872}{7714}
=10.915\%\approx10.9\%
$$

E ahorra 842 output tokens frente a B: 8,42 por respuesta. El ahorro total A→E es:

$$
R_{A\rightarrow E}=100\times\frac{9550-6872}{9550}
=28.042\%\approx28.0\%
$$

## 4. Fidelidad e integridad

Si un caso define (m_i) grupos semánticos obligatorios y la salida conserva (h_{i,v}):

$$
F_{i,v}=\frac{h_{i,v}}{m_i}
\qquad
\bar F_v=\frac{1}{n}\sum_{i=1}^{n}F_{i,v}
$$

Las macros se evalúan mediante su expansión canónica. Por ejemplo, `lorem` cuenta como sus tres afirmaciones completas.

Sea (P_i) el conjunto de literales protegidos y (Y_{i,v}) la salida:

$$
H_{i,v}=
\begin{cases}
1,& \text{si todo }p\in P_i\text{ aparece sin cambios en }Y_{i,v}\\
0,& \text{en otro caso}
\end{cases}
$$

La integridad es una puerta dura:

$$
H_{i,v}=0\Longrightarrow\mathrm{resultado}_{i,v}=\mathrm{FAIL}
$$

Ningún ahorro compensa alterar comandos, flags, rutas, URLs, hashes, versiones, IDs, direcciones, puertos, números, código o datos estructurados.

## 5. Ganancia de macros

Para la macro (j), sean (e_j) sus tokens de expansión, (a_j) sus tokens de alias y (f_j) su frecuencia:

$$
g_j=e_j-a_j
\qquad
G_j=f_j\times g_j
$$

Para `lorem`:

$$
g_{\text{lorem}}=25-6=19
$$

$$
G_{\text{lorem}}=9\times19=171\text{ tokens estimados}
$$

El probe de eco exacto incluye un framing fijo (k), pero se cancela al comparar:

$$
M(x)=k+\tau(x)
$$

$$
M(\mathrm{expansión})-M(\mathrm{alias})
=\tau(\mathrm{expansión})-\tau(\mathrm{alias})
$$

Por eso la diferencia medida es fiable aunque los totales mostrados incluyan framing.

## 6. Ablación

$$
S_{\mathrm{SMS}}=7714-7223=491\text{ tokens}=6.4\%
$$

$$
S_{\mathrm{codebook}}=7714-6760=954\text{ tokens}=12.4\%
$$

$$
S_{\mathrm{full}}=7714-6872=842\text{ tokens}=10.9\%
$$

D supera a E por 112 output tokens. La interacción descriptiva es:

$$
J=S_{\mathrm{full}}-(S_{\mathrm{SMS}}+S_{\mathrm{codebook}})
=842-(491+954)=-603
$$

El valor negativo señala solapamiento o interferencia. No significa que SMS añada directamente 603 tokens: la generación del modelo es no lineal.

## 7. Overhead y break-even

$$
h_v=\frac{1}{n}\sum_{i=1}^{n}(I_{i,v}-I_{i,B})
$$

$$
s_v=\frac{1}{n}\sum_{i=1}^{n}(O_{i,B}-O_{i,v})
$$

Si el contexto se carga una vez y se reutiliza durante (N) respuestas:

$$
\mathrm{Neto}_v(N)=N\times s_v-h_v
$$

$$
N_v^{*}=\frac{h_v}{s_v}
$$

Para E:

$$
N_E^{*}=\frac{770.47}{8.42}=91.50
$$

El primer número entero que supera el punto de equilibrio es aproximadamente 92 respuestas. Para C son unas 12; para D, unas 40. Es una aproximación de sesión: la caché real entre turnos puede reducir el overhead efectivo.

## 8. Presupuesto y caché

$$
N_{\mathrm{planificado}}=N_{\mathrm{casos}}\times
N_{\mathrm{variantes}}\times N_{\mathrm{repeticiones}}
$$

$$
N_{\mathrm{real}}=N_{\mathrm{planificado}}-N_{\mathrm{cache\ hits}}
$$

En el replay final:

$$
N_{\mathrm{real}}=500-500=0
$$

La clave conceptual de caché es:

$$
K=\mathrm{SHA256}(\mathrm{caso},\mathrm{variante},\mathrm{instrucción},
\mathrm{modelo},\mathrm{reasoning},\mathrm{versión\ del\ harness})
$$

Así, un cambio invalida únicamente las entradas afectadas.
