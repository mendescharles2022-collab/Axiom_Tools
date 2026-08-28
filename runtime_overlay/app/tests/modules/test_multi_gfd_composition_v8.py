from __future__ import annotations

import json
import sqlite3
import unittest
from pathlib import Path

from axiom_tools.modules.processing.fgts_composition import compor_guias_fgts

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def guia(id_: int, dados: dict, *, sha: str | None = None) -> dict:
    return {
        'id': id_,
        'documento_tipo': 'GUIA_FGTS_DIGITAL',
        'status': 'PROCESSADO',
        'nome_original': f'gfd-{id_}.pdf',
        'sha256': sha or f'sha-{id_}',
        'competencia': dados.get('competencia', '08/2026'),
        'dados': dados,
    }


class MultiGfdCompositionV8Tests(unittest.TestCase):
    def test_equivalent_reissue_counts_once(self):
        d={'competencia':'08/2026','cnpj_raiz':'12345678','fgts_total':1000.0,'fgts_rescisorio':0.0,
           'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1000.0}
        c=compor_guias_fgts([guia(1,d,sha='a'),guia(2,d,sha='b')])
        self.assertEqual(c['fgts_total'],1000.0)
        self.assertEqual(c['_composicao_gfd']['duplicatas_equivalentes'],1)
        self.assertEqual(c['_composicao_gfd']['quantidade_efetivos'],1)

    def test_monthly_plus_separate_rescissory_are_added(self):
        mensal={'competencia':'08/2026','fgts_total':1000.0,'fgts_rescisorio':0.0,
                'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1000.0}
        res={'competencia':'08/2026','fgts_total':200.0,'fgts_rescisorio':200.0,
             'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':200.0}
        c=compor_guias_fgts([guia(1,mensal),guia(2,res)])
        self.assertEqual(c['fgts_mensal'],1000.0)
        self.assertEqual(c['fgts_rescisorio'],200.0)
        self.assertEqual(c['fgts_total'],1200.0)
        self.assertEqual(c['_composicao_gfd']['conflitos'],[])

    def test_more_complete_successor_does_not_double_monthly(self):
        antiga={'competencia':'08/2026','fgts_total':1000.0,'fgts_rescisorio':0.0,
                'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1000.0}
        nova={'competencia':'08/2026','fgts_total':1200.0,'fgts_rescisorio':200.0,
              'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1200.0}
        c=compor_guias_fgts([guia(1,antiga),guia(2,nova)])
        self.assertEqual(c['fgts_total'],1200.0)
        self.assertEqual(c['_composicao_gfd']['guias_cobertas_por_sucessora'],1)
        self.assertEqual(c['_composicao_gfd']['quantidade_efetivos'],1)

    def test_overlapping_monthly_values_conflict_instead_of_sum(self):
        a={'competencia':'08/2026','fgts_total':1000.0,'fgts_rescisorio':0.0,
           'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1000.0}
        b={'competencia':'08/2026','fgts_total':1100.0,'fgts_rescisorio':0.0,
           'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':0.0,'guia_total':1100.0}
        c=compor_guias_fgts([guia(1,a),guia(2,b)])
        self.assertIsNone(c['fgts_total'])
        self.assertTrue(any(x['componente']=='mensal' for x in c['_composicao_gfd']['conflitos']))

    def test_authoritative_total_repairs_bad_intermediate_monthly(self):
        d={'competencia':'08/2026','fgts_mensal':1546.02,'fgts_total':546.02,'fgts_rescisorio':0.0,
           'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':354.43,'guia_total':900.45}
        c=compor_guias_fgts([guia(1,d)])
        self.assertEqual(c['fgts_mensal'],546.02)
        self.assertEqual(c['fgts_total'],546.02)
        self.assertEqual(c['consignado_total'],354.43)
        self.assertEqual(c['guia_total'],900.45)

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_ribeiro_uses_total_fgts_not_contaminated_monthly_field(self):
        con=sqlite3.connect(SOURCE_DB); con.row_factory=sqlite3.Row
        row=con.execute("""SELECT id,documento_tipo,status,nome_original,sha256,competencia,dados_json
            FROM processamento_arquivo WHERE cliente_id=694 AND competencia='08/2026'
              AND documento_tipo='GUIA_FGTS_DIGITAL' AND COALESCE(documento_vigente,1)=1 LIMIT 1""").fetchone()
        con.close()
        c=compor_guias_fgts([dict(row)])
        self.assertEqual(c['fgts_mensal'],546.02)
        self.assertEqual(c['fgts_total'],546.02)
        self.assertEqual(c['consignado_total'],354.43)
        self.assertEqual(c['guia_total'],900.45)


if __name__=='__main__':
    unittest.main()
