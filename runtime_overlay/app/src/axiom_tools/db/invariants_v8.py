"""Auditoria V8 de integridade física, referencial e lógica do SQLite."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class LogicalCheck:
    codigo: str
    descricao: str
    sql: str
    bloqueante: bool = True


CHECKS = (
    LogicalCheck("CLI_INSCR_ORFA", "Inscrição v2 sem cliente", """
        SELECT i.id,i.cliente_id,i.tipo,i.numero
        FROM cliente_inscricoes_v2 i LEFT JOIN clientes c ON c.id=i.cliente_id
        WHERE c.id IS NULL
    """),
    LogicalCheck("CLI_MATRIZ_ORFA", "Filial aponta para matriz inexistente", """
        SELECT c.id,c.nome,c.matriz_cliente_id
        FROM clientes c LEFT JOIN clientes m ON m.id=c.matriz_cliente_id
        WHERE c.matriz_cliente_id IS NOT NULL AND m.id IS NULL
    """),
    LogicalCheck("FEC_COMP_ORFA", "Fechamento cliente sem competência de controle", """
        SELECT f.id,f.competencia,f.cliente_id
        FROM fechamento_mensal_cliente f LEFT JOIN fechamento_mensal m ON m.competencia=f.competencia
        WHERE m.competencia IS NULL
    """),
    LogicalCheck("FEC_CLIENTE_ORFA", "Fechamento aponta para cliente inexistente", """
        SELECT f.id,f.competencia,f.cliente_id
        FROM fechamento_mensal_cliente f LEFT JOIN clientes c ON c.id=f.cliente_id
        WHERE c.id IS NULL
    """),
    LogicalCheck("FEC_CHAMADA_INVALIDA", "Chamada incompatível com competência/status", """
        SELECT f.id,f.competencia,f.cliente_id,f.chamada,m.chamada_atual,f.status
        FROM fechamento_mensal_cliente f JOIN fechamento_mensal m ON m.competencia=f.competencia
        WHERE f.chamada<1 OR (f.status<>'ADIADA' AND f.chamada>m.chamada_atual)
    """),
    LogicalCheck("FEC_VERSAO_ATUAL_ORFA", "versao_atual sem versão correspondente", """
        SELECT f.id,f.competencia,f.cliente_id,f.status,f.versao_atual
        FROM fechamento_mensal_cliente f
        LEFT JOIN fechamento_mensal_versao v
          ON v.competencia=f.competencia AND v.cliente_id=f.cliente_id AND v.versao=f.versao_atual
        WHERE f.versao_atual>0 AND v.id IS NULL
    """),
    LogicalCheck("FEC_FECHADA_SEM_VERSAO", "FECHADA sem snapshot/versionamento", """
        SELECT id,competencia,cliente_id,status,versao_atual
        FROM fechamento_mensal_cliente
        WHERE status='FECHADA' AND versao_atual<=0
    """),
    LogicalCheck("FEC_RETIF_SEM_REGISTRO", "RETIFICACAO sem registro DETECTADA", """
        SELECT f.id,f.competencia,f.cliente_id,f.versao_atual
        FROM fechamento_mensal_cliente f
        LEFT JOIN fechamento_mensal_retificacao r
          ON r.competencia=f.competencia AND r.cliente_id=f.cliente_id AND r.status='DETECTADA'
        WHERE f.status='RETIFICACAO' AND r.id IS NULL
    """),
    LogicalCheck("FEC_RETIF_BASE_ORFA", "Retificação aponta para versão base inexistente", """
        SELECT r.id,r.competencia,r.cliente_id,r.base_versao,r.status
        FROM fechamento_mensal_retificacao r
        LEFT JOIN fechamento_mensal_versao v
          ON v.competencia=r.competencia AND v.cliente_id=r.cliente_id AND v.versao=r.base_versao
        WHERE v.id IS NULL
    """),
    LogicalCheck("FEC_ADIADA_LIBERADA", "ADIADA pertence à chamada atual/anterior", """
        SELECT f.id,f.competencia,f.cliente_id,f.chamada,m.chamada_atual
        FROM fechamento_mensal_cliente f JOIN fechamento_mensal m ON m.competencia=f.competencia
        WHERE f.status='ADIADA' AND f.chamada<=m.chamada_atual
    """),
    LogicalCheck("FEC_RETIF_DUPLICADA", "Mais de uma retificação DETECTADA por cliente/competência", """
        SELECT competencia,cliente_id,COUNT(*) qtd
        FROM fechamento_mensal_retificacao WHERE status='DETECTADA'
        GROUP BY competencia,cliente_id HAVING COUNT(*)>1
    """),
    LogicalCheck("VER_CLIENTE_ORFA", "Versão de fechamento sem cliente", """
        SELECT v.id,v.competencia,v.cliente_id,v.versao
        FROM fechamento_mensal_versao v LEFT JOIN clientes c ON c.id=v.cliente_id
        WHERE c.id IS NULL
    """),
    LogicalCheck("VER_FECHAMENTO_ORFA", "Versão sem fechamento mensal cliente", """
        SELECT v.id,v.competencia,v.cliente_id,v.versao
        FROM fechamento_mensal_versao v
        LEFT JOIN fechamento_mensal_cliente f ON f.competencia=v.competencia AND f.cliente_id=v.cliente_id
        WHERE f.id IS NULL
    """),
    LogicalCheck("VER_ACIMA_ATUAL", "Versão histórica acima de versao_atual", """
        SELECT v.id,v.competencia,v.cliente_id,v.versao,f.versao_atual
        FROM fechamento_mensal_versao v
        JOIN fechamento_mensal_cliente f ON f.competencia=v.competencia AND f.cliente_id=v.cliente_id
        WHERE v.versao>f.versao_atual
    """),
    LogicalCheck("VER_LACUNA", "Numeração de versões não monotônica/contígua", """
        WITH seq AS (
          SELECT competencia,cliente_id,MIN(versao) mn,MAX(versao) mx,COUNT(*) qtd
          FROM fechamento_mensal_versao GROUP BY competencia,cliente_id
        )
        SELECT * FROM seq WHERE mn<>1 OR qtd<>mx
    """),
    LogicalCheck("PROC_CLIENTE_ORFA", "Processamento com cliente_id inexistente", """
        SELECT p.id,p.cliente_id,p.competencia,p.documento_tipo,p.status
        FROM processamento_arquivo p LEFT JOIN clientes c ON c.id=p.cliente_id
        WHERE p.cliente_id IS NOT NULL AND c.id IS NULL
    """),
    LogicalCheck("PROC_SUPERADO_ORFA", "superado_por_id aponta para processamento inexistente", """
        SELECT p.id,p.superado_por_id
        FROM processamento_arquivo p LEFT JOIN processamento_arquivo n ON n.id=p.superado_por_id
        WHERE p.superado_por_id IS NOT NULL AND n.id IS NULL
    """),
    LogicalCheck("PROC_VIGENTE_SUPERADO", "Documento vigente já marcado como superado", """
        SELECT id,superado_por_id,documento_vigente,versao_status
        FROM processamento_arquivo WHERE documento_vigente=1 AND superado_por_id IS NOT NULL
    """),
    LogicalCheck("CONS_CONSULTA_JOB_ORFA", "Consulta eConsignado sem job", """
        SELECT q.id,q.job_id,q.cliente_id
        FROM processamento_consignado_consulta q
        LEFT JOIN processamento_consignado_job j ON j.id=q.job_id
        WHERE j.id IS NULL
    """),
    LogicalCheck("CONS_CONSULTA_CLIENTE_ORFA", "Consulta eConsignado com cliente inexistente", """
        SELECT q.id,q.job_id,q.cliente_id
        FROM processamento_consignado_consulta q LEFT JOIN clientes c ON c.id=q.cliente_id
        WHERE q.cliente_id IS NOT NULL AND c.id IS NULL
    """),
    LogicalCheck("CONS_SNAPSHOT_CLIENTE_ORFA", "Snapshot eConsignado com cliente inexistente", """
        SELECT s.id,s.competencia,s.cliente_id,s.contrato
        FROM processamento_consignado_snapshot s LEFT JOIN clientes c ON c.id=s.cliente_id
        WHERE s.cliente_id IS NOT NULL AND c.id IS NULL
    """),
    LogicalCheck("CONS_DUP_JOB_EMPREGADOR", "Empregador duplicado no mesmo job", """
        SELECT job_id,empregador_tipo,empregador_inscricao,COUNT(*) qtd
        FROM processamento_consignado_consulta
        GROUP BY job_id,empregador_tipo,empregador_inscricao HAVING COUNT(*)>1
    """),
    LogicalCheck("CONS_DUP_CONTRATO", "Contrato eConsignado duplicado na mesma fotografia", """
        SELECT competencia,COALESCE(cliente_id,-1) cliente_id,COALESCE(cpf,'') cpf,
               COALESCE(contrato,'') contrato,COUNT(*) qtd
        FROM processamento_consignado_snapshot
        GROUP BY competencia,COALESCE(cliente_id,-1),COALESCE(cpf,''),COALESCE(contrato,'')
        HAVING COUNT(*)>1
    """),
)


def _tabela_existe(con: sqlite3.Connection, tabela: str) -> bool:
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabela,)
    ).fetchone() is not None


def _rows_dict(rows) -> list[dict]:
    result=[]
    for row in rows:
        if hasattr(row, "keys"):
            result.append({k: row[k] for k in row.keys()})
        else:
            result.append({str(i): value for i, value in enumerate(row)})
    return result


def _audit_impressao(con: sqlite3.Connection) -> dict:
    if not _tabela_existe(con, "processamento_impressao_item"):
        return {"codigo": "IMP_SNAPSHOT", "violacoes": 0, "amostra": [], "bloqueante": True}
    cols={str(r[1]) for r in con.execute("PRAGMA table_info(processamento_impressao_item)").fetchall()}
    tem_snapshot="snapshot_json" in cols
    if tem_snapshot:
        sql="""
          SELECT i.impressao_id,i.processamento_id,i.ordem
          FROM processamento_impressao_item i
          LEFT JOIN processamento_arquivo p ON p.id=i.processamento_id
          WHERE p.id IS NULL AND (i.snapshot_json IS NULL OR TRIM(i.snapshot_json)='')
        """
    else:
        sql="""
          SELECT i.impressao_id,i.processamento_id,i.ordem
          FROM processamento_impressao_item i
          LEFT JOIN processamento_arquivo p ON p.id=i.processamento_id
          WHERE p.id IS NULL
        """
    rows=con.execute(sql).fetchall()
    resolvidas=0
    if tem_snapshot:
        resolvidas=int(con.execute("""
          SELECT COUNT(*) FROM processamento_impressao_item i
          LEFT JOIN processamento_arquivo p ON p.id=i.processamento_id
          WHERE p.id IS NULL AND i.snapshot_json IS NOT NULL AND TRIM(i.snapshot_json)<>''
        """).fetchone()[0])
    return {
        "codigo": "IMP_SNAPSHOT",
        "descricao": "Item de impressão sem registro vivo precisa de snapshot histórico imutável",
        "violacoes": len(rows),
        "referencias_historicas_resolvidas": resolvidas,
        "amostra": _rows_dict(rows[:10]),
        "bloqueante": True,
    }


def auditar_invariantes(con: sqlite3.Connection) -> dict:
    integrity=[str(r[0]) for r in con.execute("PRAGMA integrity_check").fetchall()]
    fk_rows=con.execute("PRAGMA foreign_key_check").fetchall()
    resultados=[]
    for check in CHECKS:
        try:
            rows=con.execute(check.sql).fetchall()
            resultados.append({
                "codigo": check.codigo,
                "descricao": check.descricao,
                "violacoes": len(rows),
                "amostra": _rows_dict(rows[:10]),
                "bloqueante": check.bloqueante,
            })
        except sqlite3.OperationalError as exc:
            resultados.append({
                "codigo": check.codigo,
                "descricao": check.descricao,
                "violacoes": 1,
                "amostra": [{"erro": str(exc)}],
                "bloqueante": True,
            })
    resultados.append(_audit_impressao(con))
    logical_blocking=sum(x["violacoes"] for x in resultados if x.get("bloqueante"))
    return {
        "integrity_check": integrity,
        "integrity_ok": integrity == ["ok"],
        "foreign_key_check": _rows_dict(fk_rows),
        "foreign_key_violations": len(fk_rows),
        "invariantes_logicas": resultados,
        "logical_blocking_violations": logical_blocking,
        "ok": integrity == ["ok"] and not fk_rows and logical_blocking == 0,
    }
