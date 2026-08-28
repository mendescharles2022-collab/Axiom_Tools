from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from axiom_tools.modules.closing.universe import clientes_chamada_atual_ids
from axiom_tools.modules.processing.conference import conferencia_competencia
from axiom_tools.modules.processing.consignados import (
    clientes_consulta,
    criar_job,
    criar_retry_job,
    garantir_schema,
    painel,
)
from axiom_tools.modules.processing import consignado_sync_worker as worker

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def copy_db(tmp: str) -> Path:
    p = Path(tmp) / 'axiom_tools.db'
    shutil.copy2(SOURCE_DB, p)
    return p


def memory_con() -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    garantir_schema(con)
    return con


class EconsignadoOrchestrationV8Tests(unittest.TestCase):
    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_job_universe_is_current_closing_call_not_historical_clients(self):
        with tempfile.TemporaryDirectory() as td:
            con = sqlite3.connect(copy_db(td)); con.row_factory = sqlite3.Row
            garantir_schema(con)
            ids = clientes_chamada_atual_ids(con, '08/2026')
            alvos = clientes_consulta(con, '08/2026')
            self.assertEqual(len(ids), 30)
            self.assertEqual({x['cliente_id'] for x in alvos}, ids)
            self.assertEqual(len(alvos), 30)
            con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_created_job_freezes_call_and_scope_hash(self):
        with tempfile.TemporaryDirectory() as td:
            con = sqlite3.connect(copy_db(td)); con.row_factory = sqlite3.Row
            job_id = criar_job(con, competencia='08/2026')
            job = con.execute('SELECT * FROM processamento_consignado_job WHERE id=?',(job_id,)).fetchone()
            self.assertEqual(job['total_empregadores'], 30)
            self.assertEqual(job['chamada'], 1)
            self.assertEqual(job['escopo'], 'CICLO')
            self.assertEqual(len(job['escopo_hash']), 64)
            self.assertEqual(con.execute('SELECT COUNT(*) FROM processamento_consignado_consulta WHERE job_id=?',(job_id,)).fetchone()[0], 30)
            con.close()

    def test_failed_or_blocked_query_preserves_last_good_snapshot(self):
        con = memory_con()
        con.execute("INSERT INTO processamento_consignado_snapshot(competencia,cliente_id,cnpj,cpf,contrato,valor_parcela,origem) VALUES('08/2026',1,'123','111','OLD',100,'MTE_API')")
        con.commit()
        job={'competencia':'08/2026'}
        alvo={'cliente_id':1,'empregador_tipo':'CNPJ','empregador_inscricao':'123','empregador_nome':'Cliente'}
        for status in ('SEM_PROCURACAO','NAO_DISPONIVEL','ERRO'):
            changed = worker._promover_snapshot_oficial(con,job,alvo,status,[])
            self.assertFalse(changed)
            row=con.execute("SELECT contrato,valor_parcela FROM processamento_consignado_snapshot WHERE cliente_id=1").fetchone()
            self.assertEqual((row['contrato'],row['valor_parcela']),('OLD',100.0))
        con.close()

    def test_authoritative_empty_clears_snapshot_and_success_replaces_it(self):
        con = memory_con()
        con.execute("INSERT INTO processamento_consignado_snapshot(competencia,cliente_id,cnpj,cpf,contrato,valor_parcela,origem) VALUES('08/2026',1,'123','111','OLD',100,'MTE_API')")
        job={'competencia':'08/2026'}
        alvo={'cliente_id':1,'empregador_tipo':'CNPJ','empregador_inscricao':'123','empregador_nome':'Cliente'}
        self.assertTrue(worker._promover_snapshot_oficial(con,job,alvo,'SEM_CONSIGNADO',[]))
        self.assertEqual(con.execute('SELECT COUNT(*) FROM processamento_consignado_snapshot').fetchone()[0],0)
        registro={'cpf':'111','pessoa_nome':'Pessoa','contrato':'NEW','valor_parcela':250.0,'payload':{}}
        self.assertTrue(worker._promover_snapshot_oficial(con,job,alvo,'COM_CONSIGNADO',[registro]))
        row=con.execute('SELECT contrato,valor_parcela FROM processamento_consignado_snapshot').fetchone()
        self.assertEqual((row['contrato'],row['valor_parcela']),('NEW',250.0))
        con.close()

    def test_failed_promotion_rolls_back_previous_snapshot(self):
        con = memory_con()
        con.execute("INSERT INTO processamento_consignado_snapshot(competencia,cliente_id,cnpj,cpf,contrato,valor_parcela,origem) VALUES('08/2026',1,'123','111','OLD',100,'MTE_API')")
        job={'competencia':'08/2026'}
        alvo={'cliente_id':1,'empregador_tipo':'CNPJ','empregador_inscricao':'123','empregador_nome':'Cliente'}
        with patch.object(worker, '_salvar_snapshot', side_effect=RuntimeError('falhou')):
            with self.assertRaises(RuntimeError):
                worker._promover_snapshot_oficial(con,job,alvo,'COM_CONSIGNADO',[{'contrato':'NEW'}])
        row=con.execute('SELECT contrato,valor_parcela FROM processamento_consignado_snapshot').fetchone()
        self.assertEqual((row['contrato'],row['valor_parcela']),('OLD',100.0))
        con.close()

    def test_retry_creates_new_auditable_job_without_mutating_old(self):
        con=memory_con()
        cur=con.execute("INSERT INTO processamento_consignado_job(competencia,ambiente,certificado_id,status,total_empregadores,chamada,escopo) VALUES('08/2026','PRODUCAO',1,'CONCLUIDO_COM_ALERTAS',2,1,'CICLO')")
        old=int(cur.lastrowid)
        con.execute("INSERT INTO processamento_consignado_consulta(job_id,cliente_id,empregador_tipo,empregador_inscricao,empregador_nome,status) VALUES(?,1,'CNPJ','123','A','ERRO')",(old,))
        con.execute("INSERT INTO processamento_consignado_consulta(job_id,cliente_id,empregador_tipo,empregador_inscricao,empregador_nome,status) VALUES(?,2,'CNPJ','456','B','SEM_PROCURACAO')",(old,))
        con.commit()
        new=criar_retry_job(con,old)
        job=con.execute('SELECT * FROM processamento_consignado_job WHERE id=?',(new,)).fetchone()
        self.assertEqual(job['retry_de_job_id'],old)
        self.assertEqual(job['total_empregadores'],1)
        self.assertEqual(job['status'],'PENDENTE')
        self.assertEqual(con.execute('SELECT status FROM processamento_consignado_job WHERE id=?',(old,)).fetchone()[0],'CONCLUIDO_COM_ALERTAS')
        self.assertEqual(con.execute('SELECT empregador_inscricao FROM processamento_consignado_consulta WHERE job_id=?',(new,)).fetchone()[0],'123')
        con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_contextual_cases_are_not_false_conferred(self):
        expected={
            ('D A F Castro',205):('DIVERGENTE',591.86),
            ('D&L Alimentos',212):('RETORNO_RESIDUAL',603.38),
            ('GL Auto Center',362):('PAGAMENTO_DIRETO_JUSTIFICADO',0.0),
            ('Lourenconi',524):('DIVERGENTE',230.91),
        }
        with tempfile.TemporaryDirectory() as td:
            con=sqlite3.connect(copy_db(td)); con.row_factory=sqlite3.Row
            for (busca,cid),(status,dif) in expected.items():
                dados=conferencia_competencia(con,'08/2026',busca,'','TODAS')
                linha=next(x for x in dados['linhas'] if x['cliente_id']==cid)
                check=linha['checks']['econsignado']
                self.assertEqual(check['status'],status,busca)
                self.assertAlmostEqual(check['diferenca'],dif,msg=busca)
            con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_panel_and_conference_use_same_contextual_status(self):
        with tempfile.TemporaryDirectory() as td:
            con=sqlite3.connect(copy_db(td)); con.row_factory=sqlite3.Row
            for busca,cid in [('D A F Castro',205),('D&L Alimentos',212),('GL Auto Center',362),('Lourenconi',524)]:
                conf=conferencia_competencia(con,'08/2026',busca,'','TODAS')
                c=next(x for x in conf['linhas'] if x['cliente_id']==cid)['checks']['econsignado']['status']
                pan=painel(con,competencia='08/2026',busca=busca,pagina=1,por_pagina=10)
                p=next(x for x in pan['empresas'] if x['cliente_id']==cid)['status']
                self.assertEqual(p,c,busca)
            con.close()

    def test_worker_has_explicit_conference_recalculation_hook(self):
        src=Path(worker.__file__).read_text(encoding='utf-8')
        self.assertIn('sincronizar_conferencia_competencia',src)
        self.assertNotIn('status in {"COM_CONSIGNADO", "SEM_CONSIGNADO", "SEM_PROCURACAO", "NAO_DISPONIVEL"}',src)


if __name__=='__main__':
    unittest.main()
