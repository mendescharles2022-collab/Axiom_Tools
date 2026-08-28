"""Composição econômica de documentos do Processamento.

O módulo separa arquivo físico de obrigação econômica. Em especial, múltiplos
Extratos Mensais do Domínio podem representar reemissão equivalente ou
componentes distintos da mesma competência.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


def _money(value: Any) -> float | None:
    try:
        return round(float(value), 2) if value is not None else None
    except (TypeError, ValueError):
        return None


def _dados(item: Mapping[str, Any]) -> dict[str, Any]:
    raw = item.get("dados")
    if isinstance(raw, dict):
        return raw
    raw = item.get("dados_json")
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _tipo(item: Mapping[str, Any]) -> str:
    return str(item.get("documento_tipo") or item.get("tipo_anterior") or "").upper()


def _status(item: Mapping[str, Any]) -> str:
    return str(item.get("status") or item.get("status_anterior") or "").upper()


def _identificador_unidade(dados: Mapping[str, Any]) -> str | None:
    for key in (
        "caepf", "matricula", "matricula_caepf", "inscricao", "inscricao_estabelecimento",
        "documento_estabelecimento", "cnpj", "cpf", "documento_contribuinte",
    ):
        value = str(dados.get(key) or "").strip()
        if value:
            return value
    return None


def _fingerprint_extrato(item: Mapping[str, Any]) -> str:
    dados = _dados(item)
    payload = {
        "unidade": _identificador_unidade(dados),
        "competencia": dados.get("competencia") or item.get("competencia") or item.get("competencia_anterior"),
        "total_proventos": _money(dados.get("total_proventos")),
        "total_descontos": _money(dados.get("total_descontos")),
        "liquido_geral": _money(dados.get("liquido_geral")),
        "total_inss": _money(dados.get("total_inss")),
        "fgts_total": _money(dados.get("fgts_total")),
        "darf_folha_esperado": _money(dados.get("darf_folha_esperado")),
        "saldo_total_apuracao_dominio": _money(dados.get("saldo_total_apuracao_dominio")),
        "econsignado_total": _money(dados.get("econsignado_total")),
        "salario_familia": _money(dados.get("salario_familia_deducao_folha")),
        "salario_maternidade": _money(dados.get("salario_maternidade_deducao_folha")),
    }
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _source(item: Mapping[str, Any], *, fingerprint: str, duplicate: bool) -> dict[str, Any]:
    dados = _dados(item)
    return {
        "id": item.get("id") or item.get("processamento_id"),
        "nome": item.get("nome_original") or item.get("nome_original_anterior"),
        "sha256": item.get("sha256") or item.get("sha256_anterior"),
        "status": _status(item),
        "unidade": _identificador_unidade(dados),
        "fingerprint_economico": fingerprint,
        "duplicata_equivalente": duplicate,
        "total_inss": _money(dados.get("total_inss")),
        "fgts_total": _money(dados.get("fgts_total")),
        "darf_folha_esperado": _money(dados.get("darf_folha_esperado")),
        "saldo_total_apuracao_dominio": _money(dados.get("saldo_total_apuracao_dominio")),
    }


def _sum(items: Iterable[Mapping[str, Any]], field: str) -> float | None:
    values = [_money(_dados(item).get(field)) for item in items]
    present = [v for v in values if v is not None]
    return round(sum(present), 2) if present else None


def _merge_list(items: Iterable[Mapping[str, Any]], field: str) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for item in items:
        for value in _dados(item).get(field) or []:
            key = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                result.append(value)
    return result


def compor_extratos_mensais(documentos: Iterable[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Compõe Extratos Mensais sem confundir reemissão com componente distinto.

    - reemissões economicamente equivalentes contam uma vez;
    - campos de folha/FGTS são aditivos entre componentes distintos;
    - ``saldo_total_apuracao_dominio`` é consolidado: valor repetido conta uma vez;
    - saldos federais consolidados diferentes geram conflito explícito, nunca soma cega.
    """
    itens = [dict(x) for x in documentos if _tipo(x) == "EXTRATO_MENSAL"]
    if not itens:
        return None
    processados = [x for x in itens if _status(x) == "PROCESSADO"]
    candidatos = processados or itens

    unicos: list[dict[str, Any]] = []
    fontes: list[dict[str, Any]] = []
    fingerprints: set[str] = set()
    for item in candidatos:
        fingerprint = _fingerprint_extrato(item)
        duplicate = fingerprint in fingerprints
        fontes.append(_source(item, fingerprint=fingerprint, duplicate=duplicate))
        if duplicate:
            continue
        fingerprints.add(fingerprint)
        unicos.append(item)

    if not unicos:
        return None

    base = dict(_dados(unicos[-1]))
    additive = (
        "total_proventos", "total_descontos", "liquido_geral", "total_inss", "fgts_total",
        "darf_folha_esperado", "econsignado_total", "salario_familia_deducao_folha",
        "salario_maternidade_deducao_folha", "salario_maternidade_credito_total",
        "salario_maternidade_credito_remanescente",
    )
    for field in additive:
        base[field] = _sum(unicos, field)

    saldos = sorted({
        value for item in unicos
        if (value := _money(_dados(item).get("saldo_total_apuracao_dominio"))) is not None
    })
    conflito_federal = len(saldos) > 1
    base["saldo_total_apuracao_dominio"] = saldos[0] if len(saldos) == 1 else None
    base["apuracao_federal_detalhada"] = all(bool(_dados(x).get("apuracao_federal_detalhada")) for x in unicos)
    base["validacao_folha"] = all(bool(_dados(x).get("validacao_folha", True)) for x in unicos)
    base["darf_folha_justificativas"] = sorted({
        str(j) for item in unicos for j in (_dados(item).get("darf_folha_justificativas") or []) if str(j)
    })
    base["escrita_fiscal_itens"] = _merge_list(unicos, "escrita_fiscal_itens")
    base["econsignado_contratos"] = _merge_list(unicos, "econsignado_contratos")
    base["_composicao_extratos"] = {
        "quantidade_documentos": len(candidatos),
        "quantidade_componentes": len(unicos),
        "duplicatas_equivalentes": len(candidatos) - len(unicos),
        "saldo_federal_consolidado_valores": saldos,
        "saldo_federal_conflitante": conflito_federal,
        "fontes": fontes,
    }
    return base


__all__ = ["compor_extratos_mensais"]
