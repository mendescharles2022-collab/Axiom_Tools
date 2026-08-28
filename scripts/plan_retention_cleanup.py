from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SPEC_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class RetentionError(RuntimeError):
    pass


def parse_root_map(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for raw in values:
        if "=" not in raw:
            raise RetentionError(f"root-map inválido: {raw!r}")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not ID_RE.fullmatch(key) or not value:
            raise RetentionError(f"root-map inválido: {raw!r}")
        if key in result:
            raise RetentionError(f"root-map duplicado: {key}")
        root = Path(value).resolve()
        if not root.is_dir():
            raise RetentionError(f"Raiz inexistente: {root}")
        result[key] = root
    if not result:
        raise RetentionError("Ao menos um --root-map é obrigatório.")
    return result


def normalize_policy(policy: dict, roots: dict[str, Path]) -> dict:
    if not isinstance(policy, dict) or policy.get("version") != SPEC_VERSION:
        raise RetentionError(
            f"Política deve ser objeto version={SPEC_VERSION}."
        )
    rules = policy.get("rules")
    if not isinstance(rules, list) or not rules:
        raise RetentionError("Política deve conter rules.")

    seen = set()
    normalized = []
    for idx, item in enumerate(rules, start=1):
        if not isinstance(item, dict):
            raise RetentionError(f"Regra #{idx} inválida.")
        ident = str(item.get("id", "")).strip()
        if not ID_RE.fullmatch(ident):
            raise RetentionError(f"ID inválido: {ident!r}")
        if ident in seen:
            raise RetentionError(f"ID duplicado: {ident}")
        seen.add(ident)

        root_key = str(item.get("root", "")).strip()
        if root_key not in roots:
            raise RetentionError(
                f"Raiz {root_key!r} não fornecida para {ident}."
            )

        pattern = str(item.get("glob", "**/*")).strip()
        if (
            not pattern
            or ".." in Path(pattern).parts
            or Path(pattern).is_absolute()
        ):
            raise RetentionError(f"Glob inseguro em {ident}: {pattern!r}")

        age = item.get("older_than_days")
        if not isinstance(age, (int, float)) or age < 0:
            raise RetentionError(
                f"older_than_days inválido em {ident}."
            )

        extensions = item.get("extensions")
        if extensions is not None:
            if not isinstance(extensions, list) or not all(
                isinstance(value, str) and value.startswith(".")
                for value in extensions
            ):
                raise RetentionError(f"extensions inválido em {ident}.")
            extensions = [value.lower() for value in extensions]

        normalized.append(
            {
                "id": ident,
                "root": root_key,
                "glob": pattern,
                "older_than_days": float(age),
                "extensions": extensions,
            }
        )
    return {"version": SPEC_VERSION, "rules": normalized}


def plan_cleanup(
    roots: dict[str, Path],
    policy: dict,
    now_ts: float | None = None,
) -> dict:
    normalized = normalize_policy(policy, roots)
    now = (
        now_ts
        if now_ts is not None
        else datetime.now(timezone.utc).timestamp()
    )
    results = []
    total_candidates = 0
    total_bytes = 0
    seen_paths = set()

    for rule in normalized["rules"]:
        root = roots[rule["root"]].resolve()
        items = []
        matched = 0

        for path in sorted(root.rglob("*")):
            if not path.is_file() and not path.is_symlink():
                continue
            rel = path.relative_to(root).as_posix()
            pattern = rule["glob"]
            matched_pattern = (
                pattern == "**/*"
                or fnmatch.fnmatch(rel, pattern)
                or fnmatch.fnmatch(path.name, pattern)
            )
            if not matched_pattern:
                continue
            if (
                rule["extensions"]
                and path.suffix.lower() not in rule["extensions"]
            ):
                continue

            key = (rule["root"], rel)
            if key in seen_paths:
                continue
            seen_paths.add(key)
            matched += 1

            if path.is_symlink():
                items.append(
                    {
                        "path": rel,
                        "status": "REVIEW_SYMLINK",
                        "age_days": None,
                        "size": 0,
                    }
                )
                continue

            try:
                resolved = path.resolve()
                resolved.relative_to(root)
            except ValueError:
                items.append(
                    {
                        "path": rel,
                        "status": "REVIEW_OUTSIDE_ROOT",
                        "age_days": None,
                        "size": 0,
                    }
                )
                continue

            stat = path.stat()
            age_days = max(0.0, (now - stat.st_mtime) / 86400.0)
            if age_days > rule["older_than_days"]:
                status = "CANDIDATE"
                total_candidates += 1
                total_bytes += stat.st_size
            else:
                status = "KEEP_RECENT"

            items.append(
                {
                    "path": rel,
                    "status": status,
                    "age_days": round(age_days, 3),
                    "size": stat.st_size,
                }
            )

        results.append(
            {
                "id": rule["id"],
                "root": rule["root"],
                "matched": matched,
                "items": items,
            }
        )

    return {
        "mode": "DRY_RUN_ONLY",
        "summary": {
            "rules": len(results),
            "candidate_files": total_candidates,
            "candidate_bytes": total_bytes,
        },
        "rules": results,
        "warning": (
            "Este relatório não autoriza exclusão. Evidência/versionamento/"
            "acervo probatório devem ser validados antes de qualquer limpeza real."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Planeja limpeza por retenção do Axiom Tools sem apagar ou mover arquivos."
        )
    )
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument(
        "--output", type=Path, default=Path("RETENTION_DRY_RUN.json")
    )
    args = parser.parse_args()

    try:
        roots = parse_root_map(args.root_map)
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = plan_cleanup(roots, policy)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except (
        RetentionError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"RETENTION_PLAN_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RETENTION_PLAN_OK")
    print("Modo: DRY_RUN_ONLY")
    print(f"Candidatos: {report['summary']['candidate_files']}")
    print(f"Bytes: {report['summary']['candidate_bytes']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
