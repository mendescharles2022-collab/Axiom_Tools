from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_runtime_reconciliation_handoff as builder  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "consume_runtime_reconciliation_plan_test",
    SCRIPTS / "consume_runtime_reconciliation_handoff.py",
)
consumer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = consumer
SPEC.loader.exec_module(consumer)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture(base: Path, repo_text: str) -> tuple[Path, Path, Path]:
    runtime = base / "runtime"
    repo = base / "repo"
    output = base / "handoff-output"
    invariants = base / "invariants.json"
    write(runtime / "src/pkg/a.py", "x = 1\n")
    write(repo / "src/pkg/a.py", repo_text)
    database = runtime / "operational.sqlite3"
    database.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database)
    try:
        conn.execute("CREATE TABLE smoke (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
        conn.execute("INSERT INTO smoke(status) VALUES ('OK')")
        conn.commit()
    finally:
        conn.close()
    invariants.write_text(
        json.dumps({
            "version": 1,
            "invariants": [{
                "id": "smoke",
                "description": "smoke",
                "severity": "error",
                "sql": "SELECT id FROM smoke WHERE status <> 'OK'",
                "max_rows": 10,
            }],
        }),
        encoding="utf-8",
    )
    built = builder.build_handoff(runtime, database, output, label="plan-v8")
    return output / built["handoff_dir"], repo, invariants


class ConsumeRuntimeReconciliationPlanTests(unittest.TestCase):
    def test_consumer_writes_plan_and_binds_hash_to_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants = fixture(base, "x = 2\n")
            output = base / "consumed"
            result = consumer.consume_handoff(
                handoff,
                repo,
                output,
                invariants_path=invariants,
            )
            plan_path = output / "RECONCILIATION_PLAN.json"
            self.assertTrue(plan_path.is_file())
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(result["reconciliation_plan_sha256"], plan["plan_sha256"])
            self.assertEqual(result["reconciliation_review_required"], plan["summary"]["review_required"])
            self.assertFalse(result["automatic_reconciliation_write"])
            self.assertFalse(plan["automatic_write_allowed"])
            self.assertGreater(plan["summary"]["review_required"], 0)
            self.assertFalse(plan["v8_homologated"])

    def test_changed_runtime_file_is_review_merge_not_auto_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants = fixture(base, "x = 2\n")
            output = base / "consumed"
            consumer.consume_handoff(handoff, repo, output, invariants_path=invariants)
            plan = json.loads((output / "RECONCILIATION_PLAN.json").read_text(encoding="utf-8"))
            entry = next(
                item for item in plan["entries"]
                if item["relative_path"] == "pkg/a.py" and item["status"] == "CHANGED"
            )
            self.assertEqual(entry["proposed_action"], "REVIEW_MERGE")
            self.assertTrue(entry["review_required"])
            self.assertFalse(entry["automatic_write"])


if __name__ == "__main__":
    unittest.main()
