from __future__ import annotations

import sqlite3
import unittest

from axiom_tools.modules.processing.output_gate import (
    AUTORIZADO,
    CLIENTE_NAO_FECHADO,
    DOCUMENTO_FORA_DO_ESCOPO,
    FECHAMENTO_AUSENTE,
    RETIFICACAO_PENDENTE,
    VERSAO_FECHAMENTO_INVALIDA,
    autorizar_saida_cliente,
    filtrar_documentos_autorizados,
)


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE fechamento_mensal_cliente(
            competencia TEXT NOT NULL,
            cliente_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            versao_atual INTEGER
        );
        CREATE TABLE fechamento_mensal_versao(
            competencia TEXT NOT NULL,
            cliente_id INTEGER NOT NULL,
            versao INTEGER NOT NULL
        );
        CREATE TABLE fechamento_mensal_retificacao(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competencia TEXT NOT NULL,
            cliente_id INTEGER NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE processamento_arquivo(
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            competencia TEXT NOT NULL,
            status TEXT,
            documento_vigente INTEGER DEFAULT 1
        );
        """
    )
    return con


def fechar(con: sqlite3.Connection, cliente_id: int = 1, competencia: str = "08/2026", versao: int = 1):
    con.execute(
        "INSERT INTO fechamento_mensal_cliente VALUES(?,?, 'FECHADA', ?)",
        (competencia, cliente_id, versao),
    )
    con.execute(
        "INSERT INTO fechamento_mensal_versao VALUES(?,?,?)",
        (competencia, cliente_id, versao),
    )
    con.commit()


class OutputGateV8Tests(unittest.TestCase):
    def test_missing_closing_blocks_output(self):
        con = make_con()
        r = autorizar_saida_cliente(con, cliente_id=1, competencia="08/2026")
        self.assertFalse(r["autorizado"])
        self.assertEqual(r["motivo"], FECHAMENTO_AUSENTE)
        con.close()

    def test_processed_document_does_not_authorize_pronta_client(self):
        con = make_con()
        con.execute("INSERT INTO fechamento_mensal_cliente VALUES('08/2026',1,'PRONTA',NULL)")
        con.execute("INSERT INTO processamento_arquivo VALUES(10,1,'08/2026','PROCESSADO',1)")
        con.commit()
        r = filtrar_documentos_autorizados(
            con, cliente_id=1, competencia="08/2026", documento_ids=[10]
        )
        self.assertFalse(r["autorizado"])
        self.assertEqual(r["motivo"], CLIENTE_NAO_FECHADO)
        self.assertEqual(r["documentos_autorizados"], [])
        con.close()

    def test_closed_client_with_current_version_is_authorized(self):
        con = make_con(); fechar(con)
        r = autorizar_saida_cliente(con, cliente_id=1, competencia="08/2026")
        self.assertTrue(r["autorizado"])
        self.assertEqual(r["motivo"], AUTORIZADO)
        self.assertEqual(r["versao_atual"], 1)
        con.close()

    def test_closed_without_current_version_is_blocked(self):
        con = make_con()
        con.execute("INSERT INTO fechamento_mensal_cliente VALUES('08/2026',1,'FECHADA',NULL)")
        con.commit()
        r = autorizar_saida_cliente(con, cliente_id=1, competencia="08/2026")
        self.assertEqual(r["motivo"], VERSAO_FECHAMENTO_INVALIDA)
        con.close()

    def test_closed_pointing_to_missing_version_is_blocked(self):
        con = make_con()
        con.execute("INSERT INTO fechamento_mensal_cliente VALUES('08/2026',1,'FECHADA',2)")
        con.execute("INSERT INTO fechamento_mensal_versao VALUES('08/2026',1,1)")
        con.commit()
        r = autorizar_saida_cliente(con, cliente_id=1, competencia="08/2026")
        self.assertEqual(r["motivo"], VERSAO_FECHAMENTO_INVALIDA)
        con.close()

    def test_detected_retification_blocks_new_output(self):
        con = make_con(); fechar(con)
        con.execute("INSERT INTO fechamento_mensal_retificacao(competencia,cliente_id,status) VALUES('08/2026',1,'DETECTADA')")
        con.commit()
        r = autorizar_saida_cliente(con, cliente_id=1, competencia="08/2026")
        self.assertFalse(r["autorizado"])
        self.assertEqual(r["motivo"], RETIFICACAO_PENDENTE)
        con.close()

    def test_manual_ids_are_intersected_with_client_and_competence(self):
        con = make_con(); fechar(con)
        con.executemany(
            "INSERT INTO processamento_arquivo VALUES(?,?,?,?,?)",
            [
                (10,1,'08/2026','PROCESSADO',1),
                (11,2,'08/2026','PROCESSADO',1),
                (12,1,'07/2026','PROCESSADO',1),
            ],
        )
        con.commit()
        r = filtrar_documentos_autorizados(
            con, cliente_id=1, competencia="08/2026", documento_ids=[10,11,12]
        )
        self.assertEqual(r["documentos_autorizados"], [10])
        self.assertEqual(r["documentos_rejeitados"], [11,12])
        self.assertFalse(r["selecao_integralmente_autorizada"])
        self.assertEqual(r["motivo_selecao"], DOCUMENTO_FORA_DO_ESCOPO)
        con.close()

    def test_historical_document_version_is_not_released_by_id(self):
        con = make_con(); fechar(con)
        con.executemany(
            "INSERT INTO processamento_arquivo VALUES(?,?,?,?,?)",
            [(10,1,'08/2026','PROCESSADO',0),(11,1,'08/2026','PROCESSADO',1)],
        )
        con.commit()
        r = filtrar_documentos_autorizados(
            con, cliente_id=1, competencia="08/2026", documento_ids=[10,11]
        )
        self.assertEqual(r["documentos_autorizados"], [11])
        self.assertEqual(r["documentos_rejeitados"], [10])
        con.close()

    def test_duplicate_manual_ids_are_normalized(self):
        con = make_con(); fechar(con)
        con.execute("INSERT INTO processamento_arquivo VALUES(10,1,'08/2026','PROCESSADO',1)")
        con.commit()
        r = filtrar_documentos_autorizados(
            con, cliente_id=1, competencia="08/2026", documento_ids=[10,10,10]
        )
        self.assertEqual(r["documentos_solicitados"], [10])
        self.assertEqual(r["documentos_autorizados"], [10])
        self.assertTrue(r["selecao_integralmente_autorizada"])
        con.close()

    def test_empty_selection_is_safe_and_authorized_for_closed_client(self):
        con = make_con(); fechar(con)
        r = filtrar_documentos_autorizados(
            con, cliente_id=1, competencia="08/2026", documento_ids=[]
        )
        self.assertTrue(r["autorizado"])
        self.assertEqual(r["documentos_autorizados"], [])
        self.assertEqual(r["documentos_rejeitados"], [])
        con.close()


if __name__ == "__main__":
    unittest.main()
