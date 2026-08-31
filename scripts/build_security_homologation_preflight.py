from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import audit_route_security as route_audit

SPEC_VERSION = 1
RULE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class SecurityPreflightError(RuntimeError):
    pass


def _list_of_strings(value: object, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise SecurityPreflightError(f"{field} deve ser lista de strings não vazias.")
    result = [item.strip() for item in value]
    if not allow_empty and not result:
        raise SecurityPreflightError(f"{field} não pode ser vazio.")
    return result


def _required_text(value: object, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SecurityPreflightError(f"{field} é obrigatório.")
    return text


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise SecurityPreflightError(f"Spec deve ser objeto version={SPEC_VERSION}.")

    auth = _list_of_strings(
        spec.get("auth_decorators", ["login_required"]),
        "auth_decorators",
        allow_empty=False,
    )
    csrf = _list_of_strings(
        spec.get("csrf_exempt_decorators", ["csrf.exempt"]),
        "csrf_exempt_decorators",
        allow_empty=False,
    )
    rules_raw = spec.get("rules")
    if not isinstance(rules_raw, list) or not rules_raw:
        raise SecurityPreflightError("Spec deve conter lista não vazia 'rules'.")

    rules = []
    seen: set[str] = set()
    for index, raw in enumerate(rules_raw, start=1):
        if not isinstance(raw, dict):
            raise SecurityPreflightError(f"Regra #{index} deve ser objeto.")
        ident = str(raw.get("id", "")).strip()
        if not ident or not RULE_ID_RE.fullmatch(ident) or ident in seen:
            raise SecurityPreflightError(f"ID inválido/duplicado na regra #{index}: {ident!r}")
        seen.add(ident)
        path = str(raw.get("path", "")).strip()
        if not path.startswith("/"):
            raise SecurityPreflightError(f"{ident}: path deve iniciar por '/'.")
        methods = sorted(
            set(
                _list_of_strings(
                    raw.get("methods", []),
                    f"{ident}.methods",
                    allow_empty=False,
                )
            )
        )
        methods = [method.upper() for method in methods]
        if not set(methods) <= route_audit.MUTATING:
            raise SecurityPreflightError(
                f"{ident}: methods só pode conter POST/PUT/PATCH/DELETE."
            )
        required = _list_of_strings(
            raw.get("required_decorators", []),
            f"{ident}.required_decorators",
            allow_empty=False,
        )
        if raw.get("reviewed") is not True:
            raise SecurityPreflightError(
                f"{ident}: reviewed=true é obrigatório após revisão explícita da regra."
            )
        business_purpose = _required_text(
            raw.get("business_purpose"), f"{ident}.business_purpose"
        )
        reviewer = _required_text(raw.get("reviewer"), f"{ident}.reviewer")
        evidence = _list_of_strings(
            raw.get("evidence", []), f"{ident}.evidence", allow_empty=False
        )
        allow_csrf_exempt = raw.get("allow_csrf_exempt", False) is True
        csrf_reason = str(raw.get("csrf_reason") or "").strip()
        if allow_csrf_exempt and not csrf_reason:
            raise SecurityPreflightError(
                f"{ident}: csrf_reason é obrigatório quando allow_csrf_exempt=true."
            )
        rules.append(
            {
                "id": ident,
                "path": path,
                "methods": methods,
                "required_decorators": required,
                "allow_csrf_exempt": allow_csrf_exempt,
                "csrf_reason": csrf_reason,
                "reviewed": True,
                "business_purpose": business_purpose,
                "reviewer": reviewer,
                "evidence": evidence,
            }
        )

    return {
        "version": SPEC_VERSION,
        "auth_decorators": auth,
        "csrf_exempt_decorators": csrf,
        "rules": rules,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SecurityPreflightError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SecurityPreflightError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _matches(decorator: str, marker: str) -> bool:
    return route_audit._matches_marker(decorator, [marker])


def _route_key(route: dict) -> tuple[str | None, tuple[str, ...]]:
    methods = tuple(sorted(set(route["methods"]) & route_audit.MUTATING))
    return route["path"], methods


def build_preflight(root: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    route_policy = {
        "auth_decorators": normalized["auth_decorators"],
        "csrf_exempt_decorators": normalized["csrf_exempt_decorators"],
    }
    static = route_audit.audit_tree(root, route_policy)
    findings: list[dict] = []

    if static["errors"]:
        findings.append(
            {
                "code": "STATIC_PARSE_ERRORS",
                "severity": "block",
                "count": len(static["errors"]),
            }
        )

    mutating = [route for route in static["routes"] if route["mutating"]]
    rules_by_key: dict[tuple[str, tuple[str, ...]], dict] = {}
    for rule in normalized["rules"]:
        key = (rule["path"], tuple(sorted(rule["methods"])))
        if key in rules_by_key:
            raise SecurityPreflightError(
                f"Duas regras classificam o mesmo path/métodos: {rule['path']} {rule['methods']}"
            )
        rules_by_key[key] = rule

    matched_rule_ids: set[str] = set()
    route_results = []
    for route in mutating:
        key = _route_key(route)
        rule = rules_by_key.get(key)
        route_findings = []
        if rule is None:
            route_findings.append("UNCLASSIFIED_MUTATING_ROUTE")
        else:
            matched_rule_ids.add(rule["id"])
            for required in rule["required_decorators"]:
                if not any(_matches(item, required) for item in route["decorators"]):
                    route_findings.append(f"MISSING_REQUIRED_DECORATOR:{required}")
            if route["csrf_exempt"] and not rule["allow_csrf_exempt"]:
                route_findings.append("CSRF_EXEMPT_NOT_ALLOWED")

        if not route["auth_markers"]:
            route_findings.append("MISSING_AUTH_MARKER")

        if route_findings:
            findings.append(
                {
                    "code": "ROUTE_POLICY_VIOLATION",
                    "severity": "block",
                    "file": route["file"],
                    "line": route["line"],
                    "function": route["function"],
                    "path": route["path"],
                    "methods": route["methods"],
                    "violations": route_findings,
                }
            )
        route_results.append(
            {
                "file": route["file"],
                "line": route["line"],
                "function": route["function"],
                "path": route["path"],
                "methods": route["methods"],
                "rule_id": None if rule is None else rule["id"],
                "ok": not route_findings,
                "violations": route_findings,
            }
        )

    unused = sorted(
        set(rule["id"] for rule in normalized["rules"]) - matched_rule_ids
    )
    for rule_id in unused:
        findings.append(
            {
                "code": "POLICY_RULE_WITHOUT_ROUTE",
                "severity": "block",
                "rule_id": rule_id,
            }
        )

    return {
        "version": 1,
        "mode": "STATIC_SECURITY_PREFLIGHT_NOT_RUNTIME_HOMOLOGATION",
        "static_audit": static,
        "policy": normalized,
        "route_results": route_results,
        "findings": findings,
        "summary": {
            "routes": static["summary"]["routes"],
            "mutating_routes": len(mutating),
            "classified_mutating_routes": sum(
                1 for item in route_results if item["rule_id"]
            ),
            "approved_mutating_routes": sum(
                1 for item in route_results if item["ok"]
            ),
            "unused_rules": len(unused),
            "blocking_findings": len(findings),
        },
        "static_ok": len(findings) == 0,
        "runtime_homologated": False,
        "disclaimer": (
            "PASS estático não substitui teste dinâmico de autenticação, autorização de negócio, "
            "CSRF, sessão, concorrência ou manipulação de IDs no runtime reconciliado."
        ),
    }


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Pré-homologação estática de autenticação/autorização das rotas mutáveis V8."
        )
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("SECURITY_PREFLIGHT.json")
    )
    args = parser.parse_args()
    try:
        report = build_preflight(args.root, load_spec(args.spec))
        write_report(args.output, report)
    except (SecurityPreflightError, route_audit.RouteAuditError) as exc:
        print(f"SECURITY_PREFLIGHT_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "SECURITY_PREFLIGHT_OK"
        if report["static_ok"]
        else "SECURITY_PREFLIGHT_BLOQUEADO"
    )
    print(f"Rotas mutáveis: {report['summary']['mutating_routes']}")
    print(
        "Aprovadas estaticamente: "
        f"{report['summary']['approved_mutating_routes']}"
    )
    print(f"Achados bloqueantes: {report['summary']['blocking_findings']}")
    print("Runtime homologado: NÃO")
    return 0 if report["static_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
