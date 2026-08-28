from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_sqlite_queries.py"
spec = importlib.util.spec_from_file_location("benchmark_sqlite_queries", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def make_db(path: Path, rows: int = 100) -> None:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY,v TEXT)")
    conn.executemany(
        "INSERT INTO t(v) VALUES(?)",
        [(str(index),) for index in range(rows)],
    )
    conn.commit()
    conn.close()


def benchmark_spec(
    sql: str = "SELECT * FROM t WHERE id<=10",
    **overrides,
) -> dict:
    scenario = {
        "id": "q",
        "sql": sql,
        "repeat": 3,
        "warmup": 1,
    }
    scenario.update(overrides)
    return {"version": 1, "scenarios": [scenario]}


class BenchmarkSqliteTests(unittest.TestCase):
    def test_valid_query_benchmarks(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "d.sqlite"
            make_db(database)
            report = module.benchmark(database, benchmark_spec())
            self.assertTrue(report["ok"])
            self.assertEqual(len(report["results"][0]["timings_ms"]), 3)

    def test_plan_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "d.sqlite"
            make_db(database)
            report = module.benchmark(database, benchmark_spec())
            self.assertTrue(report["results"][0]["query_plan"])

    def test_threshold_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "d.sqlite"
            make_db(database)
            report = module.benchmark(
                database,
                benchmark_spec(max_p95_ms=0.000001),
            )
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["threshold_failures"], 1)

    def test_no_threshold_is_not_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "d.sqlite"
            make_db(database)
            report = module.benchmark(database, benchmark_spec())
            self.assertIsNone(report["results"][0]["threshold_ok"])

    def test_write_query_is_blocked_and_db_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "d.sqlite"
            make_db(database)
            before = database.read_bytes()
            report = module.benchmark(
                database,
                benchmark_spec("UPDATE t SET v='x' RETURNING id"),
            )
            self.assertEqual(report["summary"]["query_errors"], 1)
            self.assertEqual(before, database.read_bytes())

    def test_invalid_repeat_rejected(self):
        with self.assertRaises(module.BenchmarkError):
            module.normalize_spec(benchmark_spec(repeat=0))

    def test_percentile_monotonic(self):
        values = [1, 2, 3, 4, 5]
        self.assertLessEqual(
            module.percentile(values, 0.5),
            module.percentile(values, 0.95),
        )
        self.assertLessEqual(
            module.percentile(values, 0.95),
            module.percentile(values, 0.99),
        )


if __name__ == "__main__":
    unittest.main()
