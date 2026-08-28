from __future__ import annotations

import json
import sqlite3
import unittest
from pathlib import Path

from axiom_tools.modules.processing.composition import compor_extratos_mensais
from axiom_tools.modules.processing.conference import _check_darf_folha, _cmp

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def doc(id_: int, dados: dict, *, nome: str = 'Extrato Mensal.pdf', sha: str | None = None) -> dict:
    return {
        'id': id_,
        'documento_tipo': 'EXTRATO_MENSAL',
        'status': 'PROCESSADO',
        'nome_original': nome,
        'sha256': sha or f'sha-{id_}',
        'competencia': dados.get('competencia', '08/2026'),
        'dados': dados,
    }


class MultiExtratoCompositionV8Tests(unittest.TestCase):
    def test_equivalent_reissue_counts_once(self):
        dados = {
            'competencia': '08/2026', 'cnpj': '02.143.041/0001-62',
            'total_proventos': 3000.0, 'total_descontos': 500.0, 'liquido_geral': 2500.0,
            'total_inss': 224.73, 'fgts_total': 0.0, 'darf_folha_esperado': 224.73,
            'saldo_total_apuracao_dominio': 224.73, 'apuracao_federal_detalhada': True,
        }
        c = compor_extratos_mensais([doc(1, dados, sha='a'), doc(2, dados, sha='b')])
        self.assertEqual(c['total_inss'], 224.73)
        self.assertEqual(c['fgts_total'], 0.0)
        self.assertEqual(c['saldo_total_apuracao_dominio'], 224.73)
        self.assertEqual(c['_composicao_extratos']['quantidade_componentes'], 1)
        self.assertEqual(c['_composicao_extratos']['duplicatas_equivalentes'], 1)

    def test_distinct_components_add_fgts_but_not_consolidated_federal(self):
        a = {
            'competencia': '08/2026', 'total_proventos': 3818.64, 'total_descontos': 2319.21,
            'liquido_geral': 1499.43, 'total_inss': 155.33, 'fgts_total': 129.68,
            'darf_folha_esperado': 155.33, 'saldo_total_apuracao_dominio': 511.43,
            'apuracao_federal_detalhada': True,
        }
        b = {
            'competencia': '08/2026', 'total_proventos': 3242.0, 'total_descontos': 277.62,
            'liquido_geral': 2964.38, 'total_inss': 284.10, 'fgts_total': 259.36,
            'darf_folha_esperado': 284.10, 'saldo_total_apuracao_dominio': 511.43,
            'apuracao_federal_detalhada': True,
        }
        c = compor_extratos_mensais([doc(1, a), doc(2, b)])
        self.assertEqual(c['total_inss'], 439.43)
        self.assertEqual(c['darf_folha_esperado'], 439.43)
        self.assertEqual(c['fgts_total'], 389.04)
        self.assertEqual(c['saldo_total_apuracao_dominio'], 511.43)
        self.assertFalse(c['_composicao_extratos']['saldo_federal_conflitante'])
        self.assertEqual(c['_composicao_extratos']['quantidade_componentes'], 2)

    def test_conflicting_consolidated_federal_is_not_summed(self):
        a = {'competencia':'08/2026','total_inss':100,'fgts_total':80,'darf_folha_esperado':100,
             'saldo_total_apuracao_dominio':300,'apuracao_federal_detalhada':True}
        b = {'competencia':'08/2026','total_inss':200,'fgts_total':160,'darf_folha_esperado':200,
             'saldo_total_apuracao_dominio':400,'apuracao_federal_detalhada':True}
        c = compor_extratos_mensais([doc(1,a),doc(2,b)])
        self.assertIsNone(c['saldo_total_apuracao_dominio'])
        self.assertTrue(c['_composicao_extratos']['saldo_federal_conflitante'])
        check = _check_darf_folha(c, {'valor_total': 700})
        self.assertEqual(check['status'], 'BASE_CONFLITANTE')
        self.assertEqual(check['saldos_federais'], [300.0, 400.0])

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_leosmar_duplicate_is_deduplicated(self):
        con = sqlite3.connect(SOURCE_DB)
        con.row_factory = sqlite3.Row
        rows = con.execute("""SELECT id,documento_tipo,status,nome_original,sha256,competencia,dados_json
            FROM processamento_arquivo WHERE cliente_id=513 AND competencia='08/2026'
              AND documento_tipo='EXTRATO_MENSAL' AND COALESCE(documento_vigente,1)=1 ORDER BY id""").fetchall()
        c = compor_extratos_mensais([dict(r) for r in rows])
        con.close()
        self.assertEqual(len(rows), 2)
        self.assertEqual(c['_composicao_extratos']['quantidade_componentes'], 1)
        self.assertEqual(c['_composicao_extratos']['duplicatas_equivalentes'], 1)
        self.assertEqual(c['darf_folha_esperado'], 224.73)
        self.assertEqual(c['saldo_total_apuracao_dominio'], 224.73)
        self.assertEqual(c['fgts_total'], 0.0)

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_jair_history_reconstructs_two_components(self):
        con = sqlite3.connect(SOURCE_DB)
        con.row_factory = sqlite3.Row
        rows = con.execute("""SELECT id,processamento_id,tipo_anterior,status_anterior,nome_original_anterior,
                   sha256_anterior,competencia_anterior,dados_json_anterior
            FROM processamento_reprocessamento_historico
            WHERE cliente_id_anterior=826 AND competencia_anterior='08/2026'
              AND tipo_anterior='EXTRATO_MENSAL'
              AND nome_original_anterior IN ('449-Extrato Mensal.pdf','450-Extrato Mensal.pdf')
            ORDER BY id""").fetchall()
        docs=[]
        for r in rows:
            docs.append({
                'id': r['processamento_id'], 'documento_tipo': r['tipo_anterior'],
                'status': r['status_anterior'], 'nome_original': r['nome_original_anterior'],
                'sha256': r['sha256_anterior'], 'competencia': r['competencia_anterior'],
                'dados_json': r['dados_json_anterior'],
            })
        c = compor_extratos_mensais(docs)
        con.close()
        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(c['_composicao_extratos']['quantidade_componentes'], 2)
        self.assertEqual(c['total_inss'], 439.43)
        self.assertEqual(c['fgts_total'], 389.04)
        self.assertEqual(c['saldo_total_apuracao_dominio'], 511.43)
        self.assertEqual(c['darf_folha_esperado'], 439.43)

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_jair_composition_confers_with_darf_and_gfd(self):
        con = sqlite3.connect(SOURCE_DB)
        con.row_factory = sqlite3.Row
        hist = con.execute("""SELECT processamento_id,tipo_anterior,status_anterior,nome_original_anterior,
                   sha256_anterior,competencia_anterior,dados_json_anterior
            FROM processamento_reprocessamento_historico
            WHERE cliente_id_anterior=826 AND competencia_anterior='08/2026'
              AND tipo_anterior='EXTRATO_MENSAL'
              AND nome_original_anterior IN ('449-Extrato Mensal.pdf','450-Extrato Mensal.pdf')
            ORDER BY id""").fetchall()
        docs=[{
            'id': r['processamento_id'], 'documento_tipo': r['tipo_anterior'],
            'status': r['status_anterior'], 'nome_original': r['nome_original_anterior'],
            'sha256': r['sha256_anterior'], 'competencia': r['competencia_anterior'],
            'dados_json': r['dados_json_anterior'],
        } for r in hist]
        exd = compor_extratos_mensais(docs)
        darf = con.execute("""SELECT dados_json FROM processamento_arquivo
            WHERE cliente_id=826 AND competencia='08/2026' AND documento_tipo='DARF'
              AND COALESCE(documento_vigente,1)=1 AND status='PROCESSADO' ORDER BY id DESC LIMIT 1""").fetchone()
        gfd = con.execute("""SELECT dados_json FROM processamento_arquivo
            WHERE cliente_id=826 AND competencia='08/2026' AND documento_tipo='GUIA_FGTS_DIGITAL'
              AND COALESCE(documento_vigente,1)=1 AND status='PROCESSADO' ORDER BY id DESC LIMIT 1""").fetchone()
        con.close()
        dd=json.loads(darf['dados_json']); gd=json.loads(gfd['dados_json'])
        darf_check = _check_darf_folha(exd, dd)
        fgts_check = _cmp(exd['fgts_total'], gd['fgts_total'])
        self.assertEqual(darf_check['status'], 'CONFERIDO')
        self.assertEqual(darf_check['esperado'], 511.43)
        self.assertEqual(darf_check['inss_esperado'], 439.43)
        self.assertEqual(darf_check['previdenciario_darf'], 439.43)
        self.assertEqual(fgts_check['status'], 'CONFERIDO')
        self.assertEqual(exd['fgts_total'], 389.04)
        self.assertEqual(gd['fgts_total'], 389.04)


if __name__ == '__main__':
    unittest.main()
