from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "build_security_homologation_preflight.py"
spec = importlib.util.spec_from_file_location("build_security_homologation_preflight", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def policy(*, required=None, csrf=False, path="/admin/x", extra_rules=None) -> dict:
    rules = [
        {
            "id": "admin-x",
            "path": path,
            "methods": ["POST"],
            "required_decorators": required or ["login_required", "admin_required"],
            "allow_csrf_exempt": csrf,
        }
    ]
    rules.extend(extra_rules or [])
    return {
        "version": 1,
        "auth_decorators": ["login_required", "admin_required"],
        "csrf_exempt_decorators": ["csrf.exempt"],
        "rules": rules,
    }


class SecurityHomologationPreflightTests(unittest.TestCase):
    def test_classified_mutating_route_with_required_decorators_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\n@admin_required\ndef x(): pass\n",
            )
            report = module.build_preflight(root, policy())
            self.assertTrue(report["static_ok"])
            self.assertFalse(report["runtime_homologated"])
            self.assertEqual(report["summary"]["approved_mutating_routes"], 1)

    def test_unclassified_mutating_route_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/other')\n@login_required\ndef other(): pass\n",
            )
            report = module.build_preflight(root, policy())
            self.assertFalse(report["static_ok"])
            codes = str(report["findings"])
            self.assertIn("UNCLASSIFIED_MUTATING_ROUTE", codes)
            self.assertIn("POLICY_RULE_WITHOUT_ROUTE", codes)

    def test_missing_business_authorization_decorator_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\ndef x(): pass\n",
            )
            report = module.build_preflight(root, policy())
            self.assertFalse(report["static_ok"])
            self.assertIn(
                "MISSING_REQUIRED_DECORATOR:admin_required",
                report["route_results"][0]["violations"],
            )

    def test_missing_auth_marker_blocks_even_when_rule_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "routes.py", "@bp.post('/admin/x')\ndef x(): pass\n")
            report = module.build_preflight(
                root,
                policy(required=["custom_business_gate"]),
            )
            self.assertFalse(report["static_ok"])
            self.assertIn("MISSING_AUTH_MARKER", report["route_results"][0]["violations"])

    def test_csrf_exempt_is_blocked_unless_rule_explicitly_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\n@admin_required\n@csrf.exempt\ndef x(): pass\n",
            )
            report = module.build_preflight(root, policy(csrf=False))
            self.assertFalse(report["static_ok"])
            self.assertIn("CSRF_EXEMPT_NOT_ALLOWED", report["route_results"][0]["violations"])

    def test_explicit_csrf_exception_can_pass_static_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\n@admin_required\n@csrf.exempt\ndef x(): pass\n",
            )
            report = module.build_preflight(root, policy(csrf=True))
            self.assertTrue(report["static_ok"])
            self.assertFalse(report["runtime_homologated"])

    def test_unused_policy_rule_blocks_stale_security_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\n@admin_required\ndef x(): pass\n",
            )
            extra = {
                "id": "removed-route",
                "path": "/removed",
                "methods": ["DELETE"],
                "required_decorators": ["admin_required"],
                "allow_csrf_exempt": False,
            }
            report = module.build_preflight(root, policy(extra_rules=[extra]))
            self.assertFalse(report["static_ok"])
            self.assertEqual(report["summary"]["unused_rules"], 1)

    def test_duplicate_rule_for_same_route_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "routes.py",
                "@bp.post('/admin/x')\n@login_required\n@admin_required\ndef x(): pass\n",
            )
            duplicate = {
                "id": "duplicate",
                "path": "/admin/x",
                "methods": ["POST"],
                "required_decorators": ["login_required"],
                "allow_csrf_exempt": False,
            }
            with self.assertRaises(module.SecurityPreflightError):
                module.build_preflight(root, policy(extra_rules=[duplicate]))


if __name__ == "__main__":
    unittest.main()
