from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.modules.processing.conference import _agregar_decisoes_fontes, _check_dae_mei, conferencia_competencia
from axiom_tools.modules.processing.operations import salvar_conferencia_fonte

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


class ApplicabilityFgtsMeiV8Tests(unittest.TestCase):
    def test_mei_dae_combines_previdenciario_and_fgts(self):
        check = _check_dae_mei(
            {"darf_folha_esperado": 170.20, "fgts_total": 129.68},
            {"valor_total": 299.88},
        )
        self.assertEqual(check["status"], "CONFERIDO")
        self.assertAlmostEqual(check["esperado"], 299.88)
        self.assertAlmostEqual(check["diferenca"], 0.0)

    def test_mei_source_is_dae_not_darf_plus_fgts(self):
        checks = {
            "inss": {"status": "NAO_APLICAVEL"},
            "dae": {"status": "DIVERGENTE"},
            "fgts": {"status": "NAO_APLICAVEL"},
            "econsignado": {"status": "NAO_APLICAVEL"},
        }
        agregado, detalhe = _agregar_decisoes_fontes(
            checks, {"DAE": {"status_manual": "JUSTIFICADO"}},
            exibir_fgts=False, exibir_econsignado=False, exibir_dae=True,
        )
        self.assertEqual(agregado, "JUSTIFICADO")
        self.assertEqual(set(detalhe), {"DAE"})

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_elenice_mei_uses_unified_dae(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / 'axiom_tools.db'; shutil.copy2(SOURCE_DB, db)
            con = sqlite3.connect(db); con.row_factory = sqlite3.Row
            dados = conferencia_competencia(con, '08/2026', 'Elenice Batista', '', 'TODAS')
            linha = next(x for x in dados['linhas'] if x['cliente_id'] == 270)
            self.assertTrue(linha['perfil_mei'])
            self.assertTrue(linha['exibir_dae'])
            self.assertFalse(linha['exibir_fgts'])
            self.assertEqual(linha['checks']['dae']['status'], 'CONFERIDO')
            self.assertAlmostEqual(linha['dae_esperado'], 299.88)
            self.assertAlmostEqual(linha['dae'], 299.88)
            self.assertEqual(set(linha['status_fontes']), {'DAE'})
            con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_larissa_b_fgts_zero_is_not_missing_gfd(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / 'axiom_tools.db'; shutil.copy2(SOURCE_DB, db)
            con = sqlite3.connect(db); con.row_factory = sqlite3.Row
            dados = conferencia_competencia(con, '08/2026', 'Larissa B Maia', '', 'TODAS')
            linha = next(x for x in dados['linhas'] if x['cliente_id'] == 498)
            self.assertFalse(linha['perfil_mei'])
            self.assertFalse(linha['exibir_dae'])
            self.assertFalse(linha['exibir_fgts'])
            self.assertEqual(linha['checks']['fgts']['status'], 'NAO_APLICAVEL')
            self.assertAlmostEqual(linha['fgts_dominio'], 0.0)
            con.close()

    def test_dae_is_valid_manual_source(self):
        con = sqlite3.connect(':memory:'); con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,documento TEXT,nome_apresentacao TEXT)")
        con.execute("INSERT INTO clientes(id,nome) VALUES(1,'MEI')")
        salvar_conferencia_fonte(con, '08/2026', 1, 'DAE', 'JUSTIFICADO', 'Conferido no eSocial')
        row = con.execute("SELECT fonte,status_manual FROM processamento_conferencia_fonte").fetchone()
        self.assertEqual((row['fonte'], row['status_manual']), ('DAE','JUSTIFICADO'))
        con.close()


if __name__ == '__main__':
    unittest.main()
