from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

import audit_runtime_reconciliation as reconciliation

REPORT_NAME = "RECONCILED_STAGING_REPORT.json"
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
AREA_TARGET_MAP = {
    "src_app": "src",
    "src_root": "src",
    "tests_app": "tests",
    "tests_root": "tests",
    "scripts_app": "scripts",
    "scripts_root": "scripts",
    "migrations_app": "migrations",
    "migrations_root": "migrations",
    "alembic_app": "alembic",
    "alembic_root": "alembic",
    "templates_app": "templates",
    "templates_root": "templates",
    "static_app": "static",
    "static_root": "static",
    "config_app": "config",
    "config_root": "config",
}
METADATA_TARGET_MAP = {
    "app/pyproject.toml": "pyproject.toml",
    "pyproject.toml": "pyproject.toml",
    "app/requirements.txt": "requirements.txt",
    "requirements.txt": "requirements.txt",
    "app/requirements-dev.txt": "requirements-dev.txt",
    "requirements-dev.txt": "requirements-dev.txt",
}
RESOLVED_DECISIONS = {"ADOPT_RUNTIME", "KEEP_REPO", "EXCLUDE_WITH_REASON"}


class StagingVerificationError(RuntimeError):
    pass


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StagingVerificationError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise StagingVerificationError(f"JSON deve ser objeto: {path.name}")
    return value


def safe_relative(value: object) -> Path:
    text = str(value or "").replace("\\", "/").strip()
    pure = PurePosixPath(text)
    if (
        not text
        or pure.is_absolute()
        or ".." in pure.parts
        or "\x00" in text
        or (pure.parts and pure.parts[0].endswith(":"))
    ):
        raise StagingVerificationError(f"Caminho relativo inseguro: {value!r}")
    return Path(*pure.parts)


def verify_acceptance(acceptance: dict) -> None:
    if acceptance.get("version") != 1:
        raise StagingVerificationError("Versão do aceite não suportada.")
    if acceptance.get("mode") != "RECONCILIATION_BASELINE_ACCEPTANCE_NOT_EXECUTION":
        raise StagingVerificationError("Modo do aceite inválido.")
    if acceptance.get("review_complete") is not True or acceptance.get("baseline_ready") is not True:
        raise StagingVerificationError("Aceite não comprova baseline pronto.")
    if acceptance.get("automatic_write_allowed") is not False:
        raise StagingVerificationError("Aceite permite escrita automática indevida.")
    if acceptance.get("execution_performed") is not False:
        raise StagingVerificationError("Aceite contém execução indevida.")
    if acceptance.get("v8_homologated") is not False:
        raise StagingVerificationError("Aceite contém homologação indevida.")
    expected = str(acceptance.get("acceptance_sha256") or "").upper()
    payload = dict(acceptance)
    payload.pop("acceptance_sha256", None)
    if not SHA256_RE.fullmatch(expected) or canonical_hash(payload) != expected:
        raise StagingVerificationError("acceptance_sha256 inválido.")
    if not isinstance(acceptance.get("decisions"), list):
        raise StagingVerificationError("Aceite sem lista decisions.")


def verify_report_header(report: dict, acceptance: dict) -> None:
    if report.get("version") != 1:
        raise StagingVerificationError("Versão do relatório de staging não suportada.")
    if report.get("mode") != "RECONCILED_STAGING_MATERIALIZATION_NOT_DEPLOYMENT":
        raise StagingVerificationError("Modo do relatório de staging inválido.")
    if str(report.get("acceptance_sha256") or "").upper() != str(acceptance["acceptance_sha256"]).upper():
        raise StagingVerificationError("Relatório não está vinculado ao aceite informado.")
    required_false = (
        "repository_write_performed",
        "runtime_write_performed",
        "operational_deployment_performed",
        "automatic_write_to_sources",
        "v8_homologated",
    )
    if report.get("staging_materialization_performed") is not True:
        raise StagingVerificationError("Relatório não comprova materialização do staging.")
    for field in required_false:
        if report.get(field) is not False:
            raise StagingVerificationError(f"Flag de segurança inválida no relatório: {field}")
    expected = str(report.get("report_sha256") or "").upper()
    payload = dict(report)
    payload.pop("report_sha256", None)
    if not SHA256_RE.fullmatch(expected) or canonical_hash(payload) != expected:
        raise StagingVerificationError("report_sha256 inválido.")


def target_relative(decision: dict) -> str:
    area = str(decision.get("area") or "").strip()
    rel = str(decision.get("relative_path") or "").strip()
    if area == "metadata":
        target = METADATA_TARGET_MAP.get(rel)
        if target is None:
            raise StagingVerificationError(f"Metadata desconhecida no aceite: {rel}")
        return safe_relative(target).as_posix()
    base = AREA_TARGET_MAP.get(area)
    if base is None:
        raise StagingVerificationError(f"Área desconhecida no aceite: {area}")
    return (Path(base) / safe_relative(rel)).as_posix()


def validate_reported_files(staging_dir: Path, report: dict) -> list[dict]:
    reported = report.get("staging_files")
    if not isinstance(reported, list):
        raise StagingVerificationError("Relatório sem staging_files.")

    normalized: list[dict] = []
    seen: set[str] = set()
    for item in reported:
        if not isinstance(item, dict):
            raise StagingVerificationError("Entrada inválida em staging_files.")
        rel = safe_relative(item.get("relative_path")).as_posix()
        if rel == REPORT_NAME:
            raise StagingVerificationError("Relatório não pode listar a si próprio em staging_files.")
        if rel in seen:
            raise StagingVerificationError(f"Arquivo duplicado no relatório: {rel}")
        seen.add(rel)
        expected_hash = str(item.get("sha256") or "").upper()
        if not SHA256_RE.fullmatch(expected_hash):
            raise StagingVerificationError(f"SHA-256 inválido no relatório: {rel}")
        try:
            expected_size = int(item.get("size_bytes"))
        except (TypeError, ValueError) as exc:
            raise StagingVerificationError(f"Tamanho inválido no relatório: {rel}") from exc
        if expected_size < 0:
            raise StagingVerificationError(f"Tamanho negativo no relatório: {rel}")
        path = staging_dir / safe_relative(rel)
        if not path.is_file() or path.is_symlink():
            raise StagingVerificationError(f"Arquivo reportado ausente/inválido: {rel}")
        if path.stat().st_size != expected_size:
            raise StagingVerificationError(f"Tamanho divergente no staging: {rel}")
        if sha256_file(path) != expected_hash:
            raise StagingVerificationError(f"SHA-256 divergente no staging: {rel}")
        normalized.append({
            "relative_path": rel,
            "size_bytes": expected_size,
            "sha256": expected_hash,
        })

    actual: set[str] = set()
    for path in staging_dir.rglob("*"):
        rel = path.relative_to(staging_dir).as_posix()
        if path.is_symlink():
            raise StagingVerificationError(f"Symlink proibido no staging: {rel}")
        if path.is_file() and rel != REPORT_NAME:
            actual.add(rel)
    if actual != seen:
        extras = sorted(actual - seen)
        missing = sorted(seen - actual)
        details: list[str] = []
        if extras:
            details.append("extras=" + ",".join(extras))
        if missing:
            details.append("faltantes=" + ",".join(missing))
        raise StagingVerificationError("Conteúdo do staging diverge do relatório: " + "; ".join(details))

    normalized.sort(key=lambda item: item["relative_path"])
    if int(report.get("file_count") or -1) != len(normalized):
        raise StagingVerificationError("file_count diverge do conteúdo real.")
    if str(report.get("tree_sha256") or "").upper() != canonical_hash(normalized):
        raise StagingVerificationError("tree_sha256 diverge da árvore real.")
    return normalized


def validate_decisions(staging_dir: Path, report: dict, acceptance: dict) -> None:
    decisions = acceptance["decisions"]
    reported_applied = report.get("applied_decisions")
    if not isinstance(reported_applied, list):
        raise StagingVerificationError("Relatório sem applied_decisions.")

    expected_applied: list[dict] = []
    target_owners: dict[str, tuple[str, str]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise StagingVerificationError("Decisão inválida no aceite.")
        action = str(decision.get("decision") or "").strip().upper()
        if action not in RESOLVED_DECISIONS:
            raise StagingVerificationError(f"Decisão não resolvida no aceite: {action}")
        area = str(decision.get("area") or "").strip()
        rel = str(decision.get("relative_path") or "").strip()
        target_rel = target_relative(decision)
        owner = (area, rel)
        if target_rel in target_owners and target_owners[target_rel] != owner:
            raise StagingVerificationError(f"Colisão de destino aceita indevidamente: {target_rel}")
        target_owners[target_rel] = owner
        target = staging_dir / safe_relative(target_rel)

        if action == "ADOPT_RUNTIME":
            expected_hash = str(decision.get("runtime_sha256") or "").upper()
            if not SHA256_RE.fullmatch(expected_hash):
                raise StagingVerificationError(f"ADOPT_RUNTIME sem runtime_sha256 válido: {target_rel}")
            if not target.is_file() or target.is_symlink() or sha256_file(target) != expected_hash:
                raise StagingVerificationError(f"ADOPT_RUNTIME não materializado corretamente: {target_rel}")
        elif action == "KEEP_REPO":
            expected_hash = str(decision.get("repo_sha256") or "").upper()
            if not SHA256_RE.fullmatch(expected_hash):
                raise StagingVerificationError(f"KEEP_REPO sem repo_sha256 válido: {target_rel}")
            if not target.is_file() or target.is_symlink() or sha256_file(target) != expected_hash:
                raise StagingVerificationError(f"KEEP_REPO não preservado corretamente: {target_rel}")
        elif action == "EXCLUDE_WITH_REASON" and target.exists():
            raise StagingVerificationError(f"Arquivo excluído reapareceu no staging: {target_rel}")

        expected_applied.append({
            "area": area,
            "relative_path": rel,
            "target_relative_path": target_rel,
            "decision": action,
        })

    expected_applied.sort(key=lambda item: (item["area"], item["relative_path"]))
    actual_applied: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in reported_applied:
        if not isinstance(item, dict):
            raise StagingVerificationError("Entrada inválida em applied_decisions.")
        normalized = {
            "area": str(item.get("area") or "").strip(),
            "relative_path": str(item.get("relative_path") or "").strip(),
            "target_relative_path": safe_relative(item.get("target_relative_path")).as_posix(),
            "decision": str(item.get("decision") or "").strip().upper(),
        }
        key = (normalized["area"], normalized["relative_path"])
        if key in seen:
            raise StagingVerificationError(f"Decisão aplicada duplicada no relatório: {key[0]}/{key[1]}")
        seen.add(key)
        actual_applied.append(normalized)
    actual_applied.sort(key=lambda item: (item["area"], item["relative_path"]))
    if actual_applied != expected_applied:
        raise StagingVerificationError("applied_decisions diverge do aceite ou do mapeamento canônico.")


def verify_staging(staging_dir: Path, acceptance: dict) -> dict:
    staging_dir = staging_dir.resolve()
    if not staging_dir.is_dir():
        raise StagingVerificationError("Diretório de staging inválido.")
    report_path = staging_dir / REPORT_NAME
    if not report_path.is_file() or report_path.is_symlink():
        raise StagingVerificationError("Relatório de staging ausente/inválido.")

    before = {
        path.relative_to(staging_dir).as_posix(): sha256_file(path)
        for path in sorted(staging_dir.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }
    verify_acceptance(acceptance)
    report = load_json(report_path)
    verify_report_header(report, acceptance)
    normalized_files = validate_reported_files(staging_dir, report)
    validate_decisions(staging_dir, report, acceptance)

    forbidden = reconciliation.find_forbidden(staging_dir)
    suspicious = reconciliation.find_embedded_secrets(staging_dir)
    if forbidden:
        raise StagingVerificationError("Staging contém conteúdo proibido: " + ", ".join(forbidden))
    if suspicious:
        raise StagingVerificationError("Staging contém possível segredo: " + ", ".join(suspicious))

    after = {
        path.relative_to(staging_dir).as_posix(): sha256_file(path)
        for path in sorted(staging_dir.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }
    if before != after:
        raise StagingVerificationError("Verificação alterou o staging.")

    result = {
        "version": 1,
        "mode": "RECONCILED_STAGING_VERIFICATION_READ_ONLY",
        "acceptance_sha256": str(acceptance["acceptance_sha256"]),
        "materialization_report_sha256": str(report["report_sha256"]),
        "tree_sha256": str(report["tree_sha256"]),
        "file_count": len(normalized_files),
        "decisions_verified": len(acceptance["decisions"]),
        "staging_unchanged": True,
        "forbidden_content": [],
        "embedded_secrets": [],
        "operational_deployment_performed": False,
        "source_write_performed": False,
        "v8_homologated": False,
        "verification_ok": True,
    }
    result["verification_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica de forma read-only um staging reconciliado contra seu aceite e relatório de materialização."
    )
    parser.add_argument("--staging-dir", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.output is not None and args.output.exists():
        print("RECONCILED_STAGING_VERIFY_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        result = verify_staging(args.staging_dir, load_json(args.acceptance))
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    except (StagingVerificationError, OSError) as exc:
        print(f"RECONCILED_STAGING_VERIFY_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILED_STAGING_VERIFY_OK")
    print(f"Arquivos verificados: {result['file_count']}")
    print(f"Decisões verificadas: {result['decisions_verified']}")
    print("Staging alterado: NÃO")
    print("Deploy operacional: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
