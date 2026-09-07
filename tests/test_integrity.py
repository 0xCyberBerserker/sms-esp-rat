#!/usr/bin/env python3
import importlib.util
import hashlib
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/bench_sms_esp_rat.py"
SPEC = importlib.util.spec_from_file_location("bench_sms_esp_rat", SCRIPT)
BENCH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(BENCH)
CASES = {
    case["id"]: case
    for path in (SCRIPT.parents[1] / "data").glob("*.jsonl")
    for line in path.read_text(encoding="utf-8").splitlines()
    if (case := json.loads(line))
}


class IntegrityTests(unittest.TestCase):
    def test_token_rat_baseline_is_pinned(self):
        prompt = BENCH.variant_prompts()["B"]
        self.assertEqual(BENCH.TOKEN_RAT_COMMIT, "55f78f1d2f599bd73727f75ae04adfe564859bae")
        self.assertEqual(
            hashlib.sha256(prompt.encode()).hexdigest(),
            "3dc590fb6f4013dbde0f711d7e5680d3e82c4c4c3c9ccc800b3b8fcf881bca61",
        )

    def test_preserves_adversarial_literals(self):
        case = {
            "prompt": "Compare `--force` and `--no-force` at /srv/app on 10.0.0.2:8443, v1.2.3.",
            "protected": ["`--force`", "`--no-force`", "/srv/app", "10.0.0.2:8443", "v1.2.3"],
        }
        ok, missing = BENCH.integrity(case, "`--force` != `--no-force`; /srv/app; 10.0.0.2:8443; v1.2.3")
        self.assertTrue(ok, missing)

    def test_detects_changed_flag(self):
        case = {"prompt": "Keep `--no-force`.", "protected": ["`--no-force`"]}
        ok, missing = BENCH.integrity(case, "Keep `--force`.")
        self.assertFalse(ok)
        self.assertEqual(missing, ["--no-force"])

    def test_heuristic_coverage_requires_all_groups(self):
        case = {"required_any": [["passed", "testok"], ["runtime?"]]}
        self.assertEqual(BENCH.heuristic_coverage(case, "testok runtime?", True), 1.0)
        self.assertEqual(BENCH.heuristic_coverage(case, "testok", True), 0.5)

    def test_rejects_inverted_configuration_relation(self):
        case = CASES["case-083-diverse"]
        output = "`enabled=true` inactivo; `enabled=false` activo. `/etc/lab/feature.toml`."
        self.assertTrue(BENCH.integrity(case, output)[0])
        self.assertEqual(BENCH.heuristic_coverage(case, output, True), 0.0)

    def test_rejects_executed_rollback(self):
        case = CASES["case-087-diverse"]
        output = "`release-2026.09.07`: rollback ejecutado con `deployctl rollback release-2026.09.07`."
        self.assertTrue(BENCH.integrity(case, output)[0])
        self.assertEqual(BENCH.heuristic_coverage(case, output, True), 0.0)

    def test_rejects_forbidden_install_recommendation(self):
        case = CASES["case-088-diverse"]
        output = "Bloqueado: falta `libfoo.so.3`; instálalo. Check: `ldconfig -p | rg libfoo.so.3`."
        self.assertTrue(BENCH.integrity(case, output)[0])
        self.assertEqual(BENCH.heuristic_coverage(case, output, True), 0.0)

    def test_rejects_inverted_numeric_relation(self):
        case = CASES["case-086-diverse"]
        output = "Check fallido: p90 `101ms < 100ms`."
        self.assertTrue(BENCH.integrity(case, output)[0])
        self.assertEqual(BENCH.heuristic_coverage(case, output, True), 0.0)

    def test_natural_language_is_not_penalized_for_missing_alias(self):
        scope = CASES["case-089-diverse"]
        scope_output = "`src/parser.py`: añadido check de nulo; API sin cambios; sin refactor. `pytest -q tests/test_parser.py` PASS."
        dependency = CASES["case-088-diverse"]
        dependency_output = "Bloqueado: falta `libfoo.so.3`. Check: `ldconfig -p | rg libfoo.so.3`."
        self.assertEqual(BENCH.heuristic_coverage(scope, scope_output, True), 1.0)
        self.assertEqual(BENCH.heuristic_coverage(dependency, dependency_output, True), 1.0)


if __name__ == "__main__":
    unittest.main()
