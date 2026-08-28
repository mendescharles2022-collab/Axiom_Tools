"""Proveniência temporal canônica da competência V8.

Competência é dado de negócio. Este módulo normaliza a origem lógica sem apagar
a evidência técnica produzida por cada especialista.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Mapping

PROVENANCE_RULE_VERSION = "COMPETENCIA-PROVENIENCIA-V8-1"

_METHOD_MAP = {
    "DOCUMENTO": "DOCUMENTO_EXPLICITO",
    "DOCUMENTO_EXPLICITO": "DOCUMENTO_EXPLICITO",
    "XML_PERAPUR": "DOCUMENTO_EXPLICITO",
    "XML_PERAPUR_13": "DOCUMENTO_EXPLICITO",
    "PERIODO_APURACAO": "DOCUMENTO_EXPLICITO",
    "PERIODO_APURACAO_MES_EXTENSO": "DOCUMENTO_EXPLICITO",
    "FONTE_ESTRUTURADA": "FONTE_ESTRUTURADA",
    "CONTEXTO_OCORRENCIA": "CONTEXTO_OCORRENCIA",
    "DECISAO_MANUAL": "DECISAO_MANUAL",
    "CALENDARIO_ESOCIAL": "CALENDARIO_INFERIDO",
    "CALENDARIO_ESOCIAL_EXCECAO": "CALENDARIO_INFERIDO",
    "CALENDARIO_ESOCIAL_MULTIPLO": "CALENDARIO_INFERIDO",
    "CALENDARIO_INFERIDO": "CALENDARIO_INFERIDO",
}

_STRENGTH = {
    "DECISAO_MANUAL": 60,
    "DOCUMENTO_EXPLICITO": 50,
    "FONTE_ESTRUTURADA": 45,
    "CONTEXTO_OCORRENCIA": 40,
    "CALENDARIO_INFERIDO": 20,
    None: 0,
    "": 0,
}


def normalizar_metodo(metodo: str | None) -> str | None:
    raw = str(metodo or "").strip().upper()
    if not raw or raw in {"PENDENTE_INFERENCIA", "SEM_COMPETENCIA"}:
        return None
    if raw in _METHOD_MAP:
        return _METHOD_MAP[raw]
    if raw.startswith("DOCUMENTO") or raw.startswith("XML_") or raw.startswith("PERIODO_APURACAO"):
        return "DOCUMENTO_EXPLICITO"
    if raw.startswith("CALENDARIO"):
        return "CALENDARIO_INFERIDO"
    if raw.startswith("FONTE") or raw.startswith("API_"):
        return "FONTE_ESTRUTURADA"
    if raw.startswith("CONTEXTO"):
        return "CONTEXTO_OCORRENCIA"
    if raw.startswith("MANUAL"):
        return "DECISAO_MANUAL"
    return None


def forca_metodo(metodo: str | None) -> int:
    return int(_STRENGTH.get(normalizar_metodo(metodo), 0))


def aplicar_proveniencia(dados: dict[str, Any], *, fonte: str | None = None,
                         regra_versao: str | None = None,
                         determinado_em: str | None = None) -> dict[str, Any]:
    competencia = dados.get("competencia")
    raw = dados.get("competencia_metodo_raw") or dados.get("competencia_metodo")
    metodo = normalizar_metodo(raw)
    if not competencia:
        dados["competencia_metodo"] = None
        return dados
    dados["competencia_metodo_raw"] = raw
    dados["competencia_metodo"] = metodo
    dados["competencia_regra_versao"] = dados.get("competencia_regra_versao") or regra_versao or PROVENANCE_RULE_VERSION
    dados["competencia_determinada_em"] = dados.get("competencia_determinada_em") or determinado_em or datetime.now().isoformat(timespec="seconds")
    evidencia = dados.get("competencia_evidencia")
    if not evidencia:
        evidencia = {
            "fonte": fonte,
            "metodo_tecnico": raw,
            "data_envio": dados.get("data_envio"),
            "janela": dados.get("competencia_janela"),
            "periodo_apuracao": dados.get("periodo_apuracao"),
        }
        dados["competencia_evidencia"] = {k: v for k, v in evidencia.items() if v not in (None, "")}
    return dados


def evidencia_json(dados: Mapping[str, Any]) -> str | None:
    evidencia = dados.get("competencia_evidencia")
    if evidencia in (None, "", {}):
        return None
    if isinstance(evidencia, str):
        return evidencia
    return json.dumps(evidencia, ensure_ascii=False, sort_keys=True)


def backfill_processamento_proveniencia(con) -> int:
    """Preenche somente proveniência já demonstrável no JSON legado."""
    cols = {r[1] for r in con.execute("PRAGMA table_info(processamento_arquivo)").fetchall()}
    required = {"competencia_metodo", "competencia_janela", "competencia_regra_versao", "competencia_determinada_em", "competencia_evidencia"}
    if not required.issubset(cols):
        return 0
    rows = con.execute(
        """SELECT id,competencia,dados_json,origem_documental,processado_em
             FROM processamento_arquivo
            WHERE competencia IS NOT NULL AND TRIM(competencia)<>''
              AND (competencia_metodo IS NULL OR TRIM(competencia_metodo)='')"""
    ).fetchall()
    changed = 0
    for row in rows:
        try:
            dados = json.loads(row["dados_json"] or "{}")
        except Exception:
            continue
        raw = dados.get("competencia_metodo_raw") or dados.get("competencia_metodo")
        if not normalizar_metodo(raw):
            continue
        aplicar_proveniencia(dados, fonte=row["origem_documental"], determinado_em=row["processado_em"], regra_versao=dados.get("competencia_regra_versao") or "LEGACY-BACKFILL-V8-1")
        con.execute(
            """UPDATE processamento_arquivo
                  SET competencia_metodo=?,competencia_janela=?,competencia_regra_versao=?,
                      competencia_determinada_em=?,competencia_evidencia=?,dados_json=?
                WHERE id=?""",
            (dados.get("competencia_metodo"), dados.get("competencia_janela"), dados.get("competencia_regra_versao"), dados.get("competencia_determinada_em"), evidencia_json(dados), json.dumps(dados, ensure_ascii=False, sort_keys=True), int(row["id"])),
        )
        changed += 1
    if changed:
        con.commit()
    return changed


__all__ = ["PROVENANCE_RULE_VERSION", "normalizar_metodo", "forca_metodo", "aplicar_proveniencia", "evidencia_json", "backfill_processamento_proveniencia"]
