from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import validate_regression_results as regression


class RegressionSkeletonError(RuntimeError):
    pass


def build_skeleton(registry: dict) -> dict:
    try:
        metadata = regression.validate_registry(registry)
    except regression.RegressionValidationError as exc:
        raise RegressionSkeletonError(str(exc)) from exc

    return {
        "version": 1,
        "audit": "V8",
        "registry_sha256": metadata["hash"],
        "results": [
            {
                "case_id": case_id,
                "status": "NOT_RUN",
                "evidence": [],
                "notes": "Aguardando execução no runtime reconciliado.",
            }
            for case_id in metadata["ids"]
        ],
    }


def write_skeleton(path: Path, document: dict, *, force: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not force:
        raise RegressionSkeletonError(
            f"Destino já existe e não será sobrescrito: {path}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera resultados NOT_RUN para C01–C28 com hash do registry canônico."
    )
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        document = build_skeleton(regression.load_json(args.registry))
        write_skeleton(args.output, document, force=args.force)
        report = regression.validate_results(
            regression.load_json(args.registry),
            document,
            final_mode=False,
        )
    except (RegressionSkeletonError, regression.RegressionValidationError) as exc:
        print(f"REGRESSION_SKELETON_ERRO: {exc}", file=sys.stderr)
        return 2

    print("REGRESSION_SKELETON_OK")
    print(f"Casos: {report['submitted']}/28")
    print(f"PASS: {report['status_counts']['PASS']}")
    print(f"Final OK: {report['final_ok']}")
    print(f"Arquivo: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
