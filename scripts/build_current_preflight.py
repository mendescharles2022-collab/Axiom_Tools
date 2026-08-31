from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import create_regression_results_skeleton as skeleton
import validate_blocker_statuses as blockers
import validate_regression_case_blocker_map as dependency_map
import validate_regression_results as regression
import validate_release_gate as release_gate


class CurrentPreflightError(RuntimeError):
    pass


def build_current_preflight(repo_root: Path, output_dir: Path) -> dict:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()

    if not repo_root.is_dir():
        raise CurrentPreflightError(f"repo-root inválido: {repo_root}")
    if output_dir.exists():
        raise CurrentPreflightError(
            f"Diretório de saída já existe e não será sobrescrito: {output_dir}"
        )

    required = {
        "blocker_registry": repo_root / "config" / "blocker_registry_v8.json",
        "blocker_status": repo_root / "config" / "blocker_status_v8_current.json",
        "regression_registry": repo_root / "config" / "regression_cases_v8_202608.json",
        "regression_blocker_map": repo_root / "config" / "regression_case_blocker_map_v8_202608.json",
        "release_identity": repo_root / "config" / "release_identity.toml",
        "evidence_manifest": repo_root / "config" / "release_gate_evidence_v8_current.json",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise CurrentPreflightError(
            "Arquivos canônicos ausentes: " + ", ".join(missing)
        )

    stage = output_dir.with_name(output_dir.name + ".partial")
    if stage.exists():
        raise CurrentPreflightError(f"Stage já existe: {stage}")

    try:
        stage.mkdir(parents=True)

        blocker_registry_doc = dependency_map.load_json(required["blocker_registry"])
        regression_doc = regression.load_json(required["regression_registry"])
        causal_report = dependency_map.validate_dependency_map(
            regression_doc,
            blocker_registry_doc,
            dependency_map.load_json(required["regression_blocker_map"]),
        )

        regression_results = skeleton.build_skeleton(regression_doc)
        regression_path = stage / "REGRESSION_RESULTS_CURRENT.json"
        regression_path.write_text(
            json.dumps(regression_results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        report = release_gate.evaluate_release_gate(
            blocker_registry_path=required["blocker_registry"],
            blocker_status_path=required["blocker_status"],
            regression_registry_path=required["regression_registry"],
            regression_results_path=regression_path,
            release_identity_path=required["release_identity"],
            evidence_manifest_path=required["evidence_manifest"],
            final_mode=False,
        )

        report_path = stage / "V8_RELEASE_GATE_PREFLIGHT.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        summary = {
            "audit": "V8",
            "final_ok": report["final_ok"],
            "blockers_homologated": report["blockers"]["homologated"],
            "regression_pass": report["regression"]["status_counts"].get("PASS", 0),
            "release_ready": report["release_ready"],
            "evidence_pass": report["evidence"]["pass_count"],
            "evidence_required": report["evidence"]["required"],
            "build_ok": report["build_ok"],
            "causal_map_ok": causal_report["ok"],
            "causal_cases_mapped": causal_report["mapped_cases"],
            "causal_known_blockers": causal_report["known_blockers"],
            "causal_used_blockers": len(causal_report["used_blockers"]),
            "errors": report["errors"],
        }
        (stage / "PREFLIGHT_SUMMARY.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        stage.rename(output_dir)
        return summary
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera o preflight atual V8 sem alterar registries nem runtime."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    try:
        summary = build_current_preflight(args.repo_root, args.output_dir)
    except (
        CurrentPreflightError,
        blockers.BlockerValidationError,
        dependency_map.DependencyMapError,
        regression.RegressionValidationError,
        release_gate.ReleaseGateError,
    ) as exc:
        print(f"V8_PREFLIGHT_ERRO: {exc}", file=sys.stderr)
        return 2

    print("V8_PREFLIGHT_OK")
    print(f"Final OK: {summary['final_ok']}")
    print(f"Bloqueadores homologados: {summary['blockers_homologated']}/50")
    print(f"Casos PASS: {summary['regression_pass']}/28")
    print(f"Mapa causal: {summary['causal_cases_mapped']}/28")
    print(f"Evidências PASS: {summary['evidence_pass']}/{summary['evidence_required']}")
    print(f"Release READY: {summary['release_ready']}")
    print(f"Build OK: {summary['build_ok']}")
    print(f"Saída: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
