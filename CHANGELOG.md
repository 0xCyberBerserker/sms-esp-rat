# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [Unreleased]

### Added

- Initial `sms-esp-rat` skill with safe, normal, and max modes.
- Shared semantic codebook with reserved `lorem` macro.
- Authorship clarification: the project author created `lorem` following an initial suggestion from Miguel Ángel Díaz Oliva.
- GitHub banner, social preview asset, discoverability metadata, and publication checklist.
- MIT license and public installation URLs for the paired skills.
- Astra benchmark with measured usage, cache/resume, integrity checks, corpus splits, and A/B/C/D/E variants.
- Bilingual mathematical model with equations and worked benchmark examples.
- Semantic-relation regression tests for configuration state, rollback execution, prohibited installation, and numeric comparison.
- Pinned public `token-rat-esp` baseline snapshot and per-row instruction provenance for future runs.

### Changed

- Renamed the evaluator metric from semantic fidelity to heuristic claim coverage.
- Reframed the benchmark as exploratory, disclosed holdout contamination and baseline-provenance limits, and separated output-token reduction from total-token cost.
- Rescored saved results without new Astra calls.

---

# Registro de cambios

Los cambios relevantes siguen Keep a Changelog y Versionado Semántico.

## [Sin publicar]

### Añadido

- Skill inicial, codebook semántico, benchmark Astra reproducible y pruebas de integridad.
- Aclaración de autoría: el autor del proyecto creó `lorem` tras una sugerencia inicial de Miguel Ángel Díaz Oliva.
- Banner, vista previa social, metadatos de descubrimiento y checklist de publicación para GitHub.
- Licencia MIT y URLs públicas de instalación para las dos skills.
- Modelo matemático bilingüe con ecuaciones y ejemplos resueltos del benchmark.
- Pruebas de regresión de relaciones semánticas para estado de configuración, ejecución de rollback, instalación prohibida y comparación numérica.
- Snapshot público fijado de `token-rat-esp` y procedencia de instrucciones por fila para futuras ejecuciones.

### Cambiado

- Renombrada la métrica del evaluador: de fidelidad semántica a cobertura heurística de afirmaciones.
- Reformulado el benchmark como exploratorio; se documentan la contaminación del holdout, los límites de procedencia del baseline y la diferencia entre reducción de salida y coste total.
- Resultados guardados reevaluados sin nuevas llamadas a Astra.
