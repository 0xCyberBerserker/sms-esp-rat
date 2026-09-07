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
| (K_{i,v}) | Heuristic claim-coverage score in ([0,1]) |
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

### Split sensitivity

The combined 10.92% is not a holdout estimate. The recorded B→E reductions were 11.61% on training, 12.68% on validation, and 5.35% on the legacy holdout. That holdout was inspected during tuning, so it is contaminated and descriptive only.

## 4. Heuristic claim coverage

Each case defines (m_i) required semantic groups. If (h_{i,v}) groups are represented correctly:

$$
K_{i,v}=\frac{h_{i,v}}{m_i}
$$

If no explicit claim groups exist, coverage defaults to 1 after technical integrity passes. Known macros are evaluated using their canonical expansion, so `lorem` counts as its complete meaning rather than as an unexplained word. Explicit relation checks reject a small set of known contradictions.

Aggregate coverage is the arithmetic mean:

$$
\bar K_v=\frac{1}{n}\sum_{i=1}^{n}K_{i,v}
$$

This is a deterministic lexical and rule-based diagnostic, not a semantic-equivalence metric. A value of 1 does not prove preservation of meaning. The checks were improved after observing counterexamples, so their result is not independent confirmatory evidence.

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

The estimate ranks candidates; recorded output-token differences remain the descriptive measure for this sample because model phrasing is not perfectly additive.

### Exact-echo framing

The probe observes a fixed response overhead (k):

$$
M(x)=k+\tau(x)
$$

where $\tau(x)$ is the model token cost of string $x$. Paired subtraction cancels that framing:

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

Percentage differences over B are 6.4%, 12.4%, and 10.9%, respectively. D produced 112 fewer output tokens than E in this one-sample corpus.

A descriptive interaction term is:

$$
J=S_{\mathrm{full}}-(S_{\mathrm{SMS}}+S_{\mathrm{codebook}})
$$

$$
J=842-(491+954)=-603
$$

The negative value is descriptive only. The prompts are not an exact controlled factorial intervention, generation is nonlinear, and there is one sample per cell. Therefore it does not isolate causal overlap or interference.

## 8. Input overhead and break-even

For candidate (v) relative to B, mean input overhead is:

$$
h_v=\frac{1}{n}\sum_{i=1}^{n}(I_{i,v}-I_{i,B})
$$

Mean output saving is:

$$
s_v=\frac{1}{n}\sum_{i=1}^{n}(O_{i,B}-O_{i,v})
$$

If, hypothetically, the instruction overhead were paid once and reused across a session, approximate net saving after (N) responses would be:

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

Under that assumption, the first whole response beyond break-even would be 92. Analogous conditional values are about 12 for C and 40 for D.

These are not empirical break-even results. The CLI benchmark used independent invocations and reloaded the instructions each time. It did not measure a multi-turn session, context reuse, cache billing, or stable per-session overhead.

The observed aggregate comparison is instead:

$$
\Delta I_{B\rightarrow E}=2{,}607{,}555-2{,}530{,}508=77{,}047
$$

$$
\Delta T_{B\rightarrow E}=2{,}614{,}427-2{,}538{,}222=76{,}205
$$

$$
100\times\frac{76{,}205}{2{,}538{,}222}=3.002\%\approx3.00\%
$$

Thus E used fewer output tokens but more input-plus-output tokens in this run. Monetary cost needs separate input and output prices:

$$
C_v=p_I I_v+p_O O_v
$$

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
| (K_{i,v}) | Cobertura heurística de afirmaciones en ([0,1]) |
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

### Sensibilidad por partición

El 10,92 % combinado no es una estimación de holdout. Las reducciones B→E registradas fueron 11,61 % en training, 12,68 % en validation y 5,35 % en el holdout heredado. Ese holdout se inspeccionó durante el ajuste, por lo que está contaminado y solo permite una descripción.

## 4. Cobertura heurística e integridad

Si un caso define (m_i) grupos semánticos obligatorios y la salida conserva (h_{i,v}):

$$
K_{i,v}=\frac{h_{i,v}}{m_i}
\qquad
\bar K_v=\frac{1}{n}\sum_{i=1}^{n}K_{i,v}
$$

Las macros se evalúan mediante su expansión canónica. Por ejemplo, `lorem` cuenta como sus tres afirmaciones completas. Algunas relaciones conocidas tienen reglas explícitas contra contradicciones.

Esta métrica es un diagnóstico léxico y basado en reglas, no una medida de equivalencia semántica. Un valor 1 no demuestra que el significado se haya preservado. Además, las reglas se corrigieron tras observar contraejemplos, por lo que no constituyen evidencia confirmatoria independiente.

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

D produjo 112 output tokens menos que E en esta única muestra. La interacción descriptiva es:

$$
J=S_{\mathrm{full}}-(S_{\mathrm{SMS}}+S_{\mathrm{codebook}})
=842-(491+954)=-603
$$

El valor no aísla causalmente solapamiento o interferencia: los prompts no forman una intervención factorial controlada, la generación es no lineal y solo hay una muestra por celda.

## 7. Overhead y break-even

$$
h_v=\frac{1}{n}\sum_{i=1}^{n}(I_{i,v}-I_{i,B})
$$

$$
s_v=\frac{1}{n}\sum_{i=1}^{n}(O_{i,B}-O_{i,v})
$$

Si, hipotéticamente, el overhead de instrucciones se pagase una vez y se reutilizase durante (N) respuestas:

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

Bajo esa hipótesis, el primer entero posterior al equilibrio sería 92. Los valores condicionales análogos serían unas 12 respuestas para C y 40 para D.

No son break-even empíricos. El benchmark usó invocaciones independientes y volvió a cargar las instrucciones en cada una; no midió una sesión multiturno, reutilización de contexto, facturación de caché ni overhead estable por sesión.

La comparación agregada observada es:

$$
\Delta I_{B\rightarrow E}=2\,607\,555-2\,530\,508=77\,047
$$

$$
\Delta T_{B\rightarrow E}=2\,614\,427-2\,538\,222=76\,205
$$

$$
100\times\frac{76\,205}{2\,538\,222}=3{,}002\%\approx3{,}00\%
$$

Por tanto, E usó menos tokens de salida, pero más tokens totales de entrada más salida. El coste monetario requiere precios separados:

$$
C_v=p_I I_v+p_O O_v
$$

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
