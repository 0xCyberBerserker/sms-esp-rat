#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/bench_sms_esp_rat.py"
SPEC = importlib.util.spec_from_file_location("bench_sms_esp_rat", SCRIPT)
BENCH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(BENCH)


class IntegrityTests(unittest.TestCase):
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

    def test_fidelity_requires_all_groups(self):
        case = {"required_any": [["passed", "testok"], ["runtime?"]]}
        self.assertEqual(BENCH.fidelity(case, "testok runtime?", True), 1.0)
        self.assertEqual(BENCH.fidelity(case, "testok", True), 0.5)


if __name__ == "__main__":
    unittest.main()
