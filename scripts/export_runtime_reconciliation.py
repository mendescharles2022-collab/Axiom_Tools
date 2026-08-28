from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import stat
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = "RECONCILIATION_MANIFEST.csv"
INFO_NAME = "RECONCILIATION_INFO.txt"

FORBIDDEN_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
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
TEXT_EXTENSIONS = {
    ".py", ".ps1", ".js", ".ts", ".html", ".css", ".json", ".toml",
    ".yaml", ".yml", ".ini", ".cfg", ".conf", ".txt", ".md", ".bat", ".cmd",
}
ASSIGNMENT_RE = re.compile(
    r"(?im)\b(api[_-]?key|client[_-]?secret|secret|token|password|senha)\b"
    r"\s*[:=]\s*[\"']([^\"']{8,})[\"']"
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")
PLACEHOLDER_RE = re.compile(
    r"(example|dummy|placeholder|changeme|change-me|test|none|null|your_|seu_|"
    r"env\[|getenv|os\.environ|\$\{|%[^%]+%)",
    re.IGNORECASE,
)
LABEL_RE = re.compile(r"^[A-Za-z0-9._-]+$")

CANDIDATES = (
    ("app/src", "app/src"),
    ("app/tests", "app/tests"),
    ("app/scripts", "app/scripts"),
    ("app/migrations", "app/migrations"),
    ("app/alembic", "app/alembic"),
    ("scripts", "scripts"),
    ("app/pyproject.toml", "app/pyproject.toml"),
    ("app/requirements.txt", "app/requirements.txt"),
    ("app/requirements-dev.txt", "app/requirements-dev.txt"),
    ("pyproject.toml", "pyproject.toml"),
    ("requirements.txt", "requirements.txt"),
)


@dataclass(frozen=True)
class ExportResult:
    stage: Path
    zip_path: Path
    zip_sha256: str
    file_count: int


class ExportError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        if hasattr(path, "is_junction") and path.is_junction():
            return True
    except OSError:
        return True
    try:
        attrs = path.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def assert_under_root(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ExportError(f"Caminho fora da raiz permitida: {path}") from exc


def assert_no_reparse_tree(source: Path) -> None:
    if is_reparse_point(source):
        raise ExportError(f"Origem é junction/symlink/reparse point: {source}")
    if source.is_dir():
        for item in source.rglob("*"):
            if is_reparse_point(item):
                raise ExportError(f"Reparse point encontrado dentro da origem: {item}")


def forbidden_name(path: Path) -> bool:
    name = path.name.lower()
    if path.is_dir() and name in FORBIDDEN_DIRS:
        return True
    if path.is_file():
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            return True
        if name == ".env" or name.startswith(".env."):
            return True
        if re.search(r"(secret|token|credential|senha|password)", name, re.IGNORECASE):
            return True
    return False


def copy_safe(source: Path, destination: Path, root: Path) -> bool:
    if not source.exists():
        return False
    assert_under_root(source, root)
    assert_no_reparse_tree(source)

    if source.is_dir():
        def ignore(directory: str, names: list[str]) -> set[str]:
            ignored: set[str] = set()
            base = Path(directory)
            for name in names:
                candidate = base / name
                if forbidden_name(candidate):
                    ignored.add(name)
            return ignored

        shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignore)
    else:
        if forbidden_name(source):
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return True


def prune_forbidden(stage: Path) -> None:
    items = sorted(stage.rglob("*"), key=lambda p: len(p.parts), reverse=True)
    for path in items:
        if not path.exists() and not path.is_symlink():
            continue
        if is_reparse_point(path):
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink(missing_ok=True)
            continue
        if forbidden_name(path):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=False)
            else:
                path.unlink(missing_ok=True)


def find_forbidden(stage: Path) -> list[str]:
    violations: list[str] = []
    for path in stage.rglob("*"):
        rel = path.relative_to(stage).as_posix()
        if is_reparse_point(path):
            violations.append(rel + " [reparse]")
        elif forbidden_name(path):
            violations.append(rel + ("/" if path.is_dir() else ""))
    return sorted(set(violations))


def find_embedded_secrets(stage: Path) -> list[str]:
    suspicious: list[str] = []
    for path in stage.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if PRIVATE_KEY_RE.search(content):
            suspicious.append(path.relative_to(stage).as_posix())
            continue

        for match in ASSIGNMENT_RE.finditer(content):
            value = match.group(2).strip()
            if PLACEHOLDER_RE.search(value):
                continue
            suspicious.append(path.relative_to(stage).as_posix())
            break
    return sorted(set(suspicious))


def copy_entrypoints(root: Path, stage: Path, copied: list[str]) -> None:
    for source_root, relative_base in ((root, Path()), (root / "app", Path("app"))):
        if not source_root.is_dir():
            continue
        for source in source_root.glob("*.py"):
            if is_reparse_point(source):
                raise ExportError(f"Arquivo de entrada é reparse point: {source}")
            assert_under_root(source, root)
            if forbidden_name(source):
                continue
            destination = stage / relative_base / source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append((relative_base / source.name).as_posix())


def generate_manifest(stage: Path) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name in {MANIFEST_NAME, INFO_NAME}:
            continue
        stat_result = path.stat()
        rows.append(
            {
                "RelativePath": path.relative_to(stage).as_posix(),
                "Length": stat_result.st_size,
                "SHA256": sha256(path),
                "LastWriteUtc": datetime.fromtimestamp(
                    stat_result.st_mtime, tz=timezone.utc
                ).isoformat(),
            }
        )
    return rows


def write_manifest(stage: Path, rows: list[dict[str, str | int]]) -> None:
    manifest_path = stage / MANIFEST_NAME
    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["RelativePath", "Length", "SHA256", "LastWriteUtc"]
        )
        writer.writeheader()
        writer.writerows(rows)


def write_info(stage: Path, root: Path, copied: list[str], count: int) -> None:
    lines = [
        "Axiom Tools - exportação segura para reconciliação V8",
        f"Gerado em: {datetime.now(timezone.utc).isoformat()}",
        f"Raiz lida: {root}",
        f"Staging: {stage}",
        f"Arquivos exportados: {count}",
        "",
        "Candidatos encontrados:",
        *[f"- {item}" for item in sorted(set(copied))],
        "",
        "Proibições aplicadas:",
        "- sem banco SQLite/DB",
        "- sem documentos/uploads",
        "- sem certificados/chaves",
        "- sem .env/tokens/credenciais",
        "- sem logs/backups/temp/cache",
        "- sem .venv/__pycache__",
        "- sem junction/symlink/reparse point nas origens copiadas",
        "- bloqueio se houver possível segredo hardcoded",
        "",
        "Este exportador não altera nem remove arquivos da raiz operacional.",
    ]
    (stage / INFO_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_zip(stage: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(stage).as_posix())


def export_runtime(root: Path, output_dir: Path | None = None, label: str = "runtime-reconciliation-v8") -> ExportResult:
    if not LABEL_RE.fullmatch(label):
        raise ExportError("Label inválido; use apenas letras, números, ponto, sublinhado ou hífen.")

    root = root.resolve()
    if not root.is_dir():
        raise ExportError(f"Raiz operacional inválida: {root}")

    output_dir = (output_dir or (root / "temp")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    stage = output_dir / f"{label}-{timestamp}"
    zip_path = output_dir / f"{label}-{timestamp}.zip"
    if stage.exists() or zip_path.exists():
        raise ExportError(f"Destino de exportação já existe: {stage}")

    stage.mkdir(parents=True)
    copied: list[str] = []

    try:
        for source_rel, destination_rel in CANDIDATES:
            source = root / source_rel
            destination = stage / destination_rel
            if copy_safe(source, destination, root):
                copied.append(source_rel)

        copy_entrypoints(root, stage, copied)
        prune_forbidden(stage)

        forbidden = find_forbidden(stage)
        if forbidden:
            raise ExportError(
                "Conteúdo proibido/sensível permaneceu no export:\n" + "\n".join(forbidden)
            )

        suspicious = find_embedded_secrets(stage)
        if suspicious:
            raise ExportError(
                "Possível segredo hardcoded encontrado; revise:\n" + "\n".join(suspicious)
            )

        runtime_src = stage / "app" / "src"
        fallback_src = stage / "src"
        if not runtime_src.is_dir() and not fallback_src.is_dir():
            raise ExportError("Nenhuma árvore app/src ou src foi encontrada na raiz operacional.")

        rows = generate_manifest(stage)
        write_manifest(stage, rows)
        write_info(stage, root, copied, len(rows))
        create_zip(stage, zip_path)

        return ExportResult(
            stage=stage,
            zip_path=zip_path,
            zip_sha256=sha256(zip_path),
            file_count=len(rows),
        )
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        if zip_path.exists():
            zip_path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta somente código/testes controlados do runtime Axiom Tools para reconciliação."
    )
    parser.add_argument("--root", required=True, type=Path, help="Raiz operacional do Axiom Tools")
    parser.add_argument("--output-dir", type=Path, default=None, help="Diretório de saída")
    parser.add_argument("--label", default="runtime-reconciliation-v8")
    args = parser.parse_args()

    try:
        result = export_runtime(args.root, args.output_dir, args.label)
    except ExportError as exc:
        print(f"EXPORT_V8_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"EXPORT_V8_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("EXPORT_V8_OK")
    print(f"Stage: {result.stage}")
    print(f"ZIP:   {result.zip_path}")
    print(f"SHA256: {result.zip_sha256}")
    print(f"Arquivos: {result.file_count}")
    print("A raiz operacional não foi modificada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
