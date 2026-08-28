from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
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
INFO_NAME = "RECONCILIATION_INFO.txt"
RESERVED_EXPORT_FILES = {MANIFEST_NAME, INFO_NAME}
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


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
        if path.is_symlink():
            continue
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
        if path.is_symlink():
            violations.append(rel.as_posix() + " [symlink]")
            continue
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


def safe_manifest_target(runtime_root: Path, raw_relative: str) -> tuple[str, Path] | None:
    rel = raw_relative.replace("\\", "/").strip()
    if not rel:
        return None

    pure = PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        return None
    if pure.parts[0].endswith(":") or "\x00" in rel:
        return None

    normalized = pure.as_posix()
    target = (runtime_root / Path(*pure.parts)).resolve()
    root_resolved = runtime_root.resolve()

    try:
        target.relative_to(root_resolved)
    except ValueError:
        return None

    return normalized, target


def verify_manifest(runtime_root: Path) -> tuple[bool, list[str]]:
    manifest = runtime_root / MANIFEST_NAME
    if not manifest.exists():
        return False, [f"Manifesto ausente: {MANIFEST_NAME}"]

    errors: list[str] = []
    expected_files: set[str] = set()
    seen_files: set[str] = set()

    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"RelativePath", "Length", "SHA256"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            return False, ["Manifesto sem colunas obrigatórias RelativePath/Length/SHA256"]

        for line_no, row in enumerate(reader, start=2):
            raw_rel = row.get("RelativePath") or ""
            safe = safe_manifest_target(runtime_root, raw_rel)
            if safe is None:
                errors.append(f"Caminho inválido no manifesto (linha {line_no}): {raw_rel!r}")
                continue

            rel, path = safe
            if rel in RESERVED_EXPORT_FILES:
                errors.append(f"Arquivo reservado não deve constar no manifesto: {rel}")
                continue
            if rel in seen_files:
                errors.append(f"RelativePath duplicado no manifesto: {rel}")
                continue
            seen_files.add(rel)
            expected_files.add(rel)

            if not path.exists() or not path.is_file() or path.is_symlink():
                errors.append(f"Arquivo do manifesto ausente/inválido: {rel}")
                continue

            try:
                expected_len = int(row.get("Length") or "0")
            except ValueError:
                errors.append(f"Length inválido no manifesto: {rel}")
                continue
            if expected_len < 0:
                errors.append(f"Length negativo no manifesto: {rel}")
                continue
            if path.stat().st_size != expected_len:
                errors.append(f"Tamanho divergente: {rel}")

            expected_hash = (row.get("SHA256") or "").strip().upper()
            if not SHA256_RE.fullmatch(expected_hash):
                errors.append(f"SHA256 inválido no manifesto: {rel}")
                continue
            actual_hash = sha256(path)
            if expected_hash != actual_hash:
                errors.append(f"SHA256 divergente: {rel}")

    actual_files = {
        path.relative_to(runtime_root).as_posix()
        for path in runtime_root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and path.relative_to(runtime_root).as_posix() not in RESERVED_EXPORT_FILES
        and not should_ignore(path.relative_to(runtime_root))
    }

    for rel in sorted(actual_files - expected_files):
        errors.append(f"Arquivo extra fora do manifesto: {rel}")
    for rel in sorted(expected_files - actual_files):
        errors.append(f"Arquivo listado no manifesto não encontrado: {rel}")

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

    fieldnames = [
        "area", "relative_path", "status", "runtime_sha256",
        "repo_sha256", "runtime_size", "repo_size",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
    if not manifest_ok:
        print("ERRO: manifesto de reconciliação inválido:", file=sys.stderr)
        for error in manifest_errors:
            print(f" - {error}", file=sys.stderr)
        return 2

    runtime_src = resolve_runtime_area(runtime_root, ("app/src", "src"))
    if runtime_src is None:
        print("ERRO: export não contém app/src nem src; reconciliação de código não é possível.", file=sys.stderr)
        return 2

    areas: list[tuple[str, Path, Path]] = [
        ("src", runtime_src, repo_root / "src"),
    ]

    runtime_tests = resolve_runtime_area(runtime_root, ("app/tests", "tests"))
    if runtime_tests:
        areas.append(("tests", runtime_tests, repo_root / "tests"))

    app_scripts = runtime_root / "app" / "scripts"
    root_scripts = runtime_root / "scripts"
    if app_scripts.is_dir():
        areas.append(("scripts_app", app_scripts, repo_root / "scripts"))
    if root_scripts.is_dir():
        areas.append(("scripts_root", root_scripts, repo_root / "scripts"))

    rows: list[DiffRow] = []
    for area, runtime_dir, repo_dir in areas:
        rows.extend(compare_area(area, runtime_dir, repo_dir))

    metadata_pairs = [
        ("app/pyproject.toml", runtime_root / "app/pyproject.toml", repo_root / "pyproject.toml"),
        ("pyproject.toml", runtime_root / "pyproject.toml", repo_root / "pyproject.toml"),
    ]
    for label, runtime_file, repo_file in metadata_pairs:
        if not runtime_file.exists():
            continue
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
        "manifest_ok": True,
        "manifest_errors": [],
        "areas_compared": [area for area, _, _ in areas],
    }
    write_reports(rows, args.output_dir.resolve(), metadata)

    summary = {
        status: sum(1 for row in rows if row.status == status)
        for status in ("SAME", "CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
    }

    print("RECONCILIATION_AUDIT_OK")
    print("Manifesto: OK")
    print("Áreas:", ", ".join(metadata["areas_compared"]))
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
