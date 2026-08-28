from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, filename: str):
    script = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load("create_rollback_bundle_identity", "create_rollback_bundle.py")
verify = load("verify_rollback_bundle_identity", "verify_rollback_bundle.py")


def prepare(base: Path) -> tuple[Path, Path, Path]:
    root = base / "root"
    out = base / "bundle"
    database = base / "db.sqlite3"
    (root / "app").mkdir(parents=True)
    (root / "app" / "main.py").write_text("VALUE = 1\n", encoding="utf-8")
    con = sqlite3.connect(database)
    con.execute("CREATE TABLE t(id INTEGER PRIMARY KEY)")
    con.execute("INSERT INTO t VALUES(1)")
    con.commit()
    con.close()
    return root, out, database


def plan() -> dict:
    return {"version": 1, "files": [{"path": "app/main.py", "role": "code"}]}


def create_transition_bundle(base: Path) -> Path:
    root, out, database = prepare(base)
    builder.create_bundle(
        source_root=root,
        db_path=database,
        plan=plan(),
        output_dir=out,
        app_version="V7",
        schema_version="7",
        commit_sha="oldabc123",
        target_identity={
            "app_version": "V8",
            "schema_version": "8",
            "commit_sha": "newdef456",
        },
    )
    return out


class RollbackIdentityV8Tests(unittest.TestCase):
    def test_bundle_records_previous_and_target_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = create_transition_bundle(Path(tmp))
            report = verify.verify_bundle(out)
            self.assertEqual(report["previous_identity"]["app_version"], "V7")
            self.assertEqual(report["previous_identity"]["schema_version"], "7")
            self.assertEqual(report["target_identity"]["app_version"], "V8")
            self.assertEqual(report["target_identity"]["schema_version"], "8")

    def test_target_identity_requires_exact_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, out, database = prepare(Path(tmp))
            with self.assertRaises(builder.RollbackError):
                builder.create_bundle(
                    source_root=root,
                    db_path=database,
                    plan=plan(),
                    output_dir=out,
                    app_version="V7",
                    schema_version="7",
                    commit_sha="oldabc123",
                    target_identity={"app_version": "V8"},
                )

    def test_previous_identity_cannot_diverge_from_canonical_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = create_transition_bundle(Path(tmp))
            manifest_path = out / builder.MANIFEST_NAME
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            data["previous_identity"]["schema_version"] = "999"
            payload = dict(data)
            payload.pop("manifest_sha256", None)
            encoded = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            import hashlib
            data["manifest_sha256"] = hashlib.sha256(encoded).hexdigest().upper()
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(verify.VerificationError):
                verify.verify_bundle(out)

    def test_target_identity_tamper_is_detected_by_manifest_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = create_transition_bundle(Path(tmp))
            manifest_path = out / builder.MANIFEST_NAME
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            data["target_identity"]["commit_sha"] = "tampered"
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(verify.VerificationError):
                verify.verify_bundle(out)


if __name__ == "__main__":
    unittest.main()
