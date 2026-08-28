from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_blocker_statuses as blockers  # noqa: E402
import validate_regression_results as regression  # noqa: E402
import validate_release_gate as gate  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def all_pass_evidence() -> dict:
    return {
        "version": 1,
        "audit": "V8",
        "gates": [
            {"gate_id": gate_id, "status": "PASS", "evidence": [f"evidence:{gate_id}"]}
            for gate_id in gate.REQUIRED_EVIDENCE_GATES
        ],
    }


def final_blocker_status(registry: dict) -> dict:
    return {
        "version": 1,
        "audit": "V8",
        "registry_sha256": blockers.canonical_hash(registry),
        "blockers": [
            {
                "blocker_id": item["blocker_id"],
                "state": "CORRIGIDO_HOMOLOGADO",
                "code_evidence": [f"code:{item['blocker_id']}"],
                "test_evidence": [f"test:{item['blocker_id']}"],
                "runtime_evidence": [f"runtime:{item['blocker_id']}"],
                "homologation_evidence": [f"homologation:{item['blocker_id']}"],
            }
            for item in registry["blockers"]
        ],
    }


def final_regression_results(registry: dict) -> dict:
    return {
        "registry_sha256": regression.canonical_hash(registry),
        "results": [
            {"case_id": item["case_id"], "status": "PASS", "evidence": [f"case:{item['case_id']}"]}
            for item in registry["required_cases"]
        ],
    }


def ready_identity(path: Path) -> None:
    path.write_text(
        """
[release]
product = "Axiom Tools"
state = "READY"
release_version = "V5.6.14V8"
schema_version = "8"
python_target = "3.12"
platform_target = "windows-x64"

[policy]
require_clean_git = true
require_schema_version = true
require_release_version = true
""".strip() + "\n",
        encoding="utf-8",
    )


class ReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocker_registry = blockers.load_json(ROOT / "config" / "blocker_registry_v8.json")
        cls.regression_registry = regression.load_json(ROOT / "config" / "regression_cases_v8_202608.json")

    def test_evidence_manifest_all_pass(self):
        report = gate.validate_evidence_manifest(all_pass_evidence())
        self.assertTrue(report["final_ok"])
        self.assertEqual(report["pass_count"], len(gate.REQUIRED_EVIDENCE_GATES))

    def test_pass_without_evidence_is_rejected(self):
        document = all_pass_evidence()
        document["gates"][0]["evidence"] = []
        with self.assertRaises(gate.ReleaseGateError):
            gate.validate_evidence_manifest(document)

    def test_missing_evidence_gate_blocks_final(self):
        document = all_pass_evidence()
        document["gates"].pop()
        report = gate.validate_evidence_manifest(document)
        self.assertFalse(report["final_ok"])
        self.assertEqual(len(report["missing"]), 1)

    def test_unknown_evidence_gate_is_rejected(self):
        document = all_pass_evidence()
        document["gates"][0]["gate_id"] = "UNKNOWN"
        with self.assertRaises(gate.ReleaseGateError):
            gate.validate_evidence_manifest(document)

    def test_current_repository_state_preflight_is_not_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            regression_results = base / "regression.json"
            evidence = base / "evidence.json"
            write_json(
                regression_results,
                {
                    "registry_sha256": regression.canonical_hash(self.regression_registry),
                    "results": [
                        {"case_id": item["case_id"], "status": "NOT_RUN", "evidence": []}
                        for item in self.regression_registry["required_cases"]
                    ],
                },
            )
            write_json(evidence, {
                "version": 1,
                "audit": "V8",
                "gates": [
                    {"gate_id": gate_id, "status": "NOT_RUN", "evidence": []}
                    for gate_id in gate.REQUIRED_EVIDENCE_GATES
                ],
            })

            report = gate.evaluate_release_gate(
                blocker_registry_path=ROOT / "config" / "blocker_registry_v8.json",
                blocker_status_path=ROOT / "config" / "blocker_status_v8_current.json",
                regression_registry_path=ROOT / "config" / "regression_cases_v8_202608.json",
                regression_results_path=regression_results,
                release_identity_path=ROOT / "config" / "release_identity.toml",
                evidence_manifest_path=evidence,
                final_mode=False,
            )
            self.assertFalse(report["final_ok"])
            self.assertFalse(report["release_ready"])
            self.assertEqual(report["blockers"]["homologated"], 0)

    def test_final_mode_requires_build_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            blocker_status = base / "blockers.json"
            regression_results = base / "regression.json"
            identity = base / "release.toml"
            evidence = base / "evidence.json"
            write_json(blocker_status, final_blocker_status(self.blocker_registry))
            write_json(regression_results, final_regression_results(self.regression_registry))
            ready_identity(identity)
            write_json(evidence, all_pass_evidence())

            with self.assertRaises(gate.ReleaseGateError):
                gate.evaluate_release_gate(
                    blocker_registry_path=ROOT / "config" / "blocker_registry_v8.json",
                    blocker_status_path=blocker_status,
                    regression_registry_path=ROOT / "config" / "regression_cases_v8_202608.json",
                    regression_results_path=regression_results,
                    release_identity_path=identity,
                    evidence_manifest_path=evidence,
                    final_mode=True,
                )

    def test_final_mode_passes_only_when_every_layer_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            blocker_status = base / "blockers.json"
            regression_results = base / "regression.json"
            identity = base / "release.toml"
            evidence = base / "evidence.json"
            payload = base / "payload"
            repo = base / "repo"
            payload.mkdir()
            repo.mkdir()
            write_json(blocker_status, final_blocker_status(self.blocker_registry))
            write_json(regression_results, final_regression_results(self.regression_registry))
            ready_identity(identity)
            write_json(evidence, all_pass_evidence())

            with mock.patch.object(
                gate.build_verify,
                "verify_build",
                return_value={"produto": "Axiom Tools", "versao_release": "V5.6.14V8"},
            ):
                report = gate.evaluate_release_gate(
                    blocker_registry_path=ROOT / "config" / "blocker_registry_v8.json",
                    blocker_status_path=blocker_status,
                    regression_registry_path=ROOT / "config" / "regression_cases_v8_202608.json",
                    regression_results_path=regression_results,
                    release_identity_path=identity,
                    evidence_manifest_path=evidence,
                    payload_root=payload,
                    repo_root=repo,
                    final_mode=True,
                )
            self.assertTrue(report["final_ok"])
            self.assertTrue(report["build_ok"])
            self.assertEqual(report["blockers"]["homologated"], 50)
            self.assertEqual(report["regression"]["status_counts"]["PASS"], 28)

    def test_build_verification_failure_blocks_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            blocker_status = base / "blockers.json"
            regression_results = base / "regression.json"
            identity = base / "release.toml"
            evidence = base / "evidence.json"
            payload = base / "payload"
            repo = base / "repo"
            payload.mkdir()
            repo.mkdir()
            write_json(blocker_status, final_blocker_status(self.blocker_registry))
            write_json(regression_results, final_regression_results(self.regression_registry))
            ready_identity(identity)
            write_json(evidence, all_pass_evidence())

            with mock.patch.object(
                gate.build_verify,
                "verify_build",
                side_effect=gate.build_verify.VerificationError("tampered"),
            ):
                with self.assertRaises(gate.ReleaseGateError):
                    gate.evaluate_release_gate(
                        blocker_registry_path=ROOT / "config" / "blocker_registry_v8.json",
                        blocker_status_path=blocker_status,
                        regression_registry_path=ROOT / "config" / "regression_cases_v8_202608.json",
                        regression_results_path=regression_results,
                        release_identity_path=identity,
                        evidence_manifest_path=evidence,
                        payload_root=payload,
                        repo_root=repo,
                        final_mode=True,
                    )

    def test_unreleased_identity_blocks_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            blocker_status = base / "blockers.json"
            regression_results = base / "regression.json"
            evidence = base / "evidence.json"
            payload = base / "payload"
            repo = base / "repo"
            payload.mkdir()
            repo.mkdir()
            write_json(blocker_status, final_blocker_status(self.blocker_registry))
            write_json(regression_results, final_regression_results(self.regression_registry))
            write_json(evidence, all_pass_evidence())

            with mock.patch.object(gate.build_verify, "verify_build", return_value={"produto": "Axiom Tools"}):
                with self.assertRaises(gate.ReleaseGateError):
                    gate.evaluate_release_gate(
                        blocker_registry_path=ROOT / "config" / "blocker_registry_v8.json",
                        blocker_status_path=blocker_status,
                        regression_registry_path=ROOT / "config" / "regression_cases_v8_202608.json",
                        regression_results_path=regression_results,
                        release_identity_path=ROOT / "config" / "release_identity.toml",
                        evidence_manifest_path=evidence,
                        payload_root=payload,
                        repo_root=repo,
                        final_mode=True,
                    )

    def test_duplicate_evidence_gate_is_rejected(self):
        document = all_pass_evidence()
        document["gates"].append(dict(document["gates"][0]))
        with self.assertRaises(gate.ReleaseGateError):
            gate.validate_evidence_manifest(document)


if __name__ == "__main__":
    unittest.main()
