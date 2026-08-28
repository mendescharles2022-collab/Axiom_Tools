from __future__ import annotations

import json
import sqlite3
import unittest
from unittest.mock import patch

from axiom_tools.modules.closing import retification
from axiom_tools.modules.closing import service as closing


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,situacao TEXT DEFAULT 'ATIVO')")
    con.execute("CREATE TABLE cliente_parametros(cliente_id INTEGER PRIMARY KEY,movimento_folha TEXT)")
    con.execute("INSERT INTO clientes(id,nome) VALUES(1,'Cliente')")
    con.execute("INSERT INTO cliente_parametros(cliente_id,movimento_folha) VALUES(1,'COM_MOVIMENTO')")
    closing.garantir_schema(con)
    closing.salvar_perfil_cliente(con, 1, participa_ciclo=True, chamada_padrao=1, origem='TESTE')
    closing.inicializar_competencia(con, '09/2026')
    con.execute("UPDATE fechamento_mensal_cliente SET status='FECHADA',versao_atual=1 WHERE competencia='09/2026' AND cliente_id=1")
    con.commit()
    return con


def insert_version(con, versao: int, snap: dict) -> None:
    con.execute("""INSERT INTO fechamento_mensal_versao
        (competencia,cliente_id,versao,natureza,snapshot_hash,snapshot_json)
        VALUES('09/2026',1,?,?,?,?)""",
        (versao, 'ORIGINAL' if versao == 1 else 'RETIFICACAO', retification.snapshot_hash(snap), json.dumps(snap)))
    con.commit()


class RetificationCurrentVersionV8Tests(unittest.TestCase):
    def test_uses_current_pointer_not_highest_orphan_version(self):
        con = make_con()
        current = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 100.0}}
        orphan = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 999.0}}
        insert_version(con, 1, current)
        insert_version(con, 2, orphan)
        with patch.object(retification, 'snapshot_cliente_competencia', return_value=current):
            result = retification.avaliar_cliente(con, '09/2026', 1)
        self.assertTrue(result['avaliado'])
        self.assertFalse(result['mudou'])
        self.assertFalse(result['bloquear_saida'])
        self.assertEqual(result['versao_base'], 1)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM fechamento_mensal_retificacao").fetchone()[0], 0)
        con.close()

    def test_missing_current_pointer_target_blocks_safely(self):
        con = make_con()
        con.execute("UPDATE fechamento_mensal_cliente SET versao_atual=9 WHERE competencia='09/2026' AND cliente_id=1")
        con.commit()
        with patch.object(retification, 'snapshot_cliente_competencia', return_value={}):
            result = retification.avaliar_cliente(con, '09/2026', 1)
        self.assertFalse(result['avaliado'])
        self.assertTrue(result['bloquear_saida'])
        self.assertEqual(result['motivo'], 'SEM_SNAPSHOT_BASE')
        con.close()

    def test_material_change_uses_current_version_as_retification_base(self):
        con = make_con()
        base = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 100.0}}
        current = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 120.0}}
        insert_version(con, 1, base)
        with patch.object(retification, 'snapshot_cliente_competencia', return_value=current):
            result = retification.avaliar_cliente(con, '09/2026', 1, 77)
        self.assertTrue(result['mudou'])
        row = con.execute("SELECT base_versao,status,gatilho_processamento_id FROM fechamento_mensal_retificacao").fetchone()
        self.assertEqual((row['base_versao'], row['status'], row['gatilho_processamento_id']), (1, 'DETECTADA', 77))
        mensal = con.execute("SELECT status,revisao_estado FROM fechamento_mensal_cliente WHERE competencia='09/2026' AND cliente_id=1").fetchone()
        self.assertEqual(mensal['status'], 'RETIFICACAO')
        self.assertEqual(mensal['revisao_estado'], 1)
        con.close()

    def test_repeated_material_evaluation_keeps_single_detected_row(self):
        con = make_con()
        base = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 100.0}}
        current = {'competencia': '09/2026', 'cliente_id': 1, 'folha': {'proventos': 120.0}}
        insert_version(con, 1, base)
        with patch.object(retification, 'snapshot_cliente_competencia', return_value=current):
            first = retification.avaliar_cliente(con, '09/2026', 1, 77)
            second = retification.avaliar_cliente(con, '09/2026', 1, 78)
        self.assertTrue(first['mudou'])
        self.assertTrue(second['mudou'])
        self.assertEqual(con.execute("SELECT COUNT(*) FROM fechamento_mensal_retificacao WHERE status='DETECTADA'").fetchone()[0], 1)
        self.assertEqual(con.execute("SELECT gatilho_processamento_id FROM fechamento_mensal_retificacao WHERE status='DETECTADA'").fetchone()[0], 78)
        con.close()


if __name__ == '__main__':
    unittest.main()
