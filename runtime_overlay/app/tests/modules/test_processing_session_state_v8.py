from __future__ import annotations

import sqlite3
from pathlib import Path
import unittest

from axiom_tools.modules.processing import queue
from axiom_tools.modules.processing.central import _finalizar_chave


class ProcessingSessionStateV8Tests(unittest.TestCase):
    def test_revision_does_not_turn_completed_session_into_pending(self):
        status = queue._status_tecnico_sessao(
            percentual=100.0,
            counts={"REVISAO": 2},
            docs={"revisao": 2, "erros": 0},
            persistido="CONCLUIDO",
        )
        self.assertEqual(status, "PROCESSAMENTO_CONCLUIDO")

    def test_real_technical_error_has_distinct_completed_state(self):
        status = queue._status_tecnico_sessao(
            percentual=100.0,
            counts={"ERRO": 1},
            docs={"revisao": 3, "erros": 1},
            persistido="COM_ERROS",
        )
        self.assertEqual(status, "PROCESSAMENTO_CONCLUIDO_COM_FALHAS_TECNICAS")

    def test_cancelled_session_is_not_called_successful(self):
        status = queue._status_tecnico_sessao(
            percentual=100.0,
            counts={"CANCELADO": 1},
            docs={"revisao": 0, "erros": 0},
            persistido="CANCELADO",
        )
        self.assertEqual(status, "CANCELADO")

    def test_revision_during_execution_does_not_override_runtime_state(self):
        status = queue._status_tecnico_sessao(
            percentual=50.0,
            counts={"PROCESSADO": 1, "AGUARDANDO": 1},
            docs={"revisao": 1, "erros": 0},
            persistido="EM_EXECUCAO",
        )
        self.assertEqual(status, "EM_EXECUCAO")

    def test_legacy_pending_session_is_migrated_to_completed(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute("""CREATE TABLE processamento_chave(
            id INTEGER PRIMARY KEY, codigo TEXT UNIQUE, origem TEXT, recebidos INTEGER DEFAULT 0,
            status TEXT, concluido_em TEXT, processados INTEGER DEFAULT 0, revisao INTEGER DEFAULT 0,
            erros INTEGER DEFAULT 0, duplicados INTEGER DEFAULT 0
        )""")
        con.execute("INSERT INTO processamento_chave(id,codigo,status) VALUES(1,'PROC-X','COM_PENDENCIAS')")
        queue.garantir_schema(con)
        con.execute("INSERT INTO processamento_sessao(chave_id,origem,status,total_arquivos) VALUES(1,'TESTE','COM_PENDENCIAS',1)")
        con.commit()
        queue.garantir_schema(con)
        self.assertEqual(con.execute("SELECT status FROM processamento_chave WHERE id=1").fetchone()[0], "CONCLUIDO")
        self.assertEqual(con.execute("SELECT status FROM processamento_sessao WHERE chave_id=1").fetchone()[0], "CONCLUIDO")
        con.close()

    def test_queue_does_not_promote_revision_count_to_pending_session(self):
        text = Path('src/axiom_tools/modules/processing/queue.py').read_text(encoding='utf-8')
        self.assertNotIn('elif docs.get("revisao",0): status="COM_PENDENCIAS"', text)

    def test_processing_keys_no_longer_styles_legacy_pending_as_live_state(self):
        text = Path('src/axiom_tools/web/templates/documents/processing_keys.html').read_text(encoding='utf-8')
        self.assertNotIn("k.status=='COM_PENDENCIAS'", text)

    def test_key_finalization_keeps_revision_count_but_not_pending_status(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute("""CREATE TABLE processamento_chave(
            id INTEGER PRIMARY KEY, codigo TEXT UNIQUE, origem TEXT, recebidos INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ABERTA', concluido_em TEXT, processados INTEGER DEFAULT 0,
            revisao INTEGER DEFAULT 0, erros INTEGER DEFAULT 0, duplicados INTEGER DEFAULT 0
        )""")
        con.execute("INSERT INTO processamento_chave(id,codigo) VALUES(1,'PROC-X')")
        con.commit()
        _finalizar_chave(con, 1, {"processados": 3, "revisao": 2, "erros": 0, "duplicados": 0})
        row = con.execute("SELECT status,processados,revisao,erros FROM processamento_chave WHERE id=1").fetchone()
        self.assertEqual(row["status"], "CONCLUIDO")
        self.assertEqual(row["processados"], 3)
        self.assertEqual(row["revisao"], 2)
        self.assertEqual(row["erros"], 0)
        con.close()


if __name__ == "__main__":
    unittest.main()
