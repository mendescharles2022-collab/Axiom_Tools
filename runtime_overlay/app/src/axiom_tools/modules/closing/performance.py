from __future__ import annotations

import sqlite3


INDEX_SPECS = (
    (
        "idx_v8_fechamento_comp_status_chamada_mov",
        "fechamento_mensal_cliente",
        ("competencia", "status", "chamada", "movimento_competencia", "cliente_id"),
    ),
    (
        "idx_v8_fechamento_cliente_comp",
        "fechamento_mensal_cliente",
        ("cliente_id", "competencia"),
    ),
    (
        "idx_v8_processamento_cliente_comp_tipo_vigente",
        "processamento_arquivo",
        ("cliente_id", "competencia", "documento_tipo", "documento_vigente", "status"),
    ),
    (
        "idx_v8_retificacao_cliente_comp_status",
        "fechamento_mensal_retificacao",
        ("cliente_id", "competencia", "status"),
    ),
)


def _table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    exists = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if exists is None:
        return set()
    return {str(row[1]) for row in con.execute(f'PRAGMA table_info("{table}")')}


def garantir_indices_escala(con: sqlite3.Connection) -> dict[str, list[str]]:
    """Cria apenas índices compatíveis com o schema realmente presente.

    O helper é idempotente e seguro para migração progressiva: tabelas/colunas ainda
    inexistentes são registradas como ignoradas, nunca inventadas.
    """
    created: list[str] = []
    skipped: list[str] = []
    existing = {
        str(row[0])
        for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_v8_%'"
        )
    }

    for name, table, columns in INDEX_SPECS:
        available = _table_columns(con, table)
        if not set(columns).issubset(available):
            skipped.append(name)
            continue
        quoted = ", ".join(f'"{column}"' for column in columns)
        con.execute(f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" ({quoted})')
        if name not in existing:
            created.append(name)

    return {"created": created, "skipped": skipped}


__all__ = ["INDEX_SPECS", "garantir_indices_escala"]
