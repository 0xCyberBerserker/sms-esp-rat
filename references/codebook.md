# Shared codebook

`alias = significado canónico`. Reservados como estados independientes; nunca dentro de literales.

| Alias | Canonical meaning | Category | Arguments / restrictions |
| --- | --- | --- | --- |
| `lorem` | Solo se hizo el cambio solicitado; comportamiento previo intacto; sin refactor ni cambios fuera de scope. | scope | Las 3 afirmaciones deben ser ciertas. Reservada. |
| `testok` | Todas las pruebas indicadas en la respuesta terminaron correctamente. | validación | Indicar comandos aparte si aportan evidencia. |
| `buildok` | El build indicado en la respuesta terminó correctamente. | validación | No implica tests OK. |
| `partial` | Resultado solicitado incompleto o validado solo parcialmente. | estado | Indicar qué prueba/acción falta. |
| `runtime?` | Hay checks estáticos correctos, pero falta validar el comportamiento runtime. | evidencia | `?` forma parte del alias. |
| `evidence?` | Evidencia disponible insuficiente para concluir con confianza. | evidencia | No usar para fallo confirmado. |
| `blocked:<causa>` | Progreso bloqueado por la causa literal tras `:`. | estado | Preservar causa y literales. |
| `cause?` | La causa indicada es probable, no confirmada. | diagnóstico | No elevar certeza. |
| `rollback` | Existe rollback probado y disponible; no se ejecutó. | seguridad | Las tres afirmaciones deben ser ciertas. |

El autor de este proyecto creó el modo `lorem` y su macro reservada a partir de una sugerencia inicial de [Miguel Ángel Díaz Oliva](https://dedmaphoto.vercel.app/).

## Composition

`lorem testok`: válidas ambas expansiones completas. `partial testok`: tests OK, resultado aún parcial. Usar texto si la composición oculta condición, excepción o negación.
