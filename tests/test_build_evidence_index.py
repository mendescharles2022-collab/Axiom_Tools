from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_evidence_index as evidence  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class EvidenceIndexTests(unittest.TestCase):
    def test_build_and_verify_valid_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "reports" / "a.json", '{"ok":true}\n')
            write(root / "reports" / "b.txt", "proof\n")
            document = evidence.build_index(root, ["reports/a.json", "reports/b.txt"])
            report = evidence.verify_index(root, document)
            self.assertTrue(report["ok"])
            self.assertEqual(report["file_count"], 2)

    def test_content_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "a.txt"
            write(target, "original\n")
            document = evidence.build_index(root, ["a.txt"])
            write(target, "changed\n")
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.verify_index(root, document)

    def test_index_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.txt", "proof\n")
            document = evidence.build_index(root, ["a.txt"])
            document["files"][0]["length"] += 1
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.verify_index(root, document)

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.build_index(Path(tmp), ["../secret.txt"])

    def test_duplicate_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.txt", "proof\n")
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.build_index(root, ["a.txt", "a.txt"])

    def test_missing_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.build_index(Path(tmp), ["missing.txt"])

    def test_empty_index_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(evidence.EvidenceIndexError):
                evidence.build_index(Path(tmp), [])

    def test_file_order_is_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "b.txt", "b\n")
            write(root / "a.txt", "a\n")
            document = evidence.build_index(root, ["b.txt", "a.txt"])
            self.assertEqual([item["path"] for item in document["files"]], ["a.txt", "b.txt"])


if __name__ == "__main__":
    unittest.main()
