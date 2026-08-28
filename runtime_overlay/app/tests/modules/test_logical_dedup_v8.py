from __future__ import annotations

import unittest

from axiom_tools.modules.processing.logical_dedup import fingerprint_logico, relacao_documental
from axiom_tools.modules.processing.composition import compor_extratos_mensais
from axiom_tools.modules.processing.fgts_composition import compor_guias_fgts


class LogicalDedupV8Tests(unittest.TestCase):
    def test_same_sha_means_same_physical_file(self):
        self.assertEqual(
            relacao_documental(sha_a='abc', sha_b='ABC', fingerprint_a='x', fingerprint_b='y'),
            'MESMOS_BYTES',
        )

    def test_different_bytes_can_be_same_economic_obligation(self):
        fp = fingerprint_logico({'competencia':'08/2026','valor':100.0})
        self.assertEqual(
            relacao_documental(sha_a='a', sha_b='b', fingerprint_a=fp, fingerprint_b=fp),
            'EQUIVALENTE_LOGICO',
        )

    def test_different_fingerprints_are_distinct_obligations(self):
        a = fingerprint_logico({'valor':100.0}); b = fingerprint_logico({'valor':200.0})
        self.assertEqual(relacao_documental(fingerprint_a=a, fingerprint_b=b), 'DISTINTO_LOGICO')

    def test_missing_economic_evidence_is_indeterminate(self):
        self.assertEqual(relacao_documental(sha_a='a', sha_b='b'), 'INDETERMINADO')

    def test_extrato_reissue_with_different_sha_counts_once(self):
        base = {
            'documento_tipo':'EXTRATO_MENSAL','status':'PROCESSADO','competencia':'08/2026',
            'dados': {'competencia':'08/2026','total_inss':100.0,'fgts_total':80.0,'darf_folha_esperado':100.0,
                      'saldo_total_apuracao_dominio':100.0,'total_proventos':1000.0,'total_descontos':100.0,'liquido_geral':900.0},
        }
        a={**base,'id':1,'sha256':'sha-a'}; b={**base,'id':2,'sha256':'sha-b'}
        r=compor_extratos_mensais([a,b])
        self.assertEqual(r['_composicao_extratos']['quantidade_componentes'],1)
        self.assertEqual(r['_composicao_extratos']['duplicatas_equivalentes'],1)
        self.assertAlmostEqual(r['fgts_total'],80.0)

    def test_gfd_reissue_with_different_sha_counts_once(self):
        base={
            'documento_tipo':'GUIA_FGTS_DIGITAL','status':'PROCESSADO','competencia':'08/2026',
            'dados': {'competencia':'08/2026','fgts_total':80.0,'fgts_rescisorio':0.0,
                      'indenizacao_compensatoria':0.0,'encargos_fgts':0.0,'consignado_total':20.0,'guia_total':100.0},
        }
        a={**base,'id':1,'sha256':'sha-a'}; b={**base,'id':2,'sha256':'sha-b'}
        r=compor_guias_fgts([a,b])
        self.assertEqual(r['_composicao_gfd']['quantidade_unicos'],1)
        self.assertEqual(r['_composicao_gfd']['duplicatas_equivalentes'],1)
        self.assertAlmostEqual(r['guia_total'],100.0)


if __name__ == '__main__':
    unittest.main()
