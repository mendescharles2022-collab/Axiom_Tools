from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_blocker_statuses.py"
REGISTRY_PATH = ROOT / "config" / "blocker_registry_v8.json"

spec = importlib.util.spec_from_file_location("validate_blocker_statuses", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def statuses(state: str = "PRONTO_PARA_CORRIGIR", count: int = 50) -> dict:
    registry_hash = module.canonical_hash(REGISTRY)
    items = []
    for index in range(1, count + 1):
        item = {"blocker_id": f"B{index:02d}", "state": state}
        if state in {"CORRIGIDO_TESTADO", "CORRIGIDO_HOMOLOGADO"}:
            item["code_evidence"] = [f"commit-{index}"]
            item["test_evidence"] = [f"test-{index}"]
        if state == "CORRIGIDO_HOMOLOGADO":
            item["runtime_evidence"] = [f"runtime-{index}"]
            item["homologation_evidence"] = [f"homologation-{index}"]
        items.append(item)
    return {"registry_sha256": registry_hash, "blockers": items}


class BlockerStatusValidatorTests(unittest.TestCase):
    def test_registry_has_exact_50(self):
        meta = module.validate_registry(REGISTRY)
        self.assertEqual(len(meta["ids"]), 50)
        self.assertEqual(meta["ids"][0], "B01")
        self.assertEqual(meta["ids"][-1], "B50")

    def test_complete_nonfinal_is_valid(self):
        report = module.validate_statuses(REGISTRY, statuses())
        self.assertTrue(report["complete"])
        self.assertFalse(report["final_ok"])

    def test_homologated_requires_all_evidence(self):
        data = statuses("CORRIGIDO_HOMOLOGADO")
        data["blockers"][0]["runtime_evidence"] = []
        with self.assertRaises(module.BlockerValidationError):
            module.validate_statuses(REGISTRY, data)

    def test_corrected_tested_requires_code_and_tests(self):
        data = statuses("CORRIGIDO_TESTADO")
        data["blockers"][0]["test_evidence"] = []
        with self.assertRaises(module.BlockerValidationError):
            module.validate_statuses(REGISTRY, data)

    def test_missing_blocker_blocks_final(self):
        with self.assertRaises(module.BlockerValidationError):
            module.validate_statuses(
                REGISTRY,
                statuses("CORRIGIDO_HOMOLOGADO", 49),
                True,
            )

    def test_all_50_homologated_with_evidence_pass_final(self):
        report = module.validate_statuses(
            REGISTRY,
            statuses("CORRIGIDO_HOMOLOGADO"),
            True,
        )
        self.assertTrue(report["final_ok"])
        self.assertEqual(report["homologated"], 50)

    def test_registry_hash_mismatch_rejected(self):
        data = statuses()
        data["registry_sha256"] = "0" * 64
        with self.assertRaises(module.BlockerValidationError):
            module.validate_statuses(REGISTRY, data)

    def test_duplicate_status_rejected(self):
        data = statuses()
        data["blockers"].append(dict(data["blockers"][0]))
        with self.assertRaises(module.BlockerValidationError):
            module.validate_statuses(REGISTRY, data)


if __name__ == "__main__":
    unittest.main()
