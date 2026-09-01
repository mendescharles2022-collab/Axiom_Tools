from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

import audit_runtime_reconciliation as reconciliation

AREA_MAP = {
    "src_app": ("app/src", "src"),
    "src_root": ("src", "src"),
    "tests_app": ("app/tests", "tests"),
    "tests_root": ("tests", "tests"),
    "scripts_app": ("app/scripts", "scripts"),
    "scripts_root": ("scripts", "scripts"),
    "migrations_app": ("app/migrations", "migrations"),
    "migrations_root": ("migrations", "migrations"),
    "alembic_app": ("app/alembic", "alembic"),
    "alembic_root": ("alembic", "alembic"),
    "templates_app": ("app/templates", "templates"),
    "templates_root": ("templates", "templates"),
    "static_app": ("app/static", "static"),
    "static_root": ("static", "static"),
    "config_app": ("app/config", "config"),
    "config_root": ("config", "config"),
}
METADATA_MAP = {
    "app/pyproject.toml": ("app/pyproject.toml", "pyproject.toml"),
    "pyproject.toml": ("pyproject.toml", "pyproject.toml"),
    "app/requirements.txt": ("app/requirements.txt", "requirements.txt"),
    "requirements.txt": ("requirements.txt", "requirements.txt"),
    "app/requirements-dev.txt": ("app/requirements-dev.txt", "requirements-dev.txt"),
    "requirements-dev.txt": ("requirements-dev.txt", "requirements-dev.txt"),
}
REPO_SCOPE_DIRS = ("src", "tests", "scripts", "migrations", "alembic", "templates", "static", "config")
REPO_SCOPE_FILES = ("pyproject.toml", "requirements.txt", "requirements-dev.txt")
RESOLVED_DECISIONS = {"ADOPT_RUNTIME", "KEEP_REPO", "EXCLUDE_WITH_REASON"}
REPORT_NAME = "RECONCILED_STAGING_REPORT.json"


class StagingMaterializationError(RuntimeError):
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
        raise StagingMaterializationError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise StagingMaterializationError(f"JSON deve ser objeto: {path.name}")
    return value


def verify_acceptance(acceptance: dict) -> None:
    if acceptance.get("version") != 1:
        raise StagingMaterializationError("Versão do aceite não suportada.")
    if acceptance.get("mode") != "RECONCILIATION_BASELINE_ACCEPTANCE_NOT_EXECUTION":
        raise StagingMaterializationError("Modo do aceite inválido.")
    if acceptance.get("review_complete") is not True or acceptance.get("baseline_ready") is not True:
        raise StagingMaterializationError("Aceite não comprova revisão completa e baseline pronto.")
    if acceptance.get("automatic_write_allowed") is not False:
        raise StagingMaterializationError("Aceite permite escrita automática indevida.")
    if acceptance.get("execution_performed") is not False:
        raise StagingMaterializationError("Aceite já declara execução indevida.")
    if acceptance.get("v8_homologated") is not False:
        raise StagingMaterializationError("Aceite contém homologação indevida.")
    expected = str(acceptance.get("acceptance_sha256") or "").upper()
    payload = dict(acceptance)
    payload.pop("acceptance_sha256", None)
    if expected != canonical_hash(payload):
        raise StagingMaterializationError("acceptance_sha256 inválido.")
    decisions = acceptance.get("decisions")
    if not isinstance(decisions, list):
        raise StagingMaterializationError("Aceite sem lista decisions.")


def safe_relative(value: str) -> Path:
    text = str(value or "").replace("\\", "/").strip()
    pure = PurePosixPath(text)
    if not text or pure.is_absolute() or ".." in pure.parts or "\x00" in text:
        raise StagingMaterializationError(f"Caminho relativo inseguro: {value!r}")
    if pure.parts and pure.parts[0].endswith(":"):
        raise StagingMaterializationError(f"Caminho relativo inseguro: {value!r}")
    return Path(*pure.parts)


def decision_paths(runtime_root: Path, repo_root: Path, decision: dict) -> tuple[Path, Path, str]:
    area = str(decision.get("area") or "").strip()
    relative = str(decision.get("relative_path") or "").strip()
    if area == "metadata":
        mapping = METADATA_MAP.get(relative)
        if mapping is None:
            raise StagingMaterializationError(f"Metadata desconhecida: {relative}")
        runtime_rel, repo_rel = mapping
        return runtime_root / safe_relative(runtime_rel), repo_root / safe_relative(repo_rel), repo_rel
    mapping = AREA_MAP.get(area)
    if mapping is None:
        raise StagingMaterializationError(f"Área desconhecida no aceite: {area}")
    runtime_base, repo_base = mapping
    rel_path = safe_relative(relative)
    target_rel = (Path(repo_base) / rel_path).as_posix()
    return runtime_root / runtime_base / rel_path, repo_root / repo_base / rel_path, target_rel


def _validate_source(path: Path, expected_hash: str, label: str) -> None:
    expected = str(expected_hash or "").upper()
    if not expected:
        if path.exists():
            raise StagingMaterializationError(f"{label} deveria estar ausente: {path.name}")
        return
    if not path.is_file() or path.is_symlink():
        raise StagingMaterializationError(f"{label} ausente/inválido: {path}")
    if sha256_file(path) != expected:
        raise StagingMaterializationError(f"SHA-256 divergente em {label}: {path}")


def _assert_no_symlink(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise StagingMaterializationError(f"Symlink proibido na origem de staging: {path}")


def copy_repo_scope(repo_root: Path, staging_root: Path) -> None:
    _assert_no_symlink(repo_root)
    for name in REPO_SCOPE_DIRS:
        source = repo_root / name
        if source.is_dir():
            shutil.copytree(source, staging_root / name)
    for name in REPO_SCOPE_FILES:
        source = repo_root / name
        if source.is_file():
            target = staging_root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def snapshot_tree(root: Path) -> list[dict]:
    files: list[dict] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise StagingMaterializationError(f"Symlink proibido no staging: {path}")
        if path.is_file() and path.name != REPORT_NAME:
            files.append({
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    return files


def materialize_staging(runtime_root: Path, repo_root: Path, output_dir: Path, acceptance: dict) -> dict:
    runtime_root = runtime_root.resolve()
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    verify_acceptance(acceptance)
    if not runtime_root.is_dir() or not repo_root.is_dir():
        raise StagingMaterializationError("Runtime extraído ou repositório inválido.")
    for protected, label in ((runtime_root, "runtime"), (repo_root, "repositório")):
        try:
            output_dir.relative_to(protected)
        except ValueError:
            pass
        else:
            raise StagingMaterializationError(f"Staging não pode ficar dentro do {label}.")
    if output_dir.exists():
        raise StagingMaterializationError("Diretório de staging já existe; não será sobrescrito.")

    decisions = acceptance["decisions"]
    resolved: list[tuple[dict, Path, Path, str]] = []
    targets: dict[str, tuple[str, str]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise StagingMaterializationError("Decisão inválida no aceite.")
        action = str(decision.get("decision") or "").strip().upper()
        if action not in RESOLVED_DECISIONS:
            raise StagingMaterializationError(f"Decisão não resolvida no aceite: {action}")
        runtime_path, repo_path, target_rel = decision_paths(runtime_root, repo_root, decision)
        identity = (str(decision.get("area") or ""), str(decision.get("relative_path") or ""))
        if target_rel in targets and targets[target_rel] != identity:
            raise StagingMaterializationError(
                f"Colisão de destino no staging: {target_rel} <- {targets[target_rel]} e {identity}"
            )
        targets[target_rel] = identity
        _validate_source(runtime_path, str(decision.get("runtime_sha256") or ""), "runtime")
        _validate_source(repo_path, str(decision.get("repo_sha256") or ""), "repositório")
        resolved.append((decision, runtime_path, repo_path, target_rel))

    output_dir.mkdir(parents=True)
    try:
        copy_repo_scope(repo_root, output_dir)
        applied: list[dict] = []
        for decision, runtime_path, _, target_rel in resolved:
            action = str(decision["decision"]).upper()
            target = output_dir / safe_relative(target_rel)
            if action == "ADOPT_RUNTIME":
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(runtime_path, target)
                expected = str(decision.get("runtime_sha256") or "").upper()
                if not target.is_file() or sha256_file(target) != expected:
                    raise StagingMaterializationError(f"Falha ao materializar runtime em {target_rel}")
            elif action == "KEEP_REPO":
                expected = str(decision.get("repo_sha256") or "").upper()
                if not target.is_file() or sha256_file(target) != expected:
                    raise StagingMaterializationError(f"Staging não preservou repo em {target_rel}")
            elif action == "EXCLUDE_WITH_REASON":
                if target.exists():
                    if not target.is_file() or target.is_symlink():
                        raise StagingMaterializationError(f"Exclusão só pode atingir arquivo regular: {target_rel}")
                    target.unlink()
                if target.exists():
                    raise StagingMaterializationError(f"Arquivo excluído permaneceu no staging: {target_rel}")
            applied.append({
                "area": str(decision.get("area") or ""),
                "relative_path": str(decision.get("relative_path") or ""),
                "target_relative_path": target_rel,
                "decision": action,
            })

        forbidden = reconciliation.find_forbidden(output_dir)
        suspicious = reconciliation.find_embedded_secrets(output_dir)
        if forbidden:
            raise StagingMaterializationError("Staging contém conteúdo proibido: " + ", ".join(forbidden))
        if suspicious:
            raise StagingMaterializationError("Staging contém possível segredo: " + ", ".join(suspicious))

        tree = snapshot_tree(output_dir)
        report = {
            "version": 1,
            "mode": "RECONCILED_STAGING_MATERIALIZATION_NOT_DEPLOYMENT",
            "acceptance_sha256": str(acceptance["acceptance_sha256"]),
            "applied_decisions": applied,
            "file_count": len(tree),
            "tree_sha256": canonical_hash(tree),
            "staging_files": tree,
            "staging_materialization_performed": True,
            "repository_write_performed": False,
            "runtime_write_performed": False,
            "operational_deployment_performed": False,
            "automatic_write_to_sources": False,
            "v8_homologated": False,
        }
        report["report_sha256"] = canonical_hash(report)
        (output_dir / REPORT_NAME).write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return report
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materializa baseline reconciliado exclusivamente em staging isolado a partir de aceite válido."
    )
    parser.add_argument("--runtime-extracted", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    try:
        report = materialize_staging(
            args.runtime_extracted,
            args.repo_root,
            args.output_dir,
            load_json(args.acceptance),
        )
    except (StagingMaterializationError, OSError, shutil.Error) as exc:
        print(f"RECONCILED_STAGING_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILED_STAGING_OK")
    print(f"Decisões aplicadas no staging: {len(report['applied_decisions'])}")
    print(f"Arquivos no staging: {report['file_count']}")
    print("Repositório alterado: NÃO")
    print("Runtime alterado: NÃO")
    print("Deploy operacional: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
