from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_route_security.py"
spec = importlib.util.spec_from_file_location("audit_route_security", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class RouteAuditTests(unittest.TestCase):
    def test_get_route_is_not_mutating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "@bp.get('/x')\ndef x(): pass\n")
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(report["summary"]["routes"], 1)
            self.assertEqual(report["summary"]["mutating_routes"], 0)

    def test_post_without_auth_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "@bp.post('/x')\ndef x(): pass\n")
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(
                report["summary"]["mutating_without_auth_marker"], 1
            )

    def test_post_with_login_required_is_not_auth_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "@bp.post('/x')\n@login_required\ndef x(): pass\n",
            )
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(
                report["summary"]["mutating_without_auth_marker"], 0
            )

    def test_route_methods_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "@bp.route('/x', methods=['GET','POST'])\n@login_required\ndef x(): pass\n",
            )
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(report["routes"][0]["methods"], ["GET", "POST"])
            self.assertTrue(report["routes"][0]["mutating"])

    def test_csrf_exempt_is_reported_even_with_auth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "@bp.post('/x')\n@login_required\n@csrf.exempt\ndef x(): pass\n",
            )
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(report["summary"]["csrf_exempt_routes"], 1)

    def test_custom_auth_marker_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "@bp.delete('/x')\n@require_admin\ndef x(): pass\n",
            )
            policy = {
                "auth_decorators": ["require_admin"],
                "csrf_exempt_decorators": ["csrf.exempt"],
            }
            report = module.audit_tree(root, policy)
            self.assertEqual(
                report["summary"]["mutating_without_auth_marker"], 0
            )

    def test_multiple_route_decorators_are_inventoried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "@bp.get('/a')\n@bp.post('/b')\n@login_required\ndef x(): pass\n",
            )
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(report["summary"]["routes"], 2)

    def test_syntax_error_is_reported_not_silenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "bad.py", "def x(:\n")
            report = module.audit_tree(root, module.load_policy(None))
            self.assertEqual(report["summary"]["parse_errors"], 1)
            self.assertEqual(report["status"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
