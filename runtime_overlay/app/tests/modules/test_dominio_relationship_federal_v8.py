from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.processing.dominio import _dados_extrato
from axiom_tools.modules.processing.motors.dominio_advanced import (
    enriquecer_extrato_federal,
    extrair_situacoes_extrato,
)
from axiom_tools.modules.processing.conference import conferencia_competencia

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')

P_DA_SILVA_FRAGMENT = '''
Contr: 1 POLIANA DA SILVA CARMO Situação: Trabalhando CPF: 046.793.751-67 Adm: 09/10/2020
Vínculo: Diretor CC: 1 Depto: 1 Horas Mês:
Cargo: 1 GERENTE ADMINISTRATIVO C.B.O: 142105 Filial: 1 Salário: 2.000,00
9380 PRO-LABORE DIAS 31,00 2.000,00 P 843 INSS EMPREGADOR 11,00 220,00 D
Total Geral Proventos: 2.000,00 Total Geral Descontos: 220,00
Líquido Geral: 1.780,00
Total INSS: 220,00
Valor do FGTS: 0,00
Contribuintes: 0,00 Valor FGTS Resc. mês ant.: 0,00
Situações
No. Empregados: 0 Demitido: 0
No. Estagiários: 0 Transferido: 0
Trabalhando: 0 Férias: 0
Doença Profissional: 0 No. Contribuintes: 1
Apuração Tributos Federais
Saldo a compensar
(-)Compensação DCOMP: 0,00 (-)Salário Família: 0,00
(-)Salário Maternidade: 0,00 (-)Retenções: 0,00
Encargos Valor (-)Compensação DCOMP (-)Salário Família (-)Salário Maternidade (-)Retenções Saldo a recolher
INSS Segurado(Folha): 220,00 0,00 0,00 0,00 0,00 220,00
Saldo à recolher: 220,00
Saldo remanescente à restituir
'''


class DominioRelationshipFederalV8Tests(unittest.TestCase):
    def test_director_working_is_contributor_not_employee(self):
        r = extrair_situacoes_extrato(P_DA_SILVA_FRAGMENT)
        self.assertEqual(r['numero_empregados'], 0)
        self.assertEqual(r['numero_contribuintes'], 1)
        self.assertFalse(r['tem_empregados'])
        self.assertTrue(r['tem_contribuintes'])
        self.assertEqual(len(r['pessoas_resumo']), 1)
        pessoa = r['pessoas_resumo'][0]
        self.assertEqual(pessoa['registro_tipo'], 'CONTRIBUINTE')
        self.assertEqual(pessoa['vinculo'].upper(), 'DIRETOR')
        self.assertEqual(pessoa['situacao'].upper(), 'TRABALHANDO')

    def test_monetary_contribuintes_zero_does_not_change_headcount(self):
        r = extrair_situacoes_extrato(P_DA_SILVA_FRAGMENT)
        self.assertEqual(r['numero_contribuintes'], 1)
        self.assertTrue(r['tem_contribuintes'])

    def test_federal_authoritative_source_is_saldo_a_recolher(self):
        campos = {'total_inss': 220.0}
        enriquecer_extrato_federal(P_DA_SILVA_FRAGMENT, campos)
        self.assertTrue(campos['apuracao_federal_detalhada'])
        self.assertAlmostEqual(campos['darf_folha_esperado'], 220.0)
        self.assertAlmostEqual(campos['saldo_total_apuracao_dominio'], 220.0)
        self.assertEqual(campos['federal_fonte_autoritativa'], 'APURACAO_TRIBUTOS_FEDERAIS_SALDO_A_RECOLHER')

    def test_legacy_extrato_parser_uses_official_situations_counts(self):
        d = _dados_extrato(P_DA_SILVA_FRAGMENT)
        self.assertEqual(d['numero_empregados'], 0)
        self.assertEqual(d['numero_contribuintes'], 1)
        self.assertIn('Diretor', d['vinculos_resumo'])

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_p_da_silva_conference_has_federal_220_and_no_fgts_obligation(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / 'axiom_tools.db'
            shutil.copy2(SOURCE_DB, db)
            con = sqlite3.connect(db); con.row_factory = sqlite3.Row
            dados = conferencia_competencia(con, '08/2026', 'P da Silva Carmo', '', 'TODAS')
            linha = next(x for x in dados['linhas'] if x['cliente_id'] == 636)
            self.assertEqual(linha['checks']['inss']['status'], 'CONFERIDO')
            self.assertAlmostEqual(linha['checks']['inss']['esperado'], 220.0)
            self.assertAlmostEqual(linha['checks']['inss']['previdenciario_darf'], 220.0)
            self.assertFalse(linha['exibir_fgts'])
            self.assertEqual(linha['checks']['fgts']['status'], 'NAO_APLICAVEL')
            con.close()


if __name__ == '__main__':
    unittest.main()
