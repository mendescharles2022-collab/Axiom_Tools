from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "audit_classificacao_inativacao_contract.py"
spec = importlib.util.spec_from_file_location("audit_classificacao_inativacao_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def enum_policy(**overrides) -> dict:
    data = {
        "version": 1,
        "field_name": "classificacao_inativacao",
        "canonical_representation": "ENUM_MEMBER",
        "enum_types": ["ClassificacaoInativacao"],
        "allow_raw_string_literals": False,
        "allow_none": True,
        "allow_dynamic": False,
    }
    data.update(overrides)
    return data


def string_policy(**overrides) -> dict:
    data = enum_policy(
        canonical_representation="STRING_VALUE",
        allow_raw_string_literals=False,
    )
    data.update(overrides)
    return data


class ClassificationInactivationContractTests(unittest.TestCase):
    def test_enum_member_comparison_passes_enum_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "if cliente.classificacao_inativacao == ClassificacaoInativacao.INATIVA:\n    pass\n",
            )
            report = module.audit_tree(root, enum_policy())
            self.assertTrue(report["static_ok"])
            self.assertEqual(report["summary"]["kinds"], ["ENUM_MEMBER"])

    def test_raw_string_blocks_enum_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "if cliente.classificacao_inativacao == 'INATIVA':\n    pass\n",
            )
            report = module.audit_tree(root, enum_policy())
            self.assertFalse(report["static_ok"])
            self.assertEqual(report["usages"][0]["value_kind"], "RAW_STRING")

    def test_enum_value_passes_string_value_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "cliente.classificacao_inativacao = ClassificacaoInativacao.INATIVA.value\n",
            )
            report = module.audit_tree(root, string_policy())
            self.assertTrue(report["static_ok"])
            self.assertEqual(report["usages"][0]["value_kind"], "ENUM_VALUE")

    def test_enum_member_blocks_string_value_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "cliente.classificacao_inativacao = ClassificacaoInativacao.INATIVA\n",
            )
            report = module.audit_tree(root, string_policy())
            self.assertFalse(report["static_ok"])

    def test_raw_string_can_be_explicitly_allowed_for_storage_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "row['classificacao_inativacao'] = 'INATIVA'\n")
            report = module.audit_tree(
                root,
                string_policy(allow_raw_string_literals=True),
            )
            self.assertTrue(report["static_ok"])

    def test_mixed_enum_member_and_string_representation_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "if a.classificacao_inativacao == ClassificacaoInativacao.INATIVA:\n    pass\n"
                "if b.classificacao_inativacao == 'ATIVA':\n    pass\n",
            )
            report = module.audit_tree(
                root,
                enum_policy(allow_raw_string_literals=True),
            )
            self.assertFalse(report["static_ok"])
            self.assertIn("MIXED_ENUM_AND_STRING_REPRESENTATION", str(report["findings"]))

    def test_dynamic_assignment_requires_explicit_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "cliente.classificacao_inativacao = valor\n")
            blocked = module.audit_tree(root, enum_policy())
            allowed = module.audit_tree(root, enum_policy(allow_dynamic=True))
            self.assertFalse(blocked["static_ok"])
            self.assertTrue(allowed["static_ok"])

    def test_syntax_error_blocks_contract_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "bad.py", "def x(:\n")
            report = module.audit_tree(root, enum_policy())
            self.assertFalse(report["static_ok"])
            self.assertEqual(report["summary"]["parse_errors"], 1)


if __name__ == "__main__":
    unittest.main()
