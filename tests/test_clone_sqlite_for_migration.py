from __future__ import annotations

import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import clone_sqlite_for_migration as module  # noqa: E402


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_valid_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA user_version=7")
    connection.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
    connection.execute(
        "CREATE TABLE child("
        "id INTEGER PRIMARY KEY, "
        "parent_id INTEGER REFERENCES parent(id))"
    )
    connection.execute("INSERT INTO parent VALUES(1)")
    connection.execute("INSERT INTO child VALUES(1,1)")
    connection.commit()
    connection.close()


class CloneSqliteForMigrationTests(unittest.TestCase):
    def test_clone_is_equivalent_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.sqlite3"
            destination = base / "destination.sqlite3"
            create_valid_db(source)
            before = file_hash(source)

            report = module.clone_database(source, destination)

            self.assertTrue(destination.exists())
            self.assertEqual(before, file_hash(source))
            self.assertTrue(report["migration_ready_copy"])
            self.assertTrue(report["checks"]["schema_equal"])
            connection = sqlite3.connect(destination)
            try:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM child").fetchone()[0],
                    1,
                )
            finally:
                connection.close()

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.sqlite3"
            destination = base / "destination.sqlite3"
            create_valid_db(source)
            destination.write_text("keep", encoding="utf-8")

            with self.assertRaises(module.CloneError):
                module.clone_database(source, destination)

            self.assertEqual(destination.read_text(encoding="utf-8"), "keep")

    def test_structural_divergence_blocks_copy_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.sqlite3"
            destination = base / "destination.sqlite3"
            connection = sqlite3.connect(source)
            connection.execute("PRAGMA foreign_keys=OFF")
            connection.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE child("
                "id INTEGER, parent_id INTEGER REFERENCES parent(id))"
            )
            connection.execute("INSERT INTO child VALUES(1,999)")
            connection.commit()
            connection.close()

            with self.assertRaises(module.CloneError):
                module.clone_database(source, destination)

            self.assertFalse(destination.exists())
            self.assertFalse(
                destination.with_name(destination.name + ".partial").exists()
            )

    def test_diagnostic_mode_preserves_same_fk_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.sqlite3"
            destination = base / "destination.sqlite3"
            connection = sqlite3.connect(source)
            connection.execute("PRAGMA foreign_keys=OFF")
            connection.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE child("
                "id INTEGER, parent_id INTEGER REFERENCES parent(id))"
            )
            connection.execute("INSERT INTO child VALUES(1,999)")
            connection.commit()
            connection.close()

            report = module.clone_database(
                source, destination, require_structural_ok=False
            )

            self.assertTrue(destination.exists())
            self.assertFalse(report["migration_ready_copy"])

    def test_invalid_source_leaves_no_partial_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "invalid.sqlite3"
            destination = base / "destination.sqlite3"
            source.write_text("not sqlite", encoding="utf-8")

            with self.assertRaises(Exception):
                module.clone_database(source, destination)

            self.assertFalse(destination.exists())
            self.assertFalse(
                destination.with_name(destination.name + ".partial").exists()
            )

    def test_skip_counts_still_clones(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "source.sqlite3"
            destination = base / "destination.sqlite3"
            create_valid_db(source)

            report = module.clone_database(
                source, destination, include_row_counts=False
            )

            self.assertTrue(report["checks"]["schema_equal"])
            self.assertIsNone(report["checks"]["row_counts_equal"])


if __name__ == "__main__":
    unittest.main()
