from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.closing.output_gate import SaidaNaoAutorizada, exigir_documentos_autorizados
from axiom_tools.modules.printing import service as printing
from axiom_tools.modules.delivery import service as delivery

SCHEMA = """
CREATE TABLE fechamento_mensal(competencia TEXT PRIMARY KEY, chamada_atual INTEGER DEFAULT 1);
CREATE TABLE fechamento_mensal_cliente(competencia TEXT,cliente_id INTEGER,status TEXT,versao_atual INTEGER DEFAULT 0,PRIMARY KEY(competencia,cliente_id));
CREATE TABLE fechamento_mensal_versao(id INTEGER PRIMARY KEY AUTOINCREMENT,competencia TEXT,cliente_id INTEGER,versao INTEGER,natureza TEXT,snapshot_hash TEXT,snapshot_json TEXT);
CREATE TABLE fechamento_mensal_retificacao(id INTEGER PRIMARY KEY AUTOINCREMENT,competencia TEXT,cliente_id INTEGER,base_versao INTEGER,status TEXT,snapshot_hash TEXT,snapshot_json TEXT,delta_json TEXT);
CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,nome_apresentacao TEXT,documento TEXT,situacao TEXT DEFAULT 'ATIVO');
CREATE TABLE cliente_parametros(cliente_id INTEGER PRIMARY KEY,movimento_folha TEXT);
CREATE TABLE processamento_arquivo(id INTEGER PRIMARY KEY,cliente_id INTEGER,competencia TEXT,status TEXT,tipo_arquivo TEXT DEFAULT 'PDF',documento_vigente INTEGER DEFAULT 1,documento_tipo TEXT,documento_cliente TEXT,nome_original TEXT,origem_documental TEXT,caminho_origem TEXT,entrada_fisica TEXT,origem_id INTEGER,repositorio_caminho TEXT,arquivamento_status TEXT DEFAULT 'ARQUIVADO');
"""


def make_con():
    con=sqlite3.connect(':memory:'); con.row_factory=sqlite3.Row; con.executescript(SCHEMA)
    con.execute("INSERT INTO fechamento_mensal VALUES('08/2026',1)")
    con.execute("INSERT INTO clientes(id,nome,documento) VALUES(1,'Fechado','DOC1')")
    con.execute("INSERT INTO clientes(id,nome,documento) VALUES(2,'Ainda aberto','DOC2')")
    con.execute("INSERT INTO fechamento_mensal_cliente VALUES('08/2026',1,'FECHADA',1)")
    con.execute("INSERT INTO fechamento_mensal_cliente VALUES('08/2026',2,'PRONTA',0)")
    con.execute("INSERT INTO fechamento_mensal_versao(competencia,cliente_id,versao,natureza,snapshot_hash,snapshot_json) VALUES('08/2026',1,1,'ORIGINAL','h1','{}')")
    con.execute("INSERT INTO processamento_arquivo(id,cliente_id,competencia,status,nome_original,documento_tipo) VALUES(10,1,'08/2026','PROCESSADO','ok.pdf','DARF')")
    con.execute("INSERT INTO processamento_arquivo(id,cliente_id,competencia,status,nome_original,documento_tipo) VALUES(11,2,'08/2026','PROCESSADO','nao.pdf','DARF')")
    con.commit(); return con


class ManualOutputIdsV8Tests(unittest.TestCase):
    def test_mixed_manual_document_ids_are_rejected_as_whole(self):
        con=make_con()
        with self.assertRaises(SaidaNaoAutorizada):
            exigir_documentos_autorizados(con,'08/2026',[10,11],tipo_saida='IMPRESSAO')
        con.close()

    def test_printing_explicit_id_cannot_bypass_closing_gate(self):
        con=make_con()
        with tempfile.TemporaryDirectory() as td, self.assertRaises(SaidaNaoAutorizada):
            printing.gerar_lote(con,Path(td),ids=[11],competencia='08/2026')
        con.close()

    def test_delivery_single_manual_id_cannot_bypass_closing_gate(self):
        con=make_con()
        with tempfile.TemporaryDirectory() as td, self.assertRaises(ValueError) as ctx:
            delivery.gerar_cliente(con,Path(td),2,'08/2026')
        self.assertIn('STATUS_NAO_AUTORIZA',str(ctx.exception))
        con.close()


if __name__ == '__main__':
    unittest.main()
