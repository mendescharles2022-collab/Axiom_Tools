from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


class ApplicabilityError(RuntimeError):
    pass


def _money(value: object, *, optional: bool = False) -> Decimal | None:
    if value is None and optional:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ApplicabilityError(f"Valor monetário inválido: {value!r}") from exc
    if not result.is_finite():
        raise ApplicabilityError(f"Valor monetário não finito: {value!r}")
    return result.quantize(Decimal("0.01"))


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def derive(record: dict, policy: dict | None = None) -> dict:
    if not isinstance(record, dict):
        raise ApplicabilityError("Registro mensal deve ser objeto JSON.")
    policy = policy or {}
    tolerance = _money(policy.get("zero_tolerance", "0.02")) or Decimal("0.02")
    client_id = str(record.get("client_id") or "").strip()
    competence = str(record.get("competence") or "").strip()
    if not client_id or not competence:
        raise ApplicabilityError("client_id e competence são obrigatórios.")

    profile = str(record.get("profile") or "").strip().upper()
    mei = bool(record.get("mei", profile == "MEI"))
    dae_expected = bool(record.get("dae_expected", False))
    generic_fgts_expected = bool(record.get("generic_fgts_expected", False))

    fgts_base_available = bool(record.get("fgts_authoritative_base_available", False))
    fgts_amount = _money(record.get("fgts_authoritative_amount"), optional=True)
    federal_available = bool(record.get("federal_authoritative_available", False))
    federal_gross = _money(record.get("federal_gross"), optional=True)
    federal_deductions = _money(record.get("federal_deductions"), optional=True)
    federal_balance = _money(record.get("federal_balance"), optional=True)

    absence_integral = bool(record.get("absence_integral", False))
    monetary_incidence = bool(record.get("monetary_incidence", False))
    absence_reason = str(record.get("absence_reason") or "").strip().upper() or None

    findings: list[dict] = []
    obligations: dict[str, dict] = {}

    # FGTS/GFD: evidência mensal autoritativa tem precedência sobre expectativa genérica.
    if mei and dae_expected:
        obligations["FGTS_DIGITAL"] = {
            "applicable": False,
            "state": "NAO_APLICAVEL",
            "reason": "PERFIL_MEI_RECOLHIMENTO_VIA_DAE",
            "evidence_strength": "PROFILE_SPECIFIC",
        }
    elif fgts_base_available:
        if fgts_amount is None:
            findings.append({"code": "FGTS_AUTHORITATIVE_AMOUNT_MISSING"})
            obligations["FGTS_DIGITAL"] = {"applicable": None, "state": "REVIEW_REQUIRED", "reason": "BASE_SEM_VALOR"}
        elif abs(fgts_amount) <= tolerance:
            obligations["FGTS_DIGITAL"] = {
                "applicable": False,
                "state": "NAO_APLICAVEL",
                "reason": "VALOR_AUTORITATIVO_ZERO",
                "amount": format(fgts_amount, ".2f"),
                "generic_expectation_overridden": generic_fgts_expected,
                "evidence_strength": "AUTHORITATIVE_MONTHLY",
            }
        else:
            obligations["FGTS_DIGITAL"] = {
                "applicable": True,
                "state": "APLICAVEL",
                "reason": "INCIDENCIA_AUTORITATIVA_POSITIVA",
                "amount": format(fgts_amount, ".2f"),
                "evidence_strength": "AUTHORITATIVE_MONTHLY",
            }
    elif absence_integral and not monetary_incidence:
        obligations["FGTS_DIGITAL"] = {
            "applicable": False,
            "state": "NAO_APLICAVEL",
            "reason": "AUSENCIA_INTEGRAL_SEM_INCIDENCIA",
            "absence_reason": absence_reason,
            "evidence_strength": "MONTHLY_OCCURRENCE",
        }
    elif generic_fgts_expected:
        obligations["FGTS_DIGITAL"] = {
            "applicable": True,
            "state": "APLICAVEL_ESPERADO",
            "reason": "EXPECTATIVA_CADASTRAL_SEM_BASE_AUTORITATIVA",
            "evidence_strength": "GENERIC_PROFILE",
        }
    else:
        obligations["FGTS_DIGITAL"] = {
            "applicable": None,
            "state": "REVIEW_REQUIRED",
            "reason": "EVIDENCIA_INSUFICIENTE",
            "evidence_strength": "NONE",
        }
        findings.append({"code": "FGTS_APPLICABILITY_EVIDENCE_INSUFFICIENT"})

    # DAE é obrigação própria; não deve ser substituída por expectativa genérica de GFD.
    if mei:
        obligations["DAE"] = {
            "applicable": dae_expected,
            "state": "APLICAVEL" if dae_expected else "NAO_APLICAVEL",
            "reason": "PERFIL_MEI_DAE" if dae_expected else "MEI_SEM_DAE_NA_COMPETENCIA",
            "evidence_strength": "PROFILE_SPECIFIC",
        }
    else:
        obligations["DAE"] = {
            "applicable": False,
            "state": "NAO_APLICAVEL",
            "reason": "PERFIL_NAO_MEI",
            "evidence_strength": "PROFILE_SPECIFIC",
        }

    # DARF folha: saldo autoritativo líquido já deve refletir deduções/compensações.
    if federal_available:
        if federal_balance is None:
            findings.append({"code": "FEDERAL_AUTHORITATIVE_BALANCE_MISSING"})
            obligations["DARF_FOLHA"] = {"applicable": None, "state": "REVIEW_REQUIRED", "reason": "SALDO_AUTORITATIVO_AUSENTE"}
        else:
            if federal_gross is not None and federal_deductions is not None:
                expected_balance = (federal_gross - federal_deductions).quantize(Decimal("0.01"))
                if abs(expected_balance - federal_balance) > tolerance:
                    findings.append({
                        "code": "FEDERAL_NET_BALANCE_INCONSISTENT",
                        "gross": format(federal_gross, ".2f"),
                        "deductions": format(federal_deductions, ".2f"),
                        "declared_balance": format(federal_balance, ".2f"),
                        "expected_balance": format(expected_balance, ".2f"),
                    })
            if abs(federal_balance) <= tolerance:
                obligations["DARF_FOLHA"] = {
                    "applicable": False,
                    "state": "NAO_APLICAVEL",
                    "reason": "SALDO_AUTORITATIVO_ZERO",
                    "balance": format(federal_balance, ".2f"),
                    "evidence_strength": "AUTHORITATIVE_MONTHLY",
                }
            else:
                obligations["DARF_FOLHA"] = {
                    "applicable": True,
                    "state": "APLICAVEL",
                    "reason": "SALDO_AUTORITATIVO_POSITIVO",
                    "balance": format(federal_balance, ".2f"),
                    "evidence_strength": "AUTHORITATIVE_MONTHLY",
                }
    elif absence_integral and not monetary_incidence:
        obligations["DARF_FOLHA"] = {
            "applicable": False,
            "state": "NAO_APLICAVEL",
            "reason": "AUSENCIA_INTEGRAL_SEM_BASE_FOLHA",
            "absence_reason": absence_reason,
            "evidence_strength": "MONTHLY_OCCURRENCE",
        }
    else:
        obligations["DARF_FOLHA"] = {
            "applicable": None,
            "state": "REVIEW_REQUIRED",
            "reason": "EVIDENCIA_INSUFICIENTE",
            "evidence_strength": "NONE",
        }
        findings.append({"code": "FEDERAL_APPLICABILITY_EVIDENCE_INSUFFICIENT"})

    report = {
        "version": 1,
        "audit": "B19_B20_B21_B22_MONTHLY_APPLICABILITY",
        "all_ok": not findings,
        "client_id": client_id,
        "competence": competence,
        "obligations": obligations,
        "findings": findings,
    }
    report["report_sha256"] = _canonical_hash(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Deriva aplicabilidade mensal por evidência, sem gravar no runtime.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.input.read_text(encoding="utf-8"))
        policy = json.loads(args.policy.read_text(encoding="utf-8")) if args.policy else {}
        report = derive(record, policy)
    except (OSError, json.JSONDecodeError, ApplicabilityError) as exc:
        print(f"APPLICABILITY_ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
