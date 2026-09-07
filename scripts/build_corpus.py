#!/usr/bin/env python3
"""Build the deterministic 100-case benchmark corpus."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CATEGORIES = [
    "debugging", "linux", "shell", "programming", "git", "devops", "infrastructure",
    "code-review", "error-analysis", "architecture", "technical-docs", "security",
    "logs", "multiphase", "simple-question", "llm-boilerplate", "execution-status",
    "tests", "builds", "uncertainty",
]

STATES = [
    ("minimal", "Only the requested adjustment was made; previous behavior remains intact; no refactor or unrelated change occurred.", [["lorem", "only", "únicamente"], ["intact", "conserv"], ["refactor"]]),
    ("tests", "The requested change is complete and every named test passed.", [["testok", "test", "prueba"], ["pass", "correct", "ok"]]),
    ("build", "The requested change is complete and the named build passed; tests were not run.", [["buildok", "build", "compil"], ["no", "not", "sin"]]),
    ("partial", "Static validation passed, but runtime validation is still missing, so the result is partial.", [["partial", "parcial", "incomplet"], ["runtime?", "runtime", "ejecución"]]),
    ("evidence", "Evidence is insufficient for a confident conclusion; no change was made.", [["evidence?", "evidencia", "prueba"], ["insuficient", "falta"], ["no"]]),
    ("blocked", "Work is blocked because the named dependency is unavailable; no workaround was applied.", [["blocked", "bloque"], ["dependenc"], ["no"]]),
    ("probable", "The stated cause is probable but not confirmed; give the next exact check.", [["cause?", "probable", "posible"], ["no", "not", "sin confirmar"], ["check", "comprobar", "ejecut"]]),
    ("confirmed", "The stated cause is confirmed by the supplied error; give the exact fix.", [["cause!", "confirm"], ["fix", "corre", "solución"]]),
    ("rollback", "The operation succeeded and a tested rollback path is available but was not executed.", [["rollback", "revers"], ["no", "not", "sin ejecutar"]]),
    ("skip", "The destructive operation was deliberately skipped because authorization was absent.", [["skip", "omit", "no se ejecut"], ["autoriz", "permiso"]]),
]

COMMANDS = [
    "pytest -q tests/test_auth.py", "systemctl status sshd", "git diff --check",
    "journalctl -u api.service -n 50", "curl http://127.0.0.1:8765/healthz",
    "npm run build", "cargo test parser", "docker compose config",
    "python -m unittest tests.test_integrity", "rg -n 'enabled' config/app.toml",
]

DIVERSE_CASES = [
    ("git-adversarial", "Report that dry-run succeeded, but no destructive action ran. Preserve both `--force` and `--no-force`; recommend `git push --dry-run` next.", ["--force", "--no-force", "git push --dry-run"], [["no", "sin"], ["dry-run"]]),
    ("linux-runtime", "Static unit validation passed for `backup.timer`, but runtime behavior after `systemctl daemon-reload` is unverified. Give a partial status.", ["backup.timer", "systemctl daemon-reload"], [["partial", "parcial"], ["runtime?", "runtime", "ejecución"]]),
    ("security", "Evidence links the crash to `CVE-2026-12345`, but exploitability is only probable, not confirmed. Next check is `cargo test parser_overflow`.", ["CVE-2026-12345", "cargo test parser_overflow"], [["probable", "cause?"], ["no confirm", "sin confirmar"]]),
    ("configuration", "State that `enabled=true` is active and `enabled=false` is not active. Do not collapse or invert either value. File: `/etc/lab/feature.toml`.", ["enabled=true", "enabled=false", "/etc/lab/feature.toml"], [["activo", "active"], ["no", "inactiv"]]),
    ("versions", "The regression exists in `v2.4.10`, not `v2.4.9`; commit `a1b2c3d4e5f6` is the first bad revision. Give the exact bisect command `git bisect bad a1b2c3d4e5f6`.", ["v2.4.10", "v2.4.9", "a1b2c3d4e5f6", "git bisect bad a1b2c3d4e5f6"], [["regresi", "fallo"], ["no", "not"]]),
    ("error-analysis", "Confirmed cause: literal error `Connection refused: 127.0.0.1:5432`. The service `postgresql.service` is inactive. Give `systemctl start postgresql.service` as next action.", ["Connection refused: 127.0.0.1:5432", "postgresql.service", "systemctl start postgresql.service"], [["confirm", "cause!"], ["inactiv"]]),
    ("units", "Latency limit is `100ms`; observed p90 is `101ms`, so the check failed. Preserve both numbers and the inequality.", ["100ms", "101ms"], [["fail", "fall"], ["p90"]]),
    ("rollback", "Deployment `release-2026.09.07` succeeded. Rollback `deployctl rollback release-2026.09.07` was tested and is available, but was not executed.", ["release-2026.09.07", "deployctl rollback release-2026.09.07"], [["rollback"], ["no", "not", "sin ejecutar"]]),
    ("dependency", "Work is blocked because package `libfoo.so.3` is absent. Do not suggest installing it; exact check: `ldconfig -p | rg libfoo.so.3`.", ["libfoo.so.3", "ldconfig -p | rg libfoo.so.3"], [["blocked", "bloque"], ["absent", "falta", "ausente", "no disponible"]]),
    ("scope", "A one-line null check was added in `src/parser.py`; API behavior is unchanged and no refactor or other file change occurred. Test `pytest -q tests/test_parser.py` passed.", ["src/parser.py", "pytest -q tests/test_parser.py"], [["lorem", "null check", "check de nulo", "comprobación de nulos"], ["lorem", "api sin cambios", "api mantiene", "api behavior is unchanged"], ["lorem", "sin refactor", "no refactor"], ["testok", "test", "prueba", "pass"]]),
    ("conversation-context", "Previous user: 'Did the build and tests pass?' Previous assistant: 'Build passed; tests were not run.' Now answer whether everything passed, preserving `build=passed` and `tests=not-run`.", ["build=passed", "tests=not-run"], [["build", "buildok"], ["no", "not"]]),
    ("conversation-context", "Previous turn established that `/api/v2/items` returns `HTTP 204`. The user now asks whether the body was validated. Mention exact endpoint `/api/v2/items`: no body exists for `HTTP 204`; do not claim JSON validation.", ["/api/v2/items", "HTTP 204"], [["no"], ["body", "cuerpo"]]),
    ("conversation-context", "Earlier, cause A was ruled out and cause B remained probable. Now report: `DNS` is not the cause; `MTU=1280` is still only a hypothesis. Next check: `ping -M do -s 1252 10.0.0.1`.", ["DNS", "MTU=1280", "ping -M do -s 1252 10.0.0.1"], [["no", "descartad"], ["probable", "hipótesis", "cause?"]]),
    ("conversation-context", "Previous step changed only `timeout=30`; user asks if retries changed. Answer that `retries=3` remains unchanged and no other config changed. File `/srv/api/config.ini`.", ["timeout=30", "retries=3", "/srv/api/config.ini"], [["no", "sin", "ningún", "ninguna"], ["intact", "unchanged", "sin cambios"]]),
    ("structured-data", "Repeat this JSON exactly, then state that validation passed: ```json\n{\"enabled\": false, \"limit\": 10}\n```", ["```json\n{\"enabled\": false, \"limit\": 10}\n```"], [["pas", "correct", "ok"]]),
    ("network", "Endpoint `https://example.invalid/api?q=a%2Fb` returned `HTTP 503`; fallback `http://10.0.0.9:8080/health` was deliberately not used.", ["https://example.invalid/api?q=a%2Fb", "HTTP 503", "http://10.0.0.9:8080/health"], [["no", "not", "sin usar"], ["503", "fail", "error"]]),
    ("filesystem", "File `/srv/app/config.yaml` exists; `/srv/app/config.yml` does not. Exact command: `test -f /srv/app/config.yaml`.", ["/srv/app/config.yaml", "/srv/app/config.yml", "test -f /srv/app/config.yaml"], [["exist"], ["no"]]),
    ("formal-boundary", "Write one compact but formal sentence for a third party: validation is partial because approval ID `APP-2048` is pending; no deployment occurred.", ["APP-2048"], [["partial", "parcial"], ["no"]]),
    ("numeric-boundary", "Allowed range is `0 <= retries <= 5`; observed `retries=6`, therefore configuration is invalid. Check `appctl validate --strict`.", ["0 <= retries <= 5", "retries=6", "appctl validate --strict"], [["inválid", "invalid", "fail"]]),
    ("multiphase", "Phase 1 tests passed; phase 2 build passed; phase 3 runtime check was skipped due to missing authorization. Commands: `pytest -q`, `npm run build`, `deployctl verify --prod`.", ["pytest -q", "npm run build", "deployctl verify --prod"], [["pas", "testok"], ["build", "buildok"], ["skip", "omit", "no"]]),
]

SEMANTIC_CHECKS = {
    "configuration": {
        "all_regex": [
            r"enabled=true(?:(?!enabled=false).){0,80}\bactivo\b",
            r"enabled=false(?:(?!enabled=true).){0,80}(?:\binactivo\b|\bno(?:\s+\w+){0,2}\s+activo\b)",
        ],
    },
    "units": {
        "all_regex": [
            r"(?:101ms`?\s*>\s*(?:\w+\s+){0,3}`?100ms|101ms(?:(?!100ms).){0,60}(?:supera|excede|mayor).*100ms)",
        ],
    },
    "rollback": {
        "all_regex": [
            r"\brollback\b.{0,160}\bprobad",
            r"(?:\bno\b(?:\s+\w+){0,2}\s+ejecutad|\bsin\s+ejecutar)",
        ],
        "forbidden_raw_regex": [
            r"\brollback\b(?:(?!\bno\b|\bsin\b).){0,80}\bejecut\w*\b",
        ],
    },
    "dependency": {
        "forbidden_regex": [
            r"\b(?:debes|debe|conviene|recomiendo|recomendamos)\s+instalar",
            r"(?<!\bno )\binstalalo\b",
            r"\binstall it\b",
        ],
    },
}


def make_case(index: int) -> dict:
    if index >= 80:
        category, prompt, protected, required = DIVERSE_CASES[index - 80]
        return {
            "id": f"case-{index:03d}-diverse", "split": "holdout", "category": category,
            "prompt": "Answer in concise technical Spanish. " + prompt,
            "protected": protected, "required_any": required,
            "semantic_checks": SEMANTIC_CHECKS.get(category, {}),
        }
    category = CATEGORIES[index % len(CATEGORIES)]
    state, fact, required = STATES[index % len(STATES)]
    command = COMMANDS[index % len(COMMANDS)]
    version = f"v{1 + index % 4}.{index % 10}.{index % 7}"
    path = f"/srv/lab-{index:03d}/config.yaml"
    flag = "--no-force" if index % 2 else "--force"
    address = f"10.20.{index // 254}.{1 + index % 254}:8443"
    split = "training" if index < 50 else "validation" if index < 75 else "holdout"
    prompt = (
        f"Write a short Spanish technical status for case {index:03d}. Facts: {fact} "
        f"Mention the exact check `{command}`, path `{path}`, version `{version}`, flag `{flag}`, "
        f"and endpoint `{address}`. Preserve literals, negation, certainty, and conditions exactly."
    )
    return {
        "id": f"case-{index:03d}-{state}", "split": split, "category": category,
        "prompt": prompt,
        "protected": [f"`{command}`", f"`{path}`", f"`{version}`", f"`{flag}`", f"`{address}`"],
        "required_any": required,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    cases = [make_case(index) for index in range(100)]
    for split in ("training", "validation", "holdout"):
        rows = [case for case in cases if case["split"] == split]
        (DATA / f"{split}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
    (DATA / "smoke.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in cases[:10]),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
