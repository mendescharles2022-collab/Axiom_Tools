from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.processing import central
from axiom_tools.modules.processing.calendar_esocial import garantir_schema as garantir_calendario, inferir_competencia_detalhada, salvar_excecao
from axiom_tools.modules.processing.competence_provenance import backfill_processamento_proveniencia
from axiom_tools.modules.processing.motors.dominio_advanced import enriquecer_extrato_federal, extrair_irrf_dupla_competencia
from axiom_tools.modules.processing.reprocessing import _compare

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')

IRRF_FRAGMENT = '''
IRRF conforme competência do cálculo IRRF conforme competência do pagamento
Base IRRF Mensal: 1.980,58 Base IRRF Mensal: 1.980,58
Valor IRRF Mensal: 10,00 Valor IRRF Mensal: 20,00
Base IRRF Férias: 1.960,20 Base IRRF Férias: 0,00
Valor IRRF Férias: 0,00 Valor IRRF Férias: 0,00
Valor Total do IRRF: 10,00 Valor Total do IRRF: 20,00
IRRF Aluguéis: 0,00 IRRF Aluguéis: 0,00
IRRF contribuintes: 0,00 IRRF contribuintes: 0,00
Situações
'''


def calendar_con():
    con=sqlite3.connect(':memory:'); con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE processamento_config(id INTEGER PRIMARY KEY,esocial_calendario_ativo INTEGER DEFAULT 1,esocial_dia_inicio INTEGER DEFAULT 25,esocial_dia_fim INTEGER DEFAULT 9,esocial_excecoes_json TEXT DEFAULT '{}')")
    con.execute("INSERT INTO processamento_config VALUES(1,1,25,9,'{}')")
    garantir_calendario(con)
    return con


def snapshot(method: str, completeness=100):
    return {'arquivo': {'status':'PROCESSADO','completude':completeness,'confianca':completeness,'classificacao_confianca':100,'origem_confianca':100,'cliente_id':7,'competencia':'08/2026','competencia_metodo':method,'documento_tipo':'EXTRATO_MENSAL','origem_documental':'DOMINIO','dados_json':json.dumps({'competencia':'08/2026','competencia_metodo':method,'x':1})}, 'itens':[], 'esocial':[]}


class CompetenceTemporalV8Tests(unittest.TestCase):
    def test_default_calendar_is_fallback_with_versioned_provenance(self):
        con=calendar_con(); d=inferir_competencia_detalhada(con,'02/09/2026')
        self.assertEqual(d['competencia'],'08/2026'); self.assertEqual(d['janela'],'25/08/2026 a 09/09/2026'); self.assertTrue(d['regra_versao'].endswith('P25-09')); con.close()

    def test_december_and_thirteenth_use_configured_annual_exceptions(self):
        con=calendar_con(); salvar_excecao(con,competencia='13/2026',data_inicio='15/12/2026',data_fim='19/12/2026',tipo='13O'); salvar_excecao(con,competencia='12/2026',data_inicio='20/12/2026',data_fim='09/01/2027',tipo='DEZEMBRO')
        self.assertEqual(inferir_competencia_detalhada(con,'18/12/2026')['competencia'],'13/2026'); self.assertEqual(inferir_competencia_detalhada(con,'21/12/2026')['competencia'],'12/2026'); con.close()

    def test_exception_edit_creates_new_calendar_version_history(self):
        con=calendar_con(); a=salvar_excecao(con,competencia='13/2026',data_inicio='15/12/2026',data_fim='19/12/2026',tipo='13O'); b=salvar_excecao(con,competencia='13/2026',data_inicio='14/12/2026',data_fim='19/12/2026',tipo='13O')
        self.assertEqual((a['versao'],b['versao']),(1,2)); hist=con.execute("SELECT versao FROM processamento_esocial_calendario_historico WHERE competencia='13/2026' ORDER BY versao").fetchall(); self.assertEqual([r['versao'] for r in hist],[1,2]); con.close()

    def test_overlapping_special_windows_are_rejected(self):
        con=calendar_con(); salvar_excecao(con,competencia='13/2026',data_inicio='15/12/2026',data_fim='19/12/2026',tipo='13O')
        with self.assertRaises(ValueError): salvar_excecao(con,competencia='12/2026',data_inicio='19/12/2026',data_fim='09/01/2027',tipo='DEZEMBRO')
        con.close()

    def test_reprocessing_cannot_degrade_explicit_competence_to_calendar(self):
        decision,regressions=_compare(snapshot('DOCUMENTO_EXPLICITO',90),snapshot('CALENDARIO_INFERIDO',100)); self.assertEqual(decision,'REJEITADO_REGRESSAO'); self.assertIn('competencia_proveniencia',regressions)

    def test_backfill_does_not_invent_unknown_legacy_origin(self):
        con=sqlite3.connect(':memory:'); con.row_factory=sqlite3.Row; con.execute("CREATE TABLE processamento_arquivo(id INTEGER PRIMARY KEY,competencia TEXT,dados_json TEXT,origem_documental TEXT,processado_em TEXT,competencia_metodo TEXT,competencia_janela TEXT,competencia_regra_versao TEXT,competencia_determinada_em TEXT,competencia_evidencia TEXT)"); con.execute("INSERT INTO processamento_arquivo VALUES(1,'08/2026','{}','DOMINIO','2026-08-28 10:00:00',NULL,NULL,NULL,NULL,NULL)"); self.assertEqual(backfill_processamento_proveniencia(con),0); con.close()

    def test_backfill_normalizes_known_legacy_origin(self):
        con=sqlite3.connect(':memory:'); con.row_factory=sqlite3.Row; con.execute("CREATE TABLE processamento_arquivo(id INTEGER PRIMARY KEY,competencia TEXT,dados_json TEXT,origem_documental TEXT,processado_em TEXT,competencia_metodo TEXT,competencia_janela TEXT,competencia_regra_versao TEXT,competencia_determinada_em TEXT,competencia_evidencia TEXT)"); dados=json.dumps({'competencia':'08/2026','competencia_metodo':'DOCUMENTO'}); con.execute("INSERT INTO processamento_arquivo VALUES(1,'08/2026',?,'DOMINIO','2026-08-28 10:00:00',NULL,NULL,NULL,NULL,NULL)",(dados,)); self.assertEqual(backfill_processamento_proveniencia(con),1); self.assertEqual(con.execute('SELECT competencia_metodo FROM processamento_arquivo').fetchone()[0],'DOCUMENTO_EXPLICITO'); con.close()

    @unittest.skipUnless(SOURCE_DB.exists(),'snapshot real indisponível')
    def test_explicit_esocial_competence_is_persisted_above_calendar(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'db.sqlite'; shutil.copy2(SOURCE_DB,db); con=sqlite3.connect(db); con.row_factory=sqlite3.Row
            xml=b'<eSocial><evtRemun Id="ID1"><ideEvento><indApur>1</indApur><perApur>2026-08</perApur></ideEvento><ideEmpregador><tpInsc>1</tpInsc><nrInsc>39373545</nrInsc></ideEmpregador></evtRemun></eSocial>'
            pid,_=central.processar_conteudo_misto(con,origem_id=None,origem_nome='TESTE',entrada_fisica='UPLOAD_MANUAL',caminho_logico='explicit.xml',nome='explicit.xml',conteudo=xml); r=con.execute('SELECT competencia,competencia_metodo FROM processamento_arquivo WHERE id=?',(pid,)).fetchone(); self.assertEqual((r['competencia'],r['competencia_metodo']),('08/2026','DOCUMENTO_EXPLICITO')); con.close()

    @unittest.skipUnless(SOURCE_DB.exists(),'snapshot real indisponível')
    def test_calendar_inferred_esocial_persists_window_and_rule(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'db.sqlite'; shutil.copy2(SOURCE_DB,db); con=sqlite3.connect(db); con.row_factory=sqlite3.Row
            xml=b'<eSocial><evtFechaEvPer Id="ID2"><ideEvento><indApur>1</indApur></ideEvento><ideEmpregador><tpInsc>1</tpInsc><nrInsc>39373545</nrInsc></ideEmpregador><info>Data de Envio: 02/09/2026</info></evtFechaEvPer></eSocial>'
            pid,_=central.processar_conteudo_misto(con,origem_id=None,origem_nome='TESTE',entrada_fisica='UPLOAD_MANUAL',caminho_logico='calendar.xml',nome='calendar.xml',conteudo=xml); r=con.execute('SELECT competencia,competencia_metodo,competencia_janela,competencia_regra_versao FROM processamento_arquivo WHERE id=?',(pid,)).fetchone(); self.assertEqual((r['competencia'],r['competencia_metodo']),('08/2026','CALENDARIO_INFERIDO')); self.assertEqual(r['competencia_janela'],'25/08/2026 a 09/09/2026'); self.assertIn('P25-09',r['competencia_regra_versao']); con.close()

    def test_irrf_preserves_calculation_and_payment_views(self):
        r=extrair_irrf_dupla_competencia(IRRF_FRAGMENT); self.assertAlmostEqual(r['irrf_competencia_calculo']['base_ferias'],1960.20); self.assertAlmostEqual(r['irrf_competencia_pagamento']['base_ferias'],0.0); self.assertAlmostEqual(r['irrf_total_calculo'],10.0); self.assertAlmostEqual(r['irrf_total_pagamento'],20.0); self.assertEqual(r['irrf_criterio_competencia'],'PAGAMENTO')

    def test_federal_enrichment_keeps_balance_authoritative(self):
        texto=IRRF_FRAGMENT+'\nApuração Tributos Federais\nEncargos Valor (-)Compensação DCOMP (-)Salário Família (-)Salário Maternidade (-)Retenções Saldo a recolher\nINSS Segurado(Folha): 100,00 0,00 0,00 0,00 0,00 100,00\nSaldo à recolher: 100,00\n'; campos={'total_inss':100.0}; enriquecer_extrato_federal(texto,campos); self.assertAlmostEqual(campos['saldo_total_apuracao_dominio'],100.0); self.assertAlmostEqual(campos['irrf_total_pagamento'],20.0); self.assertEqual(campos['federal_fonte_autoritativa'],'APURACAO_TRIBUTOS_FEDERAIS_SALDO_A_RECOLHER')


if __name__=='__main__': unittest.main()
