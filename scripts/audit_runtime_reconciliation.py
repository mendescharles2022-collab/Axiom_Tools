from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

FORBIDDEN_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "data", "database", "databases", "db", "documentos", "documents",
    "uploads", "upload", "logs", "log", "backups", "backup", "temp", "tmp",
    "certificados", "certificates", "secrets", "tokens", "cache", "caches",
}
FORBIDDEN_EXTENSIONS = {
    ".sqlite", ".sqlite3", ".db", ".mdb", ".accdb",
    ".pfx", ".p12", ".p7b", ".p7c", ".cer", ".crt", ".der",
    ".pem", ".key", ".jks", ".kdb", ".kdbx",
}
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
MANIFEST_NAME = "RECONCILIATION_MANIFEST.csv"


@dataclass(frozen=True)
class DiffRow:
    area: str
    relative_path: str
    status: str
    runtime_sha256: str = ""
    repo_sha256: str = ""
    runtime_size: int = 0
    repo_size: int = 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def should_ignore(path: Path) -> bool:
    return any(part.lower() in IGNORED_DIRS for part in path.parts)


def collect_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    result: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file() or should_ignore(path.relative_to(root)):
            continue
        rel = path.relative_to(root).as_posix()
        result[rel] = path
    return result


def find_forbidden(root: Path) -> list[str]:
    violations: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        lowered_parts = {p.lower() for p in rel.parts}
        if path.is_dir() and path.name.lower() in FORBIDDEN_DIRS:
            violations.append(rel.as_posix() + "/")
            continue
        if path.is_file():
            name = path.name.lower()
            if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
                violations.append(rel.as_posix())
            elif name == ".env" or name.startswith(".env."):
                violations.append(rel.as_posix())
            elif lowered_parts & {"certificados", "certificates", "secrets", "tokens"}:
                violations.append(rel.as_posix())
    return sorted(set(violations))


def verify_manifest(runtime_root: Path) -> tuple[bool, list[str]]:
    manifest = runtime_root / MANIFEST_NAME
    if not manifest.exists():
        return False, [f"Manifesto ausente: {MANIFEST_NAME}"]

    errors: list[str] = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"RelativePath", "Length", "SHA256"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            return False, ["Manifesto sem colunas obrigatórias RelativePath/Length/SHA256"]

        for row in reader:
            rel = (row.get("RelativePath") or "").replace("\\", "/").lstrip("/")
            if not rel:
                errors.append("Linha de manifesto sem RelativePath")
                continue
            path = runtime_root / Path(rel)
            if not path.exists() or not path.is_file():
                errors.append(f"Arquivo do manifesto ausente: {rel}")
                continue
            try:
                expected_len = int(row.get("Length") or "0")
            except ValueError:
                errors.append(f"Length inválido no manifesto: {rel}")
                continue
            if path.stat().st_size != expected_len:
                errors.append(f"Tamanho divergente: {rel}")
            expected_hash = (row.get("SHA256") or "").upper()
            actual_hash = sha256(path)
            if expected_hash != actual_hash:
                errors.append(f"SHA256 divergente: {rel}")

    return not errors, errors


def compare_area(area: str, runtime_dir: Path, repo_dir: Path) -> list[DiffRow]:
    runtime_files = collect_files(runtime_dir)
    repo_files = collect_files(repo_dir)
    rows: list[DiffRow] = []

    for rel in sorted(set(runtime_files) | set(repo_files)):
        rp = runtime_files.get(rel)
        gp = repo_files.get(rel)
        if rp and gp:
            r_hash = sha256(rp)
            g_hash = sha256(gp)
            status = "SAME" if r_hash == g_hash else "CHANGED"
            rows.append(DiffRow(area, rel, status, r_hash, g_hash, rp.stat().st_size, gp.stat().st_size))
        elif rp:
            rows.append(DiffRow(area, rel, "RUNTIME_ONLY", sha256(rp), "", rp.stat().st_size, 0))
        elif gp:
            rows.append(DiffRow(area, rel, "REPO_ONLY", "", sha256(gp), 0, gp.stat().st_size))
    return rows


def resolve_runtime_area(runtime_root: Path, candidates: Iterable[str]) -> Path | None:
    for candidate in candidates:
        path = runtime_root / candidate
        if path.exists() and path.is_dir():
            return path
    return None


def write_reports(rows: list[DiffRow], output_dir: Path, metadata: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "RECONCILIATION_DIFF.csv"
    json_path = output_dir / "RECONCILIATION_DIFF.json"

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(asdict(rows[0]).keys()) if rows else [
                "area", "relative_path", "status", "runtime_sha256",
                "repo_sha256", "runtime_size", "repo_size",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    payload = {
        "metadata": metadata,
        "summary": {
            status: sum(1 for row in rows if row.status == status)
            for status in ("SAME", "CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
        },
        "rows": [asdict(row) for row in rows],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita a reconciliação entre runtime exportado e repositório Axiom Tools."
    )
    parser.add_argument(
        "--runtime-root", required=True, type=Path,
        help="Pasta extraída do export seguro do runtime",
    )
    parser.add_argument(
        "--repo-root", required=True, type=Path,
        help="Raiz do clone/repositório Axiom_Tools",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("reconciliation-report")
    )
    parser.add_argument(
        "--fail-on-diff", action="store_true",
        help="Retorna código 3 se houver qualquer diferença",
    )
    args = parser.parse_args()

    runtime_root = args.runtime_root.resolve()
    repo_root = args.repo_root.resolve()

    if not runtime_root.is_dir():
        print(f"ERRO: runtime-root inválido: {runtime_root}", file=sys.stderr)
        return 2
    if not repo_root.is_dir():
        print(f"ERRO: repo-root inválido: {repo_root}", file=sys.stderr)
        return 2

    forbidden = find_forbidden(runtime_root)
    if forbidden:
        print("ERRO: export contém conteúdo proibido/sensível:", file=sys.stderr)
        for item in forbidden:
            print(f" - {item}", file=sys.stderr)
        return 2

    manifest_ok, manifest_errors = verify_manifest(runtime_root)

    areas: list[tuple[str, Path, Path]] = []
    runtime_src = resolve_runtime_area(runtime_root, ("app/src", "src"))
    runtime_tests = resolve_runtime_area(runtime_root, ("app/tests", "tests"))
    runtime_scripts = resolve_runtime_area(runtime_root, ("app/scripts", "scripts"))

    if runtime_src:
        areas.append(("src", runtime_src, repo_root / "src"))
    if runtime_tests:
        areas.append(("tests", runtime_tests, repo_root / "tests"))
    if runtime_scripts:
        areas.append(("scripts", runtime_scripts, repo_root / "scripts"))

    rows: list[DiffRow] = []
    for area, runtime_dir, repo_dir in areas:
        rows.extend(compare_area(area, runtime_dir, repo_dir))

    metadata_pairs = [
        ("pyproject.toml", runtime_root / "pyproject.toml", repo_root / "pyproject.toml"),
        ("app/pyproject.toml", runtime_root / "app/pyproject.toml", repo_root / "pyproject.toml"),
    ]
    seen_meta = False
    for label, runtime_file, repo_file in metadata_pairs:
        if not runtime_file.exists() or seen_meta:
            continue
        seen_meta = True
        if repo_file.exists():
            r_hash = sha256(runtime_file)
            g_hash = sha256(repo_file)
            rows.append(
                DiffRow(
                    "metadata", label,
                    "SAME" if r_hash == g_hash else "CHANGED",
                    r_hash, g_hash,
                    runtime_file.stat().st_size, repo_file.stat().st_size,
                )
            )
        else:
            rows.append(
                DiffRow(
                    "metadata", label, "RUNTIME_ONLY",
                    sha256(runtime_file), "", runtime_file.stat().st_size, 0,
                )
            )

    metadata = {
        "runtime_root": str(runtime_root),
        "repo_root": str(repo_root),
        "manifest_ok": manifest_ok,
        "manifest_errors": manifest_errors,
        "areas_compared": [area for area, _, _ in areas],
    }
    write_reports(rows, args.output_dir.resolve(), metadata)

    summary = {
        status: sum(1 for row in rows if row.status == status)
        for status in ("SAME", "CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
    }

    print("RECONCILIATION_AUDIT_OK")
    print(f"Manifesto: {'OK' if manifest_ok else 'COM ERROS'}")
    for error in manifest_errors:
        print(f"  - {error}")
    print("Áreas:", ", ".join(metadata["areas_compared"]) or "nenhuma")
    for status, count in summary.items():
        print(f"{status}: {count}")
    print(f"Relatório: {args.output_dir.resolve()}")

    if args.fail_on_diff and any(
        summary[s] for s in ("CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
    ):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
