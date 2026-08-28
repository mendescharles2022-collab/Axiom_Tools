from __future__ import annotations

import sqlite3
import unittest

from axiom_tools.modules.closing.performance import garantir_indices_escala


def make_con(*, rows: int = 0) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.executescript(
        """
        CREATE TABLE fechamento_mensal(competencia TEXT PRIMARY KEY,chamada_atual INTEGER);
        CREATE TABLE fechamento_cliente_perfil(cliente_id INTEGER PRIMARY KEY,participa_ciclo INTEGER);
        CREATE TABLE fechamento_mensal_cliente(
            competencia TEXT NOT NULL, cliente_id INTEGER NOT NULL, status TEXT NOT NULL,
            chamada INTEGER NOT NULL, movimento_competencia TEXT NOT NULL
        );
        CREATE TABLE processamento_arquivo(
            id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL, competencia TEXT NOT NULL,
            documento_tipo TEXT, documento_vigente INTEGER DEFAULT 1, status TEXT
        );
        CREATE TABLE fechamento_mensal_retificacao(
            id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL, competencia TEXT NOT NULL, status TEXT
        );
        """
    )
    if rows:
        con.execute("INSERT INTO fechamento_mensal VALUES('08/2026',1)")
        con.executemany(
            "INSERT INTO fechamento_cliente_perfil VALUES(?,1)",
            [(i,) for i in range(1, rows + 1)],
        )
        fmc = []
        docs = []
        for i in range(1, rows + 1):
            status = "PRONTA" if i % 3 else "FECHADA"
            movimento = "COM_MOVIMENTO" if i % 10 else "SEM_MOVIMENTO"
            fmc.append(("08/2026", i, status, 1, movimento))
            docs.extend(
                [
                    (i * 3 - 2, i, "08/2026", "EXTRATO_MENSAL", 1, "PROCESSADO"),
                    (i * 3 - 1, i, "08/2026", "DARF", 1, "PROCESSADO"),
                    (i * 3, i, "08/2026", "GUIA_FGTS_DIGITAL", 1, "PROCESSADO"),
                ]
            )
        con.executemany("INSERT INTO fechamento_mensal_cliente VALUES(?,?,?,?,?)", fmc)
        con.executemany("INSERT INTO processamento_arquivo VALUES(?,?,?,?,?,?)", docs)
    con.commit()
    return con


def plan_text(con: sqlite3.Connection, sql: str, params=()) -> str:
    return "\n".join(str(row[3]) for row in con.execute("EXPLAIN QUERY PLAN " + sql, params))


class ScaleIndexesV8Tests(unittest.TestCase):
    def test_expected_scale_indexes_are_created(self):
        con = make_con()
        result = garantir_indices_escala(con)
        self.assertEqual(len(result["created"]), 4)
        self.assertEqual(result["skipped"], [])
        con.close()

    def test_creation_is_idempotent(self):
        con = make_con()
        garantir_indices_escala(con)
        second = garantir_indices_escala(con)
        self.assertEqual(second["created"], [])
        self.assertEqual(second["skipped"], [])
        con.close()

    def test_partial_schema_creates_only_compatible_index(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE fechamento_mensal_cliente(competencia TEXT, cliente_id INTEGER)")
        result = garantir_indices_escala(con)
        self.assertEqual(result["created"], ["idx_v8_fechamento_cliente_comp"])
        self.assertEqual(len(result["skipped"]), 3)
        con.close()

    def test_current_call_query_uses_compound_index_above_600_clients(self):
        con = make_con(rows=1000)
        garantir_indices_escala(con)
        sql = """
            SELECT f.cliente_id
              FROM fechamento_mensal_cliente f
              JOIN fechamento_mensal fm ON fm.competencia=f.competencia
              LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
             WHERE f.competencia=?
               AND f.status='PRONTA'
               AND f.chamada=fm.chamada_atual
               AND f.movimento_competencia='COM_MOVIMENTO'
               AND (NOT EXISTS (SELECT 1 FROM fechamento_cliente_perfil)
                    OR COALESCE(fp.participa_ciclo,0)=1)
        """
        plan = plan_text(con, sql, ("08/2026",))
        lines = [line.strip() for line in plan.splitlines()]
        self.assertIn("idx_v8_fechamento_comp_status_chamada_mov", plan)
        self.assertTrue(any(line.startswith("SEARCH f USING") for line in lines))
        self.assertFalse(any(line == "SCAN f" or line.startswith("SCAN f ") for line in lines))
        con.close()

    def test_document_lookup_uses_client_competence_type_index_at_scale(self):
        con = make_con(rows=1000)
        garantir_indices_escala(con)
        sql = """
            SELECT id FROM processamento_arquivo
             WHERE cliente_id=? AND competencia=? AND documento_tipo=?
               AND documento_vigente=1 AND status='PROCESSADO'
        """
        plan = plan_text(con, sql, (777, "08/2026", "DARF"))
        self.assertIn("idx_v8_processamento_cliente_comp_tipo_vigente", plan)
        self.assertNotIn("SCAN processamento_arquivo", plan)
        con.close()


if __name__ == "__main__":
    unittest.main()
