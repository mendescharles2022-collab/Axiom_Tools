from __future__ import annotations

import json
import sqlite3
import unittest

from axiom_tools.modules.processing.reprocessing_candidate import (
    executar_candidato_em_clone,
    promover_candidato,
    registrar_candidato,
)


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE processamento_arquivo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem_id INTEGER,
            origem_nome TEXT NOT NULL DEFAULT 'UPLOAD_MANUAL',
            caminho_origem TEXT NOT NULL,
            nome_original TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            tamanho_bytes INTEGER NOT NULL DEFAULT 1,
            tipo_arquivo TEXT NOT NULL DEFAULT 'PDF',
            documento_tipo TEXT,
            cliente_id INTEGER,
            documento_cliente TEXT,
            competencia TEXT,
            status TEXT NOT NULL,
            confianca INTEGER NOT NULL DEFAULT 0,
            origem_confianca INTEGER NOT NULL DEFAULT 0,
            completude INTEGER NOT NULL DEFAULT 0,
            metodo_extracao TEXT,
            parser_versao TEXT,
            dados_json TEXT,
            erro TEXT,
            processado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(origem_id,caminho_origem,sha256)
        );
        """
    )
    return con


def insert_doc(
    con: sqlite3.Connection,
    *,
    pid: int,
    path: str,
    sha: str,
    cliente: int = 826,
    competencia: str = "08/2026",
    status: str = "PROCESSADO",
    completude: int = 100,
    confianca: int = 100,
    fgts: float = 0,
    federal: float = 0,
) -> None:
    dados = json.dumps({"fgts": fgts, "federal": federal})
    con.execute(
        """INSERT INTO processamento_arquivo
           (id,origem_id,caminho_origem,nome_original,sha256,documento_tipo,
            cliente_id,competencia,status,confianca,origem_confianca,completude,
            parser_versao,dados_json)
           VALUES(?,1,?,?,?,'EXTRATO_MENSAL',?,?,?,?,?,?,?,?)""",
        (
            pid,
            path,
            path,
            sha,
            cliente,
            competencia,
            status,
            confianca,
            confianca,
            completude,
            "OLD",
            dados,
        ),
    )
    con.commit()


def destructive_reprocess(*, status="REVISAO", completude=90, confianca=90, cliente=826, competencia="08/2026"):
    def _run(con: sqlite3.Connection, pid: int):
        old = con.execute("SELECT * FROM processamento_arquivo WHERE id=?", (pid,)).fetchone()
        values = dict(old)
        con.execute("DELETE FROM processamento_arquivo WHERE id=?", (pid,))
        con.execute(
            """INSERT INTO processamento_arquivo
               (origem_id,caminho_origem,nome_original,sha256,documento_tipo,
                cliente_id,competencia,status,confianca,origem_confianca,completude,
                parser_versao,dados_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                values["origem_id"], values["caminho_origem"], values["nome_original"],
                values["sha256"], values["documento_tipo"], cliente, competencia,
                status, confianca, confianca, completude, "NEW", values["dados_json"],
            ),
        )
        con.commit()
    return _run


class ReprocessingCandidateV8Tests(unittest.TestCase):
    def test_destructive_reprocessing_runs_only_in_clone(self):
        con = make_con()
        insert_doc(con, pid=449, path="449.pdf", sha="a" * 64)
        cid = executar_candidato_em_clone(
            con,
            processamento_id=449,
            reprocessar_no_clone=destructive_reprocess(),
        )
        live = con.execute("SELECT * FROM processamento_arquivo WHERE id=449").fetchone()
        self.assertEqual(live["status"], "PROCESSADO")
        self.assertEqual(live["completude"], 100)
        self.assertEqual(live["parser_versao"], "OLD")
        candidate = con.execute(
            "SELECT evento,resultado FROM processamento_reprocessamento_historico WHERE id=?",
            (cid,),
        ).fetchone()
        self.assertEqual(tuple(candidate), ("CANDIDATO", "PENDENTE"))
        con.close()

    def test_jair_449_and_450_bad_candidates_are_rejected_without_data_loss(self):
        con = make_con()
        insert_doc(con, pid=449, path="449.pdf", sha="a" * 64, fgts=129.68, federal=511.43)
        insert_doc(con, pid=450, path="450.pdf", sha="b" * 64, fgts=259.36, federal=511.43)
        for pid in (449, 450):
            cid = executar_candidato_em_clone(
                con,
                processamento_id=pid,
                reprocessar_no_clone=destructive_reprocess(status="REVISAO", completude=90),
            )
            result = promover_candidato(con, cid)
            self.assertFalse(result["ok"])
            self.assertEqual(result["motivo"], "STATUS_REGREDIU")

        rows = con.execute("SELECT * FROM processamento_arquivo WHERE id IN (449,450) ORDER BY id").fetchall()
        self.assertEqual([r["status"] for r in rows], ["PROCESSADO", "PROCESSADO"])
        self.assertEqual([r["completude"] for r in rows], [100, 100])
        fgts = sum(json.loads(r["dados_json"])["fgts"] for r in rows)
        federais = {json.loads(r["dados_json"])["federal"] for r in rows}
        self.assertAlmostEqual(fgts, 389.04, places=2)
        self.assertEqual(federais, {511.43})
        con.close()

    def test_candidate_that_loses_client_is_rejected(self):
        con = make_con()
        insert_doc(con, pid=1, path="x.pdf", sha="c" * 64)
        cid = executar_candidato_em_clone(
            con,
            processamento_id=1,
            reprocessar_no_clone=destructive_reprocess(status="PROCESSADO", completude=100, cliente=None),
        )
        result = promover_candidato(con, cid)
        self.assertEqual(result["motivo"], "CLIENTE_ID_REGREDIU")
        self.assertEqual(con.execute("SELECT cliente_id FROM processamento_arquivo WHERE id=1").fetchone()[0], 826)
        con.close()

    def test_equal_or_better_candidate_is_promoted_in_place(self):
        con = make_con()
        insert_doc(con, pid=1, path="x.pdf", sha="d" * 64, completude=95, confianca=90)
        cid = executar_candidato_em_clone(
            con,
            processamento_id=1,
            reprocessar_no_clone=destructive_reprocess(status="PROCESSADO", completude=100, confianca=100),
        )
        result = promover_candidato(con, cid)
        self.assertTrue(result["ok"])
        current = con.execute("SELECT * FROM processamento_arquivo WHERE id=1").fetchone()
        self.assertEqual(current["id"], 1)
        self.assertEqual(current["completude"], 100)
        self.assertEqual(current["parser_versao"], "NEW")
        old = con.execute(
            "SELECT snapshot_json FROM processamento_reprocessamento_historico WHERE evento='VERSAO_SUBSTITUIDA'"
        ).fetchone()
        self.assertEqual(json.loads(old[0])["parser_versao"], "OLD")
        con.close()

    def test_concurrent_change_blocks_stale_candidate(self):
        con = make_con()
        insert_doc(con, pid=1, path="x.pdf", sha="e" * 64, completude=90, confianca=90)
        base = dict(con.execute("SELECT * FROM processamento_arquivo WHERE id=1").fetchone())
        candidate = dict(base)
        candidate.update(completude=100, confianca=100, origem_confianca=100, parser_versao="NEW")
        cid = registrar_candidato(con, processamento_id=1, candidato=candidate)
        con.execute("UPDATE processamento_arquivo SET dados_json='{}' WHERE id=1")
        con.commit()
        result = promover_candidato(con, cid)
        self.assertFalse(result["ok"])
        self.assertEqual(result["motivo"], "BASE_ALTERADA")
        self.assertEqual(con.execute("SELECT parser_versao FROM processamento_arquivo WHERE id=1").fetchone()[0], "OLD")
        con.close()

    def test_candidate_decision_is_idempotent(self):
        con = make_con()
        insert_doc(con, pid=1, path="x.pdf", sha="f" * 64, completude=95, confianca=95)
        cid = executar_candidato_em_clone(
            con,
            processamento_id=1,
            reprocessar_no_clone=destructive_reprocess(status="PROCESSADO", completude=100, confianca=100),
        )
        first = promover_candidato(con, cid)
        second = promover_candidato(con, cid)
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["motivo"], "CANDIDATO_JA_DECIDIDO")
        con.close()


if __name__ == "__main__":
    unittest.main()
