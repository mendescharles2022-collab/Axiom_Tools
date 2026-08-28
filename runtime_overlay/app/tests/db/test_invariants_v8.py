from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from axiom_tools.db.invariants_v8 import auditar_invariantes
from axiom_tools.modules.printing.service import garantir_schema

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


@unittest.skipUnless(SOURCE_DB.exists(), 'snapshot canônico real indisponível')
class InvariantesBancoV8Tests(unittest.TestCase):
    def _copy(self):
        td = tempfile.TemporaryDirectory()
        db = Path(td.name) / 'axiom_tools.db'
        shutil.copy2(SOURCE_DB, db)
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        return td, con

    def test_auditor_detecta_orfandade_logica_de_impressao_pre_migracao(self):
        td, con = self._copy()
        try:
            rel = auditar_invariantes(con)
            self.assertEqual(rel['integrity_check'], ['ok'])
            self.assertEqual(rel['foreign_key_violations'], 0)
            imp = next(x for x in rel['invariantes_logicas'] if x['codigo'] == 'IMP_SNAPSHOT')
            self.assertEqual(imp['violacoes'], 200)
            self.assertFalse(rel['ok'])
        finally:
            con.close(); td.cleanup()

    def test_migracao_preserva_evidencia_e_zera_violacoes_bloqueantes(self):
        td, con = self._copy()
        try:
            garantir_schema(con)
            rel = auditar_invariantes(con)
            self.assertTrue(rel['ok'])
            self.assertEqual(rel['integrity_check'], ['ok'])
            self.assertEqual(rel['foreign_key_violations'], 0)
            self.assertEqual(rel['logical_blocking_violations'], 0)
            total = con.execute('SELECT COUNT(*) FROM processamento_impressao_item').fetchone()[0]
            snapshots = con.execute("SELECT COUNT(*) FROM processamento_impressao_item WHERE snapshot_json IS NOT NULL AND TRIM(snapshot_json)<>''").fetchone()[0]
            self.assertEqual((snapshots, total), (414, 414))
            origens = {}
            for (raw,) in con.execute('SELECT snapshot_json FROM processamento_impressao_item'):
                origem = json.loads(raw)['origem_snapshot']
                origens[origem] = origens.get(origem, 0) + 1
            self.assertEqual(origens['HISTORICO_REPROCESSAMENTO'], 200)
            self.assertEqual(origens['PROCESSAMENTO_VIGENTE_NO_MOMENTO_DA_IMPRESSAO'], 214)
        finally:
            con.close(); td.cleanup()


if __name__ == '__main__':
    unittest.main()
