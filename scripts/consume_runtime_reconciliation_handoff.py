from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

import audit_runtime_reconciliation as reconciliation
import build_database_homologation_preflight as database_preflight
import create_reconciliation_review_skeleton as review_skeleton
import plan_runtime_reconciliation as reconciliation_plan

MANIFEST_NAME = "RUNTIME_HANDOFF_MANIFEST.json"
REPORT_NAME = "RUNTIME_HANDOFF_CONSUMPTION.json"
PLAN_NAME = "RECONCILIATION_PLAN.json"
REVIEW_SKELETON_NAME = "RECONCILIATION_REVIEW_SKELETON.json"
MAX_ZIP_FILES = 20_000
MAX_ZIP_UNCOMPRESSED = 1_073_741_824


class HandoffConsumptionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HandoffConsumptionError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise HandoffConsumptionError(f"JSON deve ser objeto: {path.name}")
    return payload


def safe_named_file(root: Path, raw_name: object, label: str) -> Path:
    name = str(raw_name or "").strip()
    pure = PurePosixPath(name)
    if (
        not name
        or pure.is_absolute()
        or len(pure.parts) != 1
        or ".." in pure.parts
        or "\\" in name
        or "\x00" in name
    ):
        raise HandoffConsumptionError(f"{label} inválido no manifesto: {name!r}")
    path = (root / name).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise HandoffConsumptionError(f"{label} sai do handoff: {name!r}") from exc
    if not path.is_file() or path.is_symlink():
        raise HandoffConsumptionError(f"{label} ausente/inválido: {name}")
    return path


def snapshot_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def verify_handoff(handoff_dir: Path) -> tuple[dict, Path, Path, Path]:
    manifest_path = handoff_dir / MANIFEST_NAME
    manifest = load_json(manifest_path)
    if manifest.get("version") != 1:
        raise HandoffConsumptionError("Versão de handoff não suportada.")
    if manifest.get("mode") != "RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION":
        raise HandoffConsumptionError("Modo do handoff inválido.")

    expected_manifest_hash = str(manifest.get("manifest_sha256") or "").upper()
    hash_payload = dict(manifest)
    hash_payload.pop("manifest_sha256", None)
    if expected_manifest_hash != canonical_hash(hash_payload):
        raise HandoffConsumptionError("SHA-256 lógico do manifesto diverge.")

    source = manifest.get("source") or {}
    code = manifest.get("code_export") or {}
    database = manifest.get("database_copy") or {}
    if source.get("source_mutation_performed") is not False:
        raise HandoffConsumptionError("Manifesto não comprova origem intacta.")
    if code.get("database_in_code_zip") is not False:
        raise HandoffConsumptionError("Manifesto permite banco dentro do ZIP de código.")
    if database.get("kept_separate_from_code_zip") is not True:
        raise HandoffConsumptionError("Manifesto não comprova banco separado do ZIP.")

    code_zip = safe_named_file(handoff_dir, code.get("zip"), "ZIP de código")
    database_copy = safe_named_file(handoff_dir, database.get("file"), "cópia SQLite")
    database_report = safe_named_file(handoff_dir, database.get("report"), "relatório SQLite")

    if sha256_file(code_zip) != str(code.get("zip_sha256") or "").upper():
        raise HandoffConsumptionError("SHA-256 do ZIP de código diverge do manifesto.")
    if sha256_file(database_copy) != str(database.get("sha256") or "").upper():
        raise HandoffConsumptionError("SHA-256 da cópia SQLite diverge do manifesto.")
    if database_copy.stat().st_size != int(database.get("size_bytes") or -1):
        raise HandoffConsumptionError("Tamanho da cópia SQLite diverge do manifesto.")

    db_report = load_json(database_report)
    destination = db_report.get("destination") or {}
    if str(destination.get("schema_sha256") or "").upper() != str(database.get("schema_sha256") or "").upper():
        raise HandoffConsumptionError("Schema SHA-256 do relatório SQLite diverge do manifesto.")
    if destination.get("user_version") != database.get("user_version"):
        raise HandoffConsumptionError("user_version do relatório SQLite diverge do manifesto.")
    return manifest, code_zip, database_copy, database_report


def _zip_member_path(name: str) -> PurePosixPath:
    pure = PurePosixPath(name)
    if (
        not name
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in name
        or "\x00" in name
        or (pure.parts and pure.parts[0].endswith(":"))
    ):
        raise HandoffConsumptionError(f"Caminho inseguro no ZIP: {name!r}")
    return pure


def safe_extract_zip(zip_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ZIP_FILES:
            raise HandoffConsumptionError("ZIP excede limite de arquivos permitido.")
        total_size = sum(info.file_size for info in infos)
        if total_size > MAX_ZIP_UNCOMPRESSED:
            raise HandoffConsumptionError("ZIP excede limite descompactado permitido.")
        for info in infos:
            pure = _zip_member_path(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise HandoffConsumptionError(f"Symlink proibido no ZIP: {info.filename}")
            target = (destination / Path(*pure.parts)).resolve()
            try:
                target.relative_to(destination.resolve())
            except ValueError as exc:
                raise HandoffConsumptionError(f"Destino inseguro no ZIP: {info.filename}") from exc
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)


def assert_output_isolated(handoff_dir: Path, repo_root: Path, output_dir: Path) -> None:
    resolved = output_dir.resolve()
    for protected, label in ((handoff_dir.resolve(), "handoff"), (repo_root.resolve(), "repositório")):
        try:
            resolved.relative_to(protected)
        except ValueError:
            continue
        raise HandoffConsumptionError(f"Saída não pode ficar dentro do {label}.")


def default_plan_policy(repo_root: Path) -> Path:
    candidate = repo_root / "config/runtime_reconciliation_plan_policy_v8.json"
    if candidate.is_file():
        return candidate
    bundled = Path(__file__).resolve().parents[1] / "config/runtime_reconciliation_plan_policy_v8.json"
    if bundled.is_file():
        return bundled
    raise HandoffConsumptionError("Política canônica do plano de reconciliação não encontrada.")


def consume_handoff(
    handoff_dir: Path,
    repo_root: Path,
    output_dir: Path,
    *,
    invariants_path: Path,
    reconciliation_policy_path: Path | None = None,
    include_row_counts: bool = True,
) -> dict:
    handoff_dir = handoff_dir.resolve()
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if not handoff_dir.is_dir():
        raise HandoffConsumptionError("Diretório de handoff inválido.")
    if not repo_root.is_dir():
        raise HandoffConsumptionError("Raiz do repositório inválida.")
    assert_output_isolated(handoff_dir, repo_root, output_dir)
    if output_dir.exists():
        raise HandoffConsumptionError("Diretório de saída já existe; não será sobrescrito.")

    before = snapshot_tree(handoff_dir)
    manifest, code_zip, database_copy, _ = verify_handoff(handoff_dir)
    output_dir.mkdir(parents=True)
    try:
        extracted = output_dir / "runtime-extracted"
        extracted.mkdir()
        safe_extract_zip(code_zip, extracted)

        forbidden = reconciliation.find_forbidden(extracted)
        suspicious = reconciliation.find_embedded_secrets(extracted)
        manifest_ok, manifest_errors = reconciliation.verify_manifest(extracted)
        if forbidden:
            raise HandoffConsumptionError("ZIP extraído contém conteúdo proibido: " + ", ".join(forbidden))
        if suspicious:
            raise HandoffConsumptionError("ZIP extraído contém possível segredo: " + ", ".join(suspicious))
        if not manifest_ok:
            raise HandoffConsumptionError("Manifesto interno inválido: " + "; ".join(manifest_errors))

        reconciliation_dir = output_dir / "reconciliation-report"
        rows, metadata = reconciliation.audit_runtime(extracted, repo_root, reconciliation_dir)
        diff_summary = {
            status: sum(1 for row in rows if row.status == status)
            for status in ("SAME", "CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
        }

        policy_path = reconciliation_policy_path or default_plan_policy(repo_root)
        diff_payload = reconciliation_plan.load_json(reconciliation_dir / "RECONCILIATION_DIFF.json")
        plan_policy = reconciliation_plan.load_json(policy_path)
        plan = reconciliation_plan.build_plan(diff_payload, plan_policy)
        (output_dir / PLAN_NAME).write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        skeleton = review_skeleton.build_skeleton(plan)
        (output_dir / REVIEW_SKELETON_NAME).write_text(
            json.dumps(skeleton, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        invariant_spec = database_preflight.load_json(invariants_path)
        db_report = database_preflight.build_database_preflight(
            database_copy,
            invariant_spec,
            include_row_counts=include_row_counts,
        )
        (output_dir / "DATABASE_HOMOLOGATION_PREFLIGHT.json").write_text(
            json.dumps(db_report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        after = snapshot_tree(handoff_dir)
        if before != after:
            raise HandoffConsumptionError("Handoff foi alterado durante o consumo.")

        result = {
            "version": 1,
            "mode": "READ_ONLY_HANDOFF_CONSUMPTION_NOT_HOMOLOGATION",
            "handoff_manifest_sha256": manifest["manifest_sha256"],
            "handoff_unchanged": True,
            "internal_manifest_ok": True,
            "runtime_layout": metadata.get("runtime_layout"),
            "areas_compared": metadata.get("areas_compared", []),
            "diff_summary": diff_summary,
            "reconciliation_plan_file": PLAN_NAME,
            "reconciliation_plan_sha256": plan["plan_sha256"],
            "reconciliation_review_required": plan["summary"]["review_required"],
            "reconciliation_review_skeleton_file": REVIEW_SKELETON_NAME,
            "reconciliation_review_skeleton_sha256": skeleton["review_skeleton_sha256"],
            "reconciliation_review_pending": len(skeleton["items"]),
            "human_review_decisions_written": False,
            "automatic_reconciliation_write": False,
            "database_preflight_ok": bool(db_report["summary"]["all_ok"]),
            "database_sha256": db_report["database_snapshot"]["before"]["sha256"],
            "ready_for_reconciliation_review": True,
            "v8_homologated": False,
        }
        result["report_sha256"] = canonical_hash(result)
        (output_dir / REPORT_NAME).write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return result
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consome o handoff B06 em staging seguro, reconciliando código e auditando a cópia SQLite sem alterar a origem."
    )
    parser.add_argument("--handoff-dir", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--invariants",
        type=Path,
        default=None,
        help="Especificação de invariantes; padrão: config/sqlite_invariants_closing_confirmed_v8.json do repositório.",
    )
    parser.add_argument(
        "--reconciliation-policy",
        type=Path,
        default=None,
        help="Política do plano; padrão: config/runtime_reconciliation_plan_policy_v8.json.",
    )
    parser.add_argument("--skip-row-counts", action="store_true")
    parser.add_argument("--fail-on-diff", action="store_true")
    parser.add_argument("--require-db-ok", action="store_true")
    args = parser.parse_args()

    invariants_path = args.invariants or (args.repo_root / "config/sqlite_invariants_closing_confirmed_v8.json")
    try:
        result = consume_handoff(
            args.handoff_dir,
            args.repo_root,
            args.output_dir,
            invariants_path=invariants_path,
            reconciliation_policy_path=args.reconciliation_policy,
            include_row_counts=not args.skip_row_counts,
        )
    except (
        HandoffConsumptionError,
        database_preflight.DatabasePreflightError,
        reconciliation_plan.ReconciliationPlanError,
        review_skeleton.ReconciliationReviewSkeletonError,
        OSError,
        zipfile.BadZipFile,
    ) as exc:
        print(f"RUNTIME_HANDOFF_CONSUMPTION_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RUNTIME_HANDOFF_CONSUMPTION_OK")
    print(f"Handoff intacto: {'SIM' if result['handoff_unchanged'] else 'NÃO'}")
    for status, count in result["diff_summary"].items():
        print(f"{status}: {count}")
    print(f"Plano: {result['reconciliation_plan_file']}")
    print(f"Revisão obrigatória: {result['reconciliation_review_required']}")
    print(f"Esqueleto de revisão: {result['reconciliation_review_skeleton_file']}")
    print(f"Decisões humanas preenchidas: {'SIM' if result['human_review_decisions_written'] else 'NÃO'}")
    print("Escrita automática: NÃO")
    print(f"Preflight DB: {'OK' if result['database_preflight_ok'] else 'FALHA'}")
    print(f"Relatório: {REPORT_NAME}")
    print("V8 homologada: NÃO")

    if args.fail_on_diff and any(result["diff_summary"][item] for item in ("CHANGED", "RUNTIME_ONLY", "REPO_ONLY")):
        return 3
    if args.require_db_ok and not result["database_preflight_ok"]:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
