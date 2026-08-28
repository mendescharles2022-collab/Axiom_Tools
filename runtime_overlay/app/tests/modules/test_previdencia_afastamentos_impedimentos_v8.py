from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.processing.conference import _agregar_decisoes_fontes, conferencia_competencia
from axiom_tools.modules.processing.operations import salvar_conferencia_fonte

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def real_line(busca: str, cliente_id: int):
    td = tempfile.TemporaryDirectory()
    db = Path(td.name) / 'axiom_tools.db'; shutil.copy2(SOURCE_DB, db)
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    dados = conferencia_competencia(con, '08/2026', busca, '', 'TODAS')
    linha = next(x for x in dados['linhas'] if x['cliente_id'] == cliente_id)
    return td, con, linha


class PrevidenciaAfastamentosImpedimentosV8Tests(unittest.TestCase):
    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_ponto_kent_deduction_derives_expected_previdenciario(self):
        td, con, linha = real_line('Ponto Kent', 659)
        try:
            self.assertAlmostEqual(linha['checks']['inss']['inss_esperado'], 758.37)
            self.assertAlmostEqual(linha['checks']['inss']['previdenciario_darf'], 758.37)
            self.assertEqual(linha['checks']['inss']['status'], 'CONFERIDO')
            self.assertEqual(linha['status_automatico'], 'CONFERIDO')
        finally:
            con.close(); td.cleanup()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_denes_family_salary_zeroes_darf_but_not_fgts(self):
        td, con, linha = real_line('Denes Mariano', 812)
        try:
            self.assertAlmostEqual(linha['checks']['inss']['inss_esperado'], 0.0)
            self.assertIn(linha['checks']['inss']['status'], {'AUSENCIA_JUSTIFICADA','NAO_APLICAVEL_ZERO'})
            self.assertEqual(linha['checks']['fgts']['status'], 'AUSENTE')
            self.assertEqual(linha['status_automatico'], 'INCOMPLETO')
        finally:
            con.close(); td.cleanup()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_zero_base_cases_are_not_fake_darf_pending(self):
        for busca, cid in [('Gold Pallace',368),('Marcos Augusto Pimentel',840),('Wilmar Ferreira',827)]:
            td, con, linha = real_line(busca, cid)
            try:
                self.assertEqual(linha['checks']['inss']['status'], 'NAO_APLICAVEL_ZERO', busca)
                self.assertAlmostEqual(linha['checks']['inss']['inss_esperado'], 0.0, msg=busca)
            finally:
                con.close(); td.cleanup()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_gl_auto_center_keeps_fgts_despite_zero_previdenciario(self):
        td, con, linha = real_line('GL Auto Center', 362)
        try:
            self.assertEqual(linha['checks']['inss']['status'], 'NAO_APLICAVEL_ZERO')
            self.assertTrue(linha['exibir_fgts'])
            self.assertEqual(linha['checks']['fgts']['status'], 'CONFERIDO')
            self.assertAlmostEqual(linha['fgts_dominio'], 194.24)
            self.assertAlmostEqual(linha['fgts_gfd'], 194.24)
        finally:
            con.close(); td.cleanup()

    def test_external_impediment_requires_observation(self):
        con = sqlite3.connect(':memory:'); con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,documento TEXT,nome_apresentacao TEXT)")
        con.execute("INSERT INTO clientes(id,nome) VALUES(1,'Cliente')")
        with self.assertRaises(ValueError):
            salvar_conferencia_fonte(con, '08/2026', 1, 'DARF', 'IMPEDIDA_EXTERNAMENTE', '')
        con.close()

    def test_external_darf_impediment_does_not_hide_fgts_divergence(self):
        checks={
            'inss': {'status':'DARF_AUSENTE_INESPERADO'},
            'dae': {'status':'NAO_APLICAVEL'},
            'fgts': {'status':'DIVERGENTE'},
            'econsignado': {'status':'NAO_APLICAVEL'},
        }
        agregado, detalhe = _agregar_decisoes_fontes(
            checks, {'DARF': {'status_manual':'IMPEDIDA_EXTERNAMENTE','observacao':'Procuração revogada'}},
            exibir_fgts=True, exibir_econsignado=False,
        )
        self.assertEqual(agregado, 'DIVERGENTE')
        self.assertEqual(detalhe['DARF']['final'], 'IMPEDIDA_EXTERNAMENTE')
        self.assertEqual(detalhe['FGTS']['final'], 'DIVERGENTE')

    def test_external_darf_impediment_can_resolve_only_when_other_sources_are_resolved(self):
        checks={
            'inss': {'status':'DARF_AUSENTE_INESPERADO'},
            'dae': {'status':'NAO_APLICAVEL'},
            'fgts': {'status':'CONFERIDO'},
            'econsignado': {'status':'NAO_APLICAVEL'},
        }
        agregado, _ = _agregar_decisoes_fontes(
            checks, {'DARF': {'status_manual':'IMPEDIDA_EXTERNAMENTE','observacao':'Procuração revogada'}},
            exibir_fgts=True, exibir_econsignado=False,
        )
        self.assertEqual(agregado, 'JUSTIFICADO')

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_casa_das_carnes_external_impediment_is_source_specific(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/'axiom_tools.db'; shutil.copy2(SOURCE_DB,db)
            con=sqlite3.connect(db); con.row_factory=sqlite3.Row
            salvar_conferencia_fonte(con,'08/2026',130,'DARF','IMPEDIDA_EXTERNAMENTE','Procuração expirada/revogada')
            dados=conferencia_competencia(con,'08/2026','Casa das Carnes','','TODAS')
            linha=next(x for x in dados['linhas'] if x['cliente_id']==130)
            self.assertEqual(linha['status_fontes']['DARF']['final'],'IMPEDIDA_EXTERNAMENTE')
            self.assertEqual(linha['status_automatico'],'JUSTIFICADO')
            self.assertFalse(linha['exibir_fgts'])
            con.close()


if __name__ == '__main__':
    unittest.main()
