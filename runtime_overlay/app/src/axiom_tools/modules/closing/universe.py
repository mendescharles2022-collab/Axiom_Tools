from __future__ import annotations

import sqlite3


def _perfil_ativo_clause() -> str:
    return "(NOT EXISTS (SELECT 1 FROM fechamento_cliente_perfil) OR COALESCE(fp.participa_ciclo,0)=1)"


def _ids(con: sqlite3.Connection, sql: str, params: tuple[object, ...]) -> set[int]:
    return {int(row[0]) for row in con.execute(sql, params).fetchall()}


def clientes_participantes_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Composição mensal efetiva, independente da etapa atual do cliente."""
    return _ids(
        con,
        f"""SELECT f.cliente_id
            FROM fechamento_mensal_cliente f
            LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
            WHERE f.competencia=? AND {_perfil_ativo_clause()}""",
        (competencia,),
    )


def clientes_chamada_atual_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Clientes com movimento liberados na chamada operacional corrente."""
    return _ids(
        con,
        f"""SELECT f.cliente_id
            FROM fechamento_mensal_cliente f
            JOIN fechamento_mensal fm ON fm.competencia=f.competencia
            LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
            WHERE f.competencia=?
              AND f.status='PRONTA'
              AND f.chamada=fm.chamada_atual
              AND f.movimento_competencia='COM_MOVIMENTO'
              AND {_perfil_ativo_clause()}""",
        (competencia,),
    )


def clientes_retificacao_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Clientes em retificação ativa; possuem fluxo próprio de conferência."""
    return _ids(
        con,
        f"""SELECT f.cliente_id
            FROM fechamento_mensal_cliente f
            LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
            WHERE f.competencia=?
              AND f.status='RETIFICACAO'
              AND {_perfil_ativo_clause()}""",
        (competencia,),
    )


def clientes_conferencia_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Mesa viva da chamada atual. Retificações possuem fluxo próprio."""
    return clientes_chamada_atual_ids(con, competencia)


def clientes_fechados_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Clientes efetivamente fechados da composição mensal."""
    return _ids(
        con,
        f"""SELECT f.cliente_id
            FROM fechamento_mensal_cliente f
            LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
            WHERE f.competencia=?
              AND f.status='FECHADA'
              AND {_perfil_ativo_clause()}""",
        (competencia,),
    )


def clientes_chamada_futura_ids(con: sqlite3.Connection, competencia: str) -> set[int]:
    """Clientes adiados para chamada posterior à atual."""
    return _ids(
        con,
        f"""SELECT f.cliente_id
            FROM fechamento_mensal_cliente f
            JOIN fechamento_mensal fm ON fm.competencia=f.competencia
            LEFT JOIN fechamento_cliente_perfil fp ON fp.cliente_id=f.cliente_id
            WHERE f.competencia=?
              AND f.status='ADIADA'
              AND f.chamada>fm.chamada_atual
              AND {_perfil_ativo_clause()}""",
        (competencia,),
    )


__all__ = [
    "clientes_participantes_ids",
    "clientes_chamada_atual_ids",
    "clientes_retificacao_ids",
    "clientes_conferencia_ids",
    "clientes_fechados_ids",
    "clientes_chamada_futura_ids",
]
