from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


class EvidenceIndexError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_index(root: Path, files: list[str]) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise EvidenceIndexError(f"root inválida: {root}")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in files:
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts:
            raise EvidenceIndexError(f"Caminho inseguro: {raw}")
        key = rel.as_posix()
        if key in seen:
            raise EvidenceIndexError(f"Caminho duplicado: {key}")
        seen.add(key)
        normalized.append(key)

    entries: list[dict[str, object]] = []
    for rel in sorted(normalized):
        path = (root / rel).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise EvidenceIndexError(f"Caminho fora da raiz: {rel}") from exc
        if path.is_symlink():
            raise EvidenceIndexError(f"Symlink não permitido: {rel}")
        if not path.is_file():
            raise EvidenceIndexError(f"Evidência ausente: {rel}")
        entries.append(
            {
                "path": rel,
                "length": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    if not entries:
        raise EvidenceIndexError("Nenhuma evidência informada.")

    payload = {
        "version": 1,
        "audit": "V8",
        "files": entries,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload["index_sha256"] = hashlib.sha256(canonical).hexdigest().upper()
    return payload


def verify_index(root: Path, document: dict) -> dict:
    if document.get("version") != 1 or document.get("audit") != "V8":
        raise EvidenceIndexError("Índice deve ser version=1 audit=V8.")
    files = document.get("files")
    if not isinstance(files, list) or not files:
        raise EvidenceIndexError("Índice sem files.")

    base = {"version": 1, "audit": "V8", "files": files}
    canonical = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    expected_index = hashlib.sha256(canonical).hexdigest().upper()
    if document.get("index_sha256") != expected_index:
        raise EvidenceIndexError("Hash do índice divergente.")

    rebuilt = build_index(root, [str(item.get("path", "")) for item in files])
    if rebuilt["files"] != files:
        raise EvidenceIndexError("Conteúdo das evidências divergiu do índice.")
    return {"ok": True, "file_count": len(files), "index_sha256": expected_index}


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria ou verifica índice SHA-256 de evidências da V8.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    try:
        if args.verify:
            document = json.loads(args.verify.read_text(encoding="utf-8"))
            report = verify_index(args.root, document)
            print("EVIDENCE_INDEX_VERIFY_OK")
            print(f"Arquivos: {report['file_count']}")
            print(f"Hash: {report['index_sha256']}")
            return 0
        if not args.output:
            raise EvidenceIndexError("--output é obrigatório ao criar índice.")
        if args.output.exists():
            raise EvidenceIndexError(f"Destino já existe: {args.output}")
        document = build_index(args.root, args.file)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (EvidenceIndexError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"EVIDENCE_INDEX_ERRO: {exc}", file=sys.stderr)
        return 2

    print("EVIDENCE_INDEX_OK")
    print(f"Arquivos: {len(document['files'])}")
    print(f"Hash: {document['index_sha256']}")
    print(f"Arquivo: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
