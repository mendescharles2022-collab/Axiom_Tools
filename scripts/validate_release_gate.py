from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import generate_build_provenance as provenance
import validate_blocker_statuses as blocker_validator
import validate_regression_results as regression_validator
import verify_build_provenance as build_verify

REQUIRED_EVIDENCE_GATES = (
    "CI_TOOLING",
    "RUNTIME_BASELINE",
    "DATABASE_INTEGRITY",
    "DATABASE_FOREIGN_KEYS",
    "DATABASE_INVARIANTS",
    "BENCHMARK_RUNTIME",
    "SECURITY_RUNTIME",
    "REPORT_A4",
    "WINDOWS_INSTALLATION",
    "ROLLBACK_WINDOWS",
)
EVIDENCE_STATUSES = {"PASS", "FAIL", "NOT_RUN", "BLOCKED"}


class ReleaseGateError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseGateError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseGateError(f"JSON deve ser objeto: {path}")
    return value


def validate_evidence_manifest(document: dict) -> dict:
    if document.get("version") != 1 or document.get("audit") != "V8":
        raise ReleaseGateError("Manifesto de evidências deve ser version=1 audit=V8.")

    raw = document.get("gates")
    if not isinstance(raw, list):
        raise ReleaseGateError("Manifesto de evidências deve conter lista gates.")

    by_id: dict[str, dict] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise ReleaseGateError("Entrada de evidência inválida.")
        gate_id = str(item.get("gate_id", "")).strip().upper()
        if gate_id in by_id:
            raise ReleaseGateError(f"Gate duplicado: {gate_id}")
        if gate_id not in REQUIRED_EVIDENCE_GATES:
            raise ReleaseGateError(f"Gate desconhecido: {gate_id}")

        status = str(item.get("status", "")).strip().upper()
        if status not in EVIDENCE_STATUSES:
            raise ReleaseGateError(f"Status inválido em {gate_id}: {status}")

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not all(
            isinstance(value, str) and value.strip() for value in evidence
        ):
            raise ReleaseGateError(f"Evidence inválida em {gate_id}.")
        if status == "PASS" and not evidence:
            raise ReleaseGateError(f"PASS sem evidência em {gate_id}.")

        by_id[gate_id] = {
            "status": status,
            "evidence": [value.strip() for value in evidence],
            "notes": str(item.get("notes", "")),
        }

    missing = [gate_id for gate_id in REQUIRED_EVIDENCE_GATES if gate_id not in by_id]
    pass_count = sum(1 for item in by_id.values() if item["status"] == "PASS")
    final_ok = not missing and pass_count == len(REQUIRED_EVIDENCE_GATES)

    return {
        "required": len(REQUIRED_EVIDENCE_GATES),
        "submitted": len(by_id),
        "missing": missing,
        "pass_count": pass_count,
        "final_ok": final_ok,
        "gates": by_id,
    }


def _release_identity(identity_path: Path) -> tuple[bool, dict | None, str | None]:
    try:
        identity = provenance.load_release_identity(identity_path)
    except provenance.ProvenanceError as exc:
        return False, None, str(exc)
    return True, identity, None


def evaluate_release_gate(
    *,
    blocker_registry_path: Path,
    blocker_status_path: Path,
    regression_registry_path: Path,
    regression_results_path: Path,
    release_identity_path: Path,
    evidence_manifest_path: Path,
    payload_root: Path | None = None,
    repo_root: Path | None = None,
    final_mode: bool = False,
) -> dict:
    errors: list[str] = []

    try:
        blocker_report = blocker_validator.validate_statuses(
            blocker_validator.load_json(blocker_registry_path),
            blocker_validator.load_json(blocker_status_path),
            final_mode=False,
        )
    except blocker_validator.BlockerValidationError as exc:
        raise ReleaseGateError(f"Blockers inválidos: {exc}") from exc

    try:
        regression_report = regression_validator.validate_results(
            regression_validator.load_json(regression_registry_path),
            regression_validator.load_json(regression_results_path),
            final_mode=False,
        )
    except regression_validator.RegressionValidationError as exc:
        raise ReleaseGateError(f"Regressão inválida: {exc}") from exc

    evidence_report = validate_evidence_manifest(load_json(evidence_manifest_path))
    release_ready, identity, release_error = _release_identity(release_identity_path)

    build_ok = False
    build_manifest: dict | None = None
    build_error: str | None = None
    if payload_root is not None and repo_root is not None:
        try:
            build_manifest = build_verify.verify_build(
                payload_root=payload_root,
                repo_root=repo_root,
            )
            build_ok = True
        except build_verify.VerificationError as exc:
            build_error = str(exc)
    elif final_mode:
        build_error = "payload_root e repo_root são obrigatórios no gate final."

    if not blocker_report["final_ok"]:
        errors.append(
            f"bloqueadores homologados={blocker_report['homologated']}/50"
        )
    if not regression_report["final_ok"]:
        errors.append(
            f"regressão PASS={regression_report['status_counts'].get('PASS', 0)}/28"
        )
    if not release_ready:
        errors.append("release não está READY")
    if not evidence_report["final_ok"]:
        errors.append(
            f"evidências PASS={evidence_report['pass_count']}/{evidence_report['required']}"
        )
    if not build_ok:
        errors.append("build não verificado")

    final_ok = not errors
    report = {
        "audit": "V8",
        "blockers": blocker_report,
        "regression": regression_report,
        "release_ready": release_ready,
        "release_identity": identity,
        "release_error": release_error,
        "evidence": evidence_report,
        "build_ok": build_ok,
        "build_error": build_error,
        "build": build_manifest,
        "errors": errors,
        "final_ok": final_ok,
    }

    if final_mode and not final_ok:
        raise ReleaseGateError(
            "Gate final V8 bloqueado: " + "; ".join(errors)
        )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida o gate único de homologação/liberação da V8."
    )
    parser.add_argument("--blocker-registry", required=True, type=Path)
    parser.add_argument("--blocker-status", required=True, type=Path)
    parser.add_argument("--regression-registry", required=True, type=Path)
    parser.add_argument("--regression-results", required=True, type=Path)
    parser.add_argument("--release-identity", required=True, type=Path)
    parser.add_argument("--evidence-manifest", required=True, type=Path)
    parser.add_argument("--payload-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--final", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path("V8_RELEASE_GATE.json")
    )
    args = parser.parse_args()

    try:
        report = evaluate_release_gate(
            blocker_registry_path=args.blocker_registry,
            blocker_status_path=args.blocker_status,
            regression_registry_path=args.regression_registry,
            regression_results_path=args.regression_results,
            release_identity_path=args.release_identity,
            evidence_manifest_path=args.evidence_manifest,
            payload_root=args.payload_root,
            repo_root=args.repo_root,
            final_mode=args.final,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except ReleaseGateError as exc:
        print(f"V8_RELEASE_GATE_ERRO: {exc}", file=sys.stderr)
        return 2

    print("V8_RELEASE_GATE_OK")
    print(f"Final OK: {report['final_ok']}")
    if report["errors"]:
        print("Pendências: " + "; ".join(report["errors"]))
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
