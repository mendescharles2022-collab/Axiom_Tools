from __future__ import annotations

import sqlite3
from typing import Iterable


AUTORIZADO = "AUTORIZADO"
FECHAMENTO_AUSENTE = "FECHAMENTO_AUSENTE"
CLIENTE_NAO_FECHADO = "CLIENTE_NAO_FECHADO"
VERSAO_FECHAMENTO_INVALIDA = "VERSAO_FECHAMENTO_INVALIDA"
RETIFICACAO_PENDENTE = "RETIFICACAO_PENDENTE"
DOCUMENTO_FORA_DO_ESCOPO = "DOCUMENTO_FORA_DO_ESCOPO"


def _decision(*, autorizado: bool, motivo: str, cliente_id: int, competencia: str, **extra) -> dict:
    payload = {
        "autorizado": bool(autorizado),
        "motivo": motivo,
        "cliente_id": int(cliente_id),
        "competencia": str(competencia),
    }
    payload.update(extra)
    return payload


def autorizar_saida_cliente(
    con: sqlite3.Connection,
    *,
    cliente_id: int,
    competencia: str,
) -> dict:
    """Gate canônico mínimo para qualquer saída operacional V8.

    A decisão é deliberadamente de backend e não depende de filtros de UI.
    FECHADA representa que as obrigações aplicáveis já passaram pelo fechamento;
    este gate ainda exige a versão fechada vigente e ausência de retificação material.
    """
    row = con.execute(
        """
        SELECT status, versao_atual
          FROM fechamento_mensal_cliente
         WHERE competencia=? AND cliente_id=?
         LIMIT 1
        """,
        (competencia, cliente_id),
    ).fetchone()

    if row is None:
        return _decision(
            autorizado=False,
            motivo=FECHAMENTO_AUSENTE,
            cliente_id=cliente_id,
            competencia=competencia,
        )

    status = str(row[0] or "").strip().upper()
    versao_atual = row[1]
    if status != "FECHADA":
        return _decision(
            autorizado=False,
            motivo=CLIENTE_NAO_FECHADO,
            cliente_id=cliente_id,
            competencia=competencia,
            estado=status or None,
        )

    if versao_atual is None:
        return _decision(
            autorizado=False,
            motivo=VERSAO_FECHAMENTO_INVALIDA,
            cliente_id=cliente_id,
            competencia=competencia,
            estado=status,
        )

    versao = con.execute(
        """
        SELECT 1
          FROM fechamento_mensal_versao
         WHERE competencia=? AND cliente_id=? AND versao=?
         LIMIT 1
        """,
        (competencia, cliente_id, versao_atual),
    ).fetchone()
    if versao is None:
        return _decision(
            autorizado=False,
            motivo=VERSAO_FECHAMENTO_INVALIDA,
            cliente_id=cliente_id,
            competencia=competencia,
            estado=status,
            versao_atual=versao_atual,
        )

    retificacao = con.execute(
        """
        SELECT 1
          FROM fechamento_mensal_retificacao
         WHERE competencia=? AND cliente_id=? AND UPPER(COALESCE(status,''))='DETECTADA'
         LIMIT 1
        """,
        (competencia, cliente_id),
    ).fetchone()
    if retificacao is not None:
        return _decision(
            autorizado=False,
            motivo=RETIFICACAO_PENDENTE,
            cliente_id=cliente_id,
            competencia=competencia,
            estado=status,
            versao_atual=versao_atual,
        )

    return _decision(
        autorizado=True,
        motivo=AUTORIZADO,
        cliente_id=cliente_id,
        competencia=competencia,
        estado=status,
        versao_atual=versao_atual,
    )


def filtrar_documentos_autorizados(
    con: sqlite3.Connection,
    *,
    cliente_id: int,
    competencia: str,
    documento_ids: Iterable[int],
) -> dict:
    """Revalida uma seleção explícita de IDs no backend.

    IDs de outro cliente, competência ou versão documental são rejeitados mesmo
    quando vieram de uma tela previamente filtrada.
    """
    ids = sorted({int(value) for value in documento_ids})
    base = autorizar_saida_cliente(
        con,
        cliente_id=cliente_id,
        competencia=competencia,
    )
    if not base["autorizado"]:
        return {
            **base,
            "documentos_solicitados": ids,
            "documentos_autorizados": [],
            "documentos_rejeitados": ids,
        }

    if not ids:
        return {
            **base,
            "documentos_solicitados": [],
            "documentos_autorizados": [],
            "documentos_rejeitados": [],
        }

    placeholders = ",".join("?" for _ in ids)
    rows = con.execute(
        f"""
        SELECT id
          FROM processamento_arquivo
         WHERE id IN ({placeholders})
           AND cliente_id=?
           AND competencia=?
           AND COALESCE(documento_vigente,1)=1
        """,
        (*ids, cliente_id, competencia),
    ).fetchall()
    permitidos = sorted({int(row[0]) for row in rows})
    permitidos_set = set(permitidos)
    rejeitados = [doc_id for doc_id in ids if doc_id not in permitidos_set]

    return {
        **base,
        "documentos_solicitados": ids,
        "documentos_autorizados": permitidos,
        "documentos_rejeitados": rejeitados,
        "selecao_integralmente_autorizada": not rejeitados,
        "motivo_selecao": AUTORIZADO if not rejeitados else DOCUMENTO_FORA_DO_ESCOPO,
    }
