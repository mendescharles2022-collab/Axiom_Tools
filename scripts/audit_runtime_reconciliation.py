from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

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
    ".zip", ".7z", ".rar",
}
SENSITIVE_FILENAMES = {
    "credentials.json", "credential.json", "secrets.json", "secret.json",
    "token.json", "tokens.json", "service-account.json", "service_account.json",
}
TEXT_EXTENSIONS = {
    ".py", ".ps1", ".js", ".ts", ".html", ".css", ".json", ".toml",
    ".yaml", ".yml", ".ini", ".cfg", ".conf", ".txt", ".md", ".bat", ".cmd",
}
ASSIGNMENT_RE = re.compile(
    r'''(?im)["']?(api[_-]?key|client[_-]?secret|secret|token|password|senha)["']?'''
    r'''\s*[:=]\s*["']([^"']{8,})["']'''
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")
PLACEHOLDER_RE = re.compile(
    r"(example|dummy|placeholder|changeme|change-me|test|fake|mock|sample|fixture|"
    r"none|null|your_|seu_|not[-_ ]?a[-_ ]?real|env\[|getenv|os\.environ|"
    r"\$\{|%[^%]+%)",
    re.IGNORECASE,
)
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def should_ignore(path: Path) -> bool:
    return any(part.lower() in IGNORED_DIRS for part in path.parts)


def collect_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    result: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel_path = path.relative_to(root)
        if should_ignore(rel_path):
            continue
        result[rel_path.as_posix()] = path
    return result


def forbidden_name(path: Path) -> bool:
    name = path.name.lower()
    if path.is_dir() and name in FORBIDDEN_DIRS:
        return True
    if path.is_file():
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            return True
        if name == ".env" or name.startswith(".env."):
            return True
        if name in SENSITIVE_FILENAMES:
            return True
    return False


def find_forbidden(root: Path) -> list[str]:
    violations: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink():
            violations.append(rel.as_posix() + " [symlink]")
        elif forbidden_name(path):
            violations.append(rel.as_posix() + ("/" if path.is_dir() else ""))
    return sorted(set(violations))


def find_embedded_secrets(root: Path) -> list[str]:
    suspicious: list[str] = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if path.name in RESERVED_EXPORT_FILES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if PRIVATE_KEY_RE.search(content):
            suspicious.append(path.relative_to(root).as_posix())
            continue
        for match in ASSIGNMENT_RE.finditer(content):
            if not PLACEHOLDER_RE.search(match.group(2).strip()):
                suspicious.append(path.relative_to(root).as_posix())
                break
    return sorted(set(suspicious))


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
    try:
        target.relative_to(runtime_root.resolve())
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
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
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
            if expected_hash != sha256(path):
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
        runtime_file = runtime_files.get(rel)
        repo_file = repo_files.get(rel)
        if runtime_file and repo_file:
            runtime_hash = sha256(runtime_file)
            repo_hash = sha256(repo_file)
            rows.append(DiffRow(
                area, rel, "SAME" if runtime_hash == repo_hash else "CHANGED",
                runtime_hash, repo_hash, runtime_file.stat().st_size, repo_file.stat().st_size,
            ))
        elif runtime_file:
            rows.append(DiffRow(area, rel, "RUNTIME_ONLY", sha256(runtime_file), "", runtime_file.stat().st_size, 0))
        elif repo_file:
            rows.append(DiffRow(area, rel, "REPO_ONLY", "", sha256(repo_file), 0, repo_file.stat().st_size))
    return rows


def add_area_if_present(
    areas: list[tuple[str, Path, Path]],
    area: str,
    runtime_dir: Path,
    repo_dir: Path,
) -> None:
    if runtime_dir.is_dir():
        areas.append((area, runtime_dir, repo_dir))


def compare_metadata_file(area: str, label: str, runtime_file: Path, repo_file: Path) -> DiffRow | None:
    if not runtime_file.exists():
        return None
    if repo_file.exists():
        runtime_hash = sha256(runtime_file)
        repo_hash = sha256(repo_file)
        return DiffRow(
            area, label, "SAME" if runtime_hash == repo_hash else "CHANGED",
            runtime_hash, repo_hash, runtime_file.stat().st_size, repo_file.stat().st_size,
        )
    return DiffRow(area, label, "RUNTIME_ONLY", sha256(runtime_file), "", runtime_file.stat().st_size, 0)


def write_reports(rows: list[DiffRow], output_dir: Path, metadata: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "RECONCILIATION_DIFF.csv"
    json_path = output_dir / "RECONCILIATION_DIFF.json"
    fieldnames = [
        "area", "relative_path", "status", "runtime_sha256",
        "repo_sha256", "runtime_size", "repo_size",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
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


def build_areas(runtime_root: Path, repo_root: Path) -> list[tuple[str, Path, Path]]:
    areas: list[tuple[str, Path, Path]] = []
    add_area_if_present(areas, "src_app", runtime_root / "app" / "src", repo_root / "src")
    add_area_if_present(areas, "src_root", runtime_root / "src", repo_root / "src")
    add_area_if_present(areas, "tests_app", runtime_root / "app" / "tests", repo_root / "tests")
    add_area_if_present(areas, "tests_root", runtime_root / "tests", repo_root / "tests")
    add_area_if_present(areas, "scripts_app", runtime_root / "app" / "scripts", repo_root / "scripts")
    add_area_if_present(areas, "scripts_root", runtime_root / "scripts", repo_root / "scripts")
    add_area_if_present(areas, "migrations_app", runtime_root / "app" / "migrations", repo_root / "migrations")
    add_area_if_present(areas, "migrations_root", runtime_root / "migrations", repo_root / "migrations")
    add_area_if_present(areas, "alembic_app", runtime_root / "app" / "alembic", repo_root / "alembic")
    add_area_if_present(areas, "alembic_root", runtime_root / "alembic", repo_root / "alembic")
    add_area_if_present(areas, "templates_app", runtime_root / "app" / "templates", repo_root / "templates")
    add_area_if_present(areas, "templates_root", runtime_root / "templates", repo_root / "templates")
    add_area_if_present(areas, "static_app", runtime_root / "app" / "static", repo_root / "static")
    add_area_if_present(areas, "static_root", runtime_root / "static", repo_root / "static")
    add_area_if_present(areas, "config_app", runtime_root / "app" / "config", repo_root / "config")
    add_area_if_present(areas, "config_root", runtime_root / "config", repo_root / "config")
    return areas


def audit_runtime(runtime_root: Path, repo_root: Path, output_dir: Path) -> tuple[list[DiffRow], dict]:
    areas = build_areas(runtime_root, repo_root)
    rows: list[DiffRow] = []
    for area, runtime_dir, repo_dir in areas:
        rows.extend(compare_area(area, runtime_dir, repo_dir))

    metadata_pairs = [
        ("app/pyproject.toml", runtime_root / "app/pyproject.toml", repo_root / "pyproject.toml"),
        ("pyproject.toml", runtime_root / "pyproject.toml", repo_root / "pyproject.toml"),
        ("app/requirements.txt", runtime_root / "app/requirements.txt", repo_root / "requirements.txt"),
        ("requirements.txt", runtime_root / "requirements.txt", repo_root / "requirements.txt"),
        ("app/requirements-dev.txt", runtime_root / "app/requirements-dev.txt", repo_root / "requirements-dev.txt"),
        ("requirements-dev.txt", runtime_root / "requirements-dev.txt", repo_root / "requirements-dev.txt"),
    ]
    for label, runtime_file, repo_file in metadata_pairs:
        row = compare_metadata_file("metadata", label, runtime_file, repo_file)
        if row:
            rows.append(row)

    # Não registrar paths absolutos em artefatos que podem sair do servidor.
    metadata = {
        "runtime_layout": "app/src" if (runtime_root / "app" / "src").is_dir() else "src",
        "manifest_ok": True,
        "manifest_errors": [],
        "areas_compared": [area for area, _, _ in areas],
        "config_compared": any(area.startswith("config_") for area, _, _ in areas),
        "release_identity_compared": any(
            row.area.startswith("config_") and row.relative_path == "release_identity.toml"
            for row in rows
        ),
    }
    write_reports(rows, output_dir, metadata)
    return rows, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita a reconciliação entre runtime exportado e repositório Axiom Tools.")
    parser.add_argument("--runtime-root", required=True, type=Path, help="Pasta extraída do export seguro do runtime")
    parser.add_argument("--repo-root", required=True, type=Path, help="Raiz do clone/repositório Axiom_Tools")
    parser.add_argument("--output-dir", type=Path, default=Path("reconciliation-report"))
    parser.add_argument("--fail-on-diff", action="store_true", help="Retorna código 3 se houver qualquer diferença")
    args = parser.parse_args()

    runtime_root = args.runtime_root.resolve()
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
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

    suspicious = find_embedded_secrets(runtime_root)
    if suspicious:
        print("ERRO: export contém possível segredo hardcoded:", file=sys.stderr)
        for item in suspicious:
            print(f" - {item}", file=sys.stderr)
        return 2

    manifest_ok, manifest_errors = verify_manifest(runtime_root)
    if not manifest_ok:
        print("ERRO: manifesto de reconciliação inválido:", file=sys.stderr)
        for error in manifest_errors:
            print(f" - {error}", file=sys.stderr)
        return 2

    if not (runtime_root / "app" / "src").is_dir() and not (runtime_root / "src").is_dir():
        print("ERRO: export não contém app/src nem src; reconciliação de código não é possível.", file=sys.stderr)
        return 2

    rows, metadata = audit_runtime(runtime_root, repo_root, output_dir)
    summary = {
        status: sum(1 for row in rows if row.status == status)
        for status in ("SAME", "CHANGED", "RUNTIME_ONLY", "REPO_ONLY")
    }
    print("RECONCILIATION_AUDIT_OK")
    print("Manifesto: OK")
    print("Áreas:", ", ".join(metadata["areas_compared"]))
    for status, count in summary.items():
        print(f"{status}: {count}")
    print(f"Relatório: {output_dir.name}")

    if args.fail_on_diff and any(summary[state] for state in ("CHANGED", "RUNTIME_ONLY", "REPO_ONLY")):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
