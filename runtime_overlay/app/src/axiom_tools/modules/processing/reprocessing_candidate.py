from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from typing import Callable


IMMUTABLE_FIELDS = {
    "id",
    "origem_id",
    "origem_nome",
    "caminho_origem",
    "nome_original",
    "sha256",
    "tamanho_bytes",
    "tipo_arquivo",
    "chave_processamento_id",
    "processado_em",
}


def _row_dict(row) -> dict:
    return dict(row) if row is not None else {}


def _canonical(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _snapshot_hash(data: dict) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def garantir_schema_candidato(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS processamento_reprocessamento_historico (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               processamento_id INTEGER NOT NULL,
               status_anterior TEXT,
               cliente_id_anterior INTEGER,
               competencia_anterior TEXT,
               confianca_anterior INTEGER,
               dados_json_anterior TEXT,
               reprocessado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
               evento TEXT NOT NULL DEFAULT 'REPROCESSAMENTO',
               resultado TEXT
           )"""
    )
    cols = {r[1] for r in con.execute("PRAGMA table_info(processamento_reprocessamento_historico)")}
    additions = {
        "snapshot_json": "TEXT",
        "base_snapshot_hash": "TEXT",
        "lote_candidato_id": "TEXT",
        "motivo_resultado": "TEXT",
    }
    for name, kind in additions.items():
        if name not in cols:
            con.execute(f'ALTER TABLE processamento_reprocessamento_historico ADD COLUMN "{name}" {kind}')
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_reproc_candidato_pid ON processamento_reprocessamento_historico(processamento_id,evento,resultado)"
    )
    con.commit()


def _identity_key(row: dict) -> tuple:
    return (
        row.get("origem_id"),
        row.get("caminho_origem"),
        row.get("sha256"),
    )


def _quality(row: dict) -> tuple[int, int, int]:
    rank = {"ERRO": 0, "REVISAO": 1, "PROCESSADO": 2}
    status = str(row.get("status") or "").upper()
    completude = int(row.get("completude") or 0)
    confianca = int(row.get("origem_confianca") or row.get("confianca") or 0)
    return rank.get(status, -1), completude, confianca


def decidir_promocao(base: dict, candidato: dict) -> tuple[bool, str]:
    if not candidato:
        return False, "CANDIDATO_AUSENTE"
    if _identity_key(base) != _identity_key(candidato):
        return False, "IDENTIDADE_FISICA_DIVERGENTE"

    for field in ("cliente_id", "competencia"):
        old = base.get(field)
        new = candidato.get(field)
        if old not in (None, "") and new != old:
            return False, f"{field.upper()}_REGREDIU"

    base_q = _quality(base)
    cand_q = _quality(candidato)
    if cand_q[0] < base_q[0]:
        return False, "STATUS_REGREDIU"
    if cand_q[1] < base_q[1]:
        return False, "COMPLETUDE_REGREDIU"
    if cand_q[2] < base_q[2] and cand_q[1] <= base_q[1]:
        return False, "CONFIANCA_REGREDIU"

    operational_base = {k: v for k, v in base.items() if k not in IMMUTABLE_FIELDS}
    operational_candidate = {k: v for k, v in candidato.items() if k not in IMMUTABLE_FIELDS}
    if _canonical(operational_base) == _canonical(operational_candidate):
        return False, "SEM_ALTERACAO"
    return True, "CANDIDATO_SUPERIOR_OU_EQUIVALENTE"


def registrar_candidato(
    con: sqlite3.Connection,
    *,
    processamento_id: int,
    candidato: dict,
    lote_candidato_id: str | None = None,
) -> int:
    garantir_schema_candidato(con)
    base_row = con.execute("SELECT * FROM processamento_arquivo WHERE id=?", (processamento_id,)).fetchone()
    if base_row is None:
        raise ValueError("processamento vigente não encontrado")
    base = _row_dict(base_row)
    lote = lote_candidato_id or uuid.uuid4().hex
    cur = con.execute(
        """INSERT INTO processamento_reprocessamento_historico
           (processamento_id,status_anterior,cliente_id_anterior,competencia_anterior,
            confianca_anterior,dados_json_anterior,evento,resultado,snapshot_json,
            base_snapshot_hash,lote_candidato_id)
           VALUES (?,?,?,?,?,?,'CANDIDATO','PENDENTE',?,?,?)""",
        (
            processamento_id,
            base.get("status"),
            base.get("cliente_id"),
            base.get("competencia"),
            base.get("origem_confianca") or base.get("confianca"),
            base.get("dados_json"),
            _canonical(candidato),
            _snapshot_hash(base),
            lote,
        ),
    )
    con.commit()
    return int(cur.lastrowid)


def promover_candidato(con: sqlite3.Connection, candidato_id: int) -> dict:
    garantir_schema_candidato(con)
    con.execute("BEGIN IMMEDIATE")
    try:
        hist = con.execute(
            "SELECT * FROM processamento_reprocessamento_historico WHERE id=? AND evento='CANDIDATO'",
            (candidato_id,),
        ).fetchone()
        if hist is None:
            raise ValueError("candidato não encontrado")
        if str(hist["resultado"] or "") != "PENDENTE":
            con.rollback()
            return {"ok": False, "resultado": hist["resultado"], "motivo": "CANDIDATO_JA_DECIDIDO"}

        pid = int(hist["processamento_id"])
        base_row = con.execute("SELECT * FROM processamento_arquivo WHERE id=?", (pid,)).fetchone()
        if base_row is None:
            raise ValueError("versão vigente não encontrada")
        base = _row_dict(base_row)
        if _snapshot_hash(base) != str(hist["base_snapshot_hash"] or ""):
            con.execute(
                "UPDATE processamento_reprocessamento_historico SET resultado='REJEITADO',motivo_resultado='BASE_ALTERADA' WHERE id=?",
                (candidato_id,),
            )
            con.commit()
            return {"ok": False, "resultado": "REJEITADO", "motivo": "BASE_ALTERADA"}

        candidato = json.loads(hist["snapshot_json"] or "{}")
        promover, motivo = decidir_promocao(base, candidato)
        if not promover:
            con.execute(
                "UPDATE processamento_reprocessamento_historico SET resultado='REJEITADO',motivo_resultado=? WHERE id=?",
                (motivo, candidato_id),
            )
            con.commit()
            return {"ok": False, "resultado": "REJEITADO", "motivo": motivo, "processamento_id": pid}

        con.execute(
            """INSERT INTO processamento_reprocessamento_historico
               (processamento_id,status_anterior,cliente_id_anterior,competencia_anterior,
                confianca_anterior,dados_json_anterior,evento,resultado,snapshot_json,
                base_snapshot_hash,lote_candidato_id,motivo_resultado)
               VALUES (?,?,?,?,?,?,'VERSAO_SUBSTITUIDA','PRESERVADA',?,?,?,?)""",
            (
                pid,
                base.get("status"),
                base.get("cliente_id"),
                base.get("competencia"),
                base.get("origem_confianca") or base.get("confianca"),
                base.get("dados_json"),
                _canonical(base),
                _snapshot_hash(base),
                hist["lote_candidato_id"],
                f"PROMOVIDA_POR_CANDIDATO_{candidato_id}",
            ),
        )

        columns = {r[1] for r in con.execute("PRAGMA table_info(processamento_arquivo)")}
        updates = {
            key: value
            for key, value in candidato.items()
            if key in columns and key not in IMMUTABLE_FIELDS
        }
        if not updates:
            raise ValueError("candidato não contém campos operacionais promovíveis")
        assignments = ",".join(f'"{key}"=?' for key in updates)
        con.execute(
            f'UPDATE processamento_arquivo SET {assignments} WHERE id=?',
            (*updates.values(), pid),
        )
        con.execute(
            "UPDATE processamento_reprocessamento_historico SET resultado='PROMOVIDO',motivo_resultado=? WHERE id=?",
            (motivo, candidato_id),
        )
        con.commit()
        return {"ok": True, "resultado": "PROMOVIDO", "motivo": motivo, "processamento_id": pid}
    except Exception:
        con.rollback()
        raise


def executar_candidato_em_clone(
    con: sqlite3.Connection,
    *,
    processamento_id: int,
    reprocessar_no_clone: Callable[[sqlite3.Connection, int], object],
) -> int:
    """Executa a lógica destrutiva antiga somente em clone e registra o resultado."""
    con.row_factory = sqlite3.Row
    base_row = con.execute("SELECT * FROM processamento_arquivo WHERE id=?", (processamento_id,)).fetchone()
    if base_row is None:
        raise ValueError("processamento vigente não encontrado")
    base = _row_dict(base_row)

    clone = sqlite3.connect(":memory:")
    clone.row_factory = sqlite3.Row
    try:
        con.backup(clone)
        reprocessar_no_clone(clone, processamento_id)
        key = _identity_key(base)
        candidato_row = clone.execute(
            """SELECT * FROM processamento_arquivo
               WHERE origem_id IS ? AND caminho_origem=? AND sha256=?
               ORDER BY id DESC LIMIT 1""",
            key,
        ).fetchone()
        if candidato_row is None:
            raise ValueError("reprocessamento isolado não produziu candidato compatível")
        return registrar_candidato(
            con,
            processamento_id=processamento_id,
            candidato=_row_dict(candidato_row),
        )
    finally:
        clone.close()


__all__ = [
    "decidir_promocao",
    "executar_candidato_em_clone",
    "garantir_schema_candidato",
    "promover_candidato",
    "registrar_candidato",
]
