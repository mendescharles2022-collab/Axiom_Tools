from __future__ import annotations

import sqlite3
import unittest
from unittest.mock import patch

from axiom_tools.modules.closing import service as closing


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,situacao TEXT DEFAULT 'ATIVO')")
    con.execute("CREATE TABLE cliente_parametros(cliente_id INTEGER PRIMARY KEY,movimento_folha TEXT)")
    con.execute("INSERT INTO clientes(id,nome) VALUES(1,'Cliente 1')")
    con.execute("INSERT INTO cliente_parametros(cliente_id,movimento_folha) VALUES(1,'COM_MOVIMENTO')")
    closing.garantir_schema(con)
    closing.salvar_perfil_cliente(con, 1, participa_ciclo=True, chamada_padrao=1, origem='TESTE')
    closing.inicializar_competencia(con, '09/2026')
    return con


class ClosingOptimisticConcurrencyV8Tests(unittest.TestCase):
    def test_schema_has_revision_counter(self):
        con = make_con()
        cols = {r[1] for r in con.execute("PRAGMA table_info(fechamento_mensal_cliente)")}
        self.assertIn('revisao_estado', cols)
        row = con.execute("SELECT revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual(row[0], 0)
        con.close()

    def test_stale_revision_is_rejected_and_newer_state_survives(self):
        con = make_con()
        old = con.execute("SELECT revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()[0]
        con.execute("UPDATE fechamento_mensal_cliente SET status='ADIADA',chamada=2,revisao_estado=revisao_estado+1 WHERE competencia='09/2026' AND cliente_id=1")
        con.commit()
        with self.assertRaises(closing.ConflitoEstadoMensal):
            closing._atualizar_mensal_otimista(con, '09/2026', 1, old, "status='FECHADA'", ())
        row = con.execute("SELECT status,chamada,revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual((row['status'], row['chamada'], row['revisao_estado']), ('ADIADA', 2, 1))
        con.close()

    def test_regular_transition_increments_revision(self):
        con = make_con()
        self.assertEqual(closing.adiar_clientes(con, '09/2026', [1], 'DECISAO_ADMINISTRATIVA'), 1)
        row = con.execute("SELECT status,chamada,revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual(row['status'], 'ADIADA')
        self.assertEqual(row['chamada'], 2)
        self.assertEqual(row['revisao_estado'], 1)
        con.close()

    def test_stale_conference_close_cannot_override_newer_deferral(self):
        con = make_con()

        def concurrent_change(conn, competencia, cliente_id, *, commit=True):
            conn.execute("UPDATE fechamento_mensal_cliente SET status='ADIADA',chamada=2,revisao_estado=revisao_estado+1 WHERE competencia=? AND cliente_id=?", (competencia, cliente_id))
            conn.commit()
            return {'versao': 99, 'natureza': 'TESTE', 'snapshot_hash': 'x'}

        linha = {'cliente_id': 1, 'status_manual': 'CONFERIDO', 'status_automatico': 'CONFERIDO'}
        with patch('axiom_tools.modules.closing.retification.registrar_versao_fechada', side_effect=concurrent_change):
            with self.assertRaises(closing.ConflitoEstadoMensal):
                closing.sincronizar_resultados_conferencia(con, '09/2026', [linha])
        row = con.execute("SELECT status,chamada,revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual((row['status'], row['chamada'], row['revisao_estado']), ('ADIADA', 2, 1))
        con.close()

    def test_stale_next_call_request_is_rejected(self):
        con = make_con()
        con.execute("UPDATE fechamento_mensal SET chamada_atual=2 WHERE competencia='09/2026'")
        con.commit()
        with patch('axiom_tools.modules.closing.service.obter_controle', return_value={'chamada_atual': 1}):
            with self.assertRaises(closing.ConflitoEstadoMensal):
                closing.abrir_proxima_chamada(con, '09/2026')
        self.assertEqual(con.execute("SELECT chamada_atual FROM fechamento_mensal WHERE competencia='09/2026'").fetchone()[0], 2)
        con.close()

    def test_opening_due_call_increments_released_row_revision(self):
        con = make_con()
        closing.adiar_clientes(con, '09/2026', [1], 'DECISAO_ADMINISTRATIVA')
        before = con.execute("SELECT revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()[0]
        self.assertEqual(closing.abrir_proxima_chamada(con, '09/2026'), 2)
        row = con.execute("SELECT status,chamada,revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual((row['status'], row['chamada']), ('PRONTA', 2))
        self.assertEqual(row['revisao_estado'], before + 1)
        con.close()


if __name__ == '__main__':
    unittest.main()
