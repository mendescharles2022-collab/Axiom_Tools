from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.closing import service as closing
from axiom_tools.modules.closing import universe

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,situacao TEXT DEFAULT 'ATIVO')")
    con.execute("CREATE TABLE cliente_parametros(cliente_id INTEGER PRIMARY KEY,movimento_folha TEXT)")
    for cid in range(1, 7):
        con.execute("INSERT INTO clientes(id,nome,situacao) VALUES(?,?, 'ATIVO')", (cid, f'C{cid}'))
        con.execute("INSERT INTO cliente_parametros(cliente_id,movimento_folha) VALUES(?, 'COM_MOVIMENTO')", (cid,))
    closing.garantir_schema(con)
    for cid in range(1, 7):
        closing.salvar_perfil_cliente(con, cid, participa_ciclo=True, chamada_padrao=1, origem='TESTE')
    con.execute("INSERT INTO fechamento_mensal(competencia,chamada_atual,status) VALUES('09/2026',1,'ABERTO')")
    rows = [
        (1, 1, 'PRONTA', 'COM_MOVIMENTO'),
        (2, 1, 'PRONTA', 'SEM_MOVIMENTO'),
        (3, 1, 'FECHADA', 'COM_MOVIMENTO'),
        (4, 1, 'RETIFICACAO', 'SEM_MOVIMENTO'),
        (5, 2, 'ADIADA', 'COM_MOVIMENTO'),
        (6, 1, 'PRONTA', 'COM_MOVIMENTO'),
    ]
    con.executemany("""INSERT INTO fechamento_mensal_cliente
        (competencia,cliente_id,chamada,status,movimento_competencia)
        VALUES('09/2026',?,?,?,?)""", rows)
    closing.salvar_perfil_cliente(con, 6, participa_ciclo=False, chamada_padrao=1, origem='TESTE')
    con.commit()
    return con


class ClosingUniverseV8Tests(unittest.TestCase):
    def test_universes_are_distinct(self):
        con = make_con()
        self.assertEqual(universe.clientes_participantes_ids(con, '09/2026'), {1,2,3,4,5})
        self.assertEqual(universe.clientes_chamada_atual_ids(con, '09/2026'), {1})
        self.assertEqual(universe.clientes_retificacao_ids(con, '09/2026'), {4})
        self.assertEqual(universe.clientes_conferencia_ids(con, '09/2026'), {1,4})
        self.assertEqual(universe.clientes_fechados_ids(con, '09/2026'), {3})
        self.assertEqual(universe.clientes_chamada_futura_ids(con, '09/2026'), {5})
        con.close()

    def test_conference_never_contains_closed_client(self):
        con = make_con()
        self.assertTrue(universe.clientes_conferencia_ids(con, '09/2026').isdisjoint(universe.clientes_fechados_ids(con, '09/2026')))
        con.close()

    def test_sem_movimento_pronta_stays_out_of_normal_current_call(self):
        con = make_con()
        self.assertNotIn(2, universe.clientes_chamada_atual_ids(con, '09/2026'))
        self.assertNotIn(2, universe.clientes_conferencia_ids(con, '09/2026'))
        con.close()

    def test_retification_remains_in_conference_even_sem_movimento(self):
        con = make_con()
        self.assertIn(4, universe.clientes_conferencia_ids(con, '09/2026'))
        con.close()

    def test_service_wrappers_use_canonical_universe(self):
        con = make_con()
        self.assertEqual(closing.clientes_conferencia_ids(con, '09/2026'), {1,4})
        self.assertEqual(closing.clientes_fechados_ids(con, '09/2026'), {3})
        con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_august_snapshot_has_expected_canonical_counts(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / 'axiom_tools.db'
            shutil.copy2(SOURCE_DB, db)
            con = sqlite3.connect(db)
            con.row_factory = sqlite3.Row
            closing.garantir_schema(con)
            self.assertEqual(len(universe.clientes_participantes_ids(con, '08/2026')), 339)
            self.assertEqual(len(universe.clientes_chamada_atual_ids(con, '08/2026')), 30)
            self.assertEqual(len(universe.clientes_retificacao_ids(con, '08/2026')), 7)
            self.assertEqual(len(universe.clientes_conferencia_ids(con, '08/2026')), 37)
            self.assertEqual(len(universe.clientes_fechados_ids(con, '08/2026')), 296)
            self.assertEqual(len(universe.clientes_chamada_futura_ids(con, '08/2026')), 5)
            self.assertTrue(universe.clientes_conferencia_ids(con, '08/2026').isdisjoint(universe.clientes_fechados_ids(con, '08/2026')))
            con.close()


if __name__ == '__main__':
    unittest.main()
