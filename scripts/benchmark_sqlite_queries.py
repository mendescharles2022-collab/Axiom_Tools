from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import statistics
import sys
import time
from pathlib import Path
from urllib.parse import quote

SPEC_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class BenchmarkError(RuntimeError):
    pass


def connect_ro(path: Path) -> sqlite3.Connection:
    db = path.resolve()
    if not db.is_file():
        raise BenchmarkError(f"Banco inexistente: {db}")
    uri = "file:" + quote(db.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def authorizer(action, arg1, arg2, dbname, source):
    denied = {
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_ANALYZE,
    }
    if action in denied or action == sqlite3.SQLITE_PRAGMA:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise BenchmarkError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    scenarios = spec.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise BenchmarkError("Spec deve conter scenarios.")

    seen = set()
    normalized = []
    for idx, item in enumerate(scenarios, start=1):
        if not isinstance(item, dict):
            raise BenchmarkError(f"Cenário #{idx} inválido.")
        ident = str(item.get("id", "")).strip()
        if not ID_RE.fullmatch(ident):
            raise BenchmarkError(f"ID inválido: {ident!r}")
        if ident in seen:
            raise BenchmarkError(f"ID duplicado: {ident}")
        seen.add(ident)
        sql = str(item.get("sql", "")).strip()
        if not sql:
            raise BenchmarkError(f"SQL ausente em {ident}.")
        repeat = item.get("repeat", 5)
        warmup = item.get("warmup", 1)
        if not isinstance(repeat, int) or not (1 <= repeat <= 100):
            raise BenchmarkError(f"repeat inválido em {ident}.")
        if not isinstance(warmup, int) or not (0 <= warmup <= 20):
            raise BenchmarkError(f"warmup inválido em {ident}.")
        max_p95 = item.get("max_p95_ms")
        if max_p95 is not None and (
            not isinstance(max_p95, (int, float)) or max_p95 <= 0
        ):
            raise BenchmarkError(f"max_p95_ms inválido em {ident}.")
        normalized.append(
            {
                "id": ident,
                "sql": sql,
                "repeat": repeat,
                "warmup": warmup,
                "max_p95_ms": max_p95,
            }
        )
    return {"version": SPEC_VERSION, "scenarios": normalized}


def execute_once(conn: sqlite3.Connection, sql: str) -> tuple[float, int]:
    start = time.perf_counter()
    rows = conn.execute(sql).fetchall()
    elapsed = (time.perf_counter() - start) * 1000.0
    return elapsed, len(rows)


def benchmark(db: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    conn = connect_ro(db)
    conn.set_authorizer(authorizer)
    results = []
    try:
        for scenario in normalized["scenarios"]:
            error = None
            plan = []
            timings = []
            row_counts = []
            try:
                plan = [
                    list(row)
                    for row in conn.execute(
                        "EXPLAIN QUERY PLAN " + scenario["sql"]
                    )
                ]
                for _ in range(scenario["warmup"]):
                    execute_once(conn, scenario["sql"])
                for _ in range(scenario["repeat"]):
                    elapsed, rows = execute_once(conn, scenario["sql"])
                    timings.append(elapsed)
                    row_counts.append(rows)
            except sqlite3.Error as exc:
                error = str(exc)

            if timings:
                p50 = percentile(timings, 0.50)
                p95 = percentile(timings, 0.95)
                p99 = percentile(timings, 0.99)
                average = statistics.fmean(timings)
            else:
                p50 = p95 = p99 = average = 0.0

            threshold = scenario["max_p95_ms"]
            threshold_ok = (
                None
                if threshold is None or error
                else p95 <= float(threshold)
            )
            results.append(
                {
                    "id": scenario["id"],
                    "repeat": scenario["repeat"],
                    "warmup": scenario["warmup"],
                    "timings_ms": [round(value, 3) for value in timings],
                    "avg_ms": round(average, 3),
                    "p50_ms": round(p50, 3),
                    "p95_ms": round(p95, 3),
                    "p99_ms": round(p99, 3),
                    "row_counts": row_counts,
                    "query_plan": plan,
                    "max_p95_ms": threshold,
                    "threshold_ok": threshold_ok,
                    "error": error,
                }
            )
    finally:
        conn.close()

    query_errors = sum(1 for result in results if result["error"])
    threshold_failures = sum(
        1 for result in results if result["threshold_ok"] is False
    )
    return {
        "database_name": db.name,
        "summary": {
            "scenarios": len(results),
            "query_errors": query_errors,
            "threshold_failures": threshold_failures,
        },
        "ok": query_errors == 0 and threshold_failures == 0,
        "results": results,
        "note": (
            "Benchmark de query não substitui benchmark HTTP/UX, concorrência, "
            "workers ou teste Windows."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark somente leitura de consultas SQLite do Axiom Tools."
    )
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("SQLITE_BENCHMARK.json")
    )
    args = parser.parse_args()

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        report = benchmark(args.db, spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except (
        BenchmarkError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"SQLITE_BENCHMARK_ERRO: {exc}", file=sys.stderr)
        return 2

    print("SQLITE_BENCHMARK_OK" if report["ok"] else "SQLITE_BENCHMARK_FALHA")
    print(f"Cenários: {report['summary']['scenarios']}")
    print(f"Erros: {report['summary']['query_errors']}")
    print(f"Thresholds falhos: {report['summary']['threshold_failures']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
