"""Composição segura de múltiplas GFD/FGTS Digital por competência."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


def _money(v: Any) -> float | None:
    try:
        return round(float(v), 2) if v is not None else None
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
        obj = json.loads(raw or "{}")
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _tipo(item: Mapping[str, Any]) -> str:
    return str(item.get("documento_tipo") or item.get("tipo_anterior") or "").upper()


def _status(item: Mapping[str, Any]) -> str:
    return str(item.get("status") or item.get("status_anterior") or "").upper()


def _components(d: Mapping[str, Any]) -> dict[str, float]:
    total = _money(d.get("fgts_total"))
    rescisorio = _money(d.get("fgts_rescisorio")) or 0.0
    indenizacao = _money(d.get("indenizacao_compensatoria")) or 0.0
    encargos = _money(d.get("encargos_fgts")) or 0.0
    mensal = None if total is None else round(max(0.0, total - rescisorio - indenizacao - encargos), 2)
    if mensal is None:
        mensal = _money(d.get("fgts_mensal")) or 0.0
    return {
        "mensal": mensal,
        "rescisorio": rescisorio,
        "indenizacao": indenizacao,
        "encargos": encargos,
        "consignado": _money(d.get("consignado_total")) or 0.0,
    }


def _fingerprint(item: Mapping[str, Any]) -> str:
    d = _dados(item); c = _components(d)
    payload = {
        "competencia": d.get("competencia") or item.get("competencia") or item.get("competencia_anterior"),
        "empregador": d.get("cnpj_raiz") or d.get("cpf_empregador") or d.get("documento_contribuinte"),
        "componentes": c,
        "trabalhadores": d.get("quantidade_trabalhadores"),
        "guia_total": _money(d.get("guia_total")),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _source(item: Mapping[str, Any], fp: str, duplicate: bool) -> dict[str, Any]:
    d = _dados(item)
    return {
        "id": item.get("id") or item.get("processamento_id"),
        "nome": item.get("nome_original") or item.get("nome_original_anterior"),
        "sha256": item.get("sha256") or item.get("sha256_anterior"),
        "identificador": d.get("identificador"),
        "status": _status(item),
        "fingerprint_economico": fp,
        "duplicata_equivalente": duplicate,
        "componentes": _components(d),
    }


def _is_subset(a: Mapping[str, float], b: Mapping[str, float]) -> bool:
    extra = False
    for key in ("mensal", "rescisorio", "indenizacao", "encargos", "consignado"):
        av = round(float(a.get(key) or 0), 2); bv = round(float(b.get(key) or 0), 2)
        if av > 0.02 and abs(av - bv) > 0.02:
            return False
        if av <= 0.02 and bv > 0.02:
            extra = True
    return extra


def compor_guias_fgts(documentos: Iterable[Mapping[str, Any]]) -> dict[str, Any] | None:
    itens = [dict(x) for x in documentos if _tipo(x) == "GUIA_FGTS_DIGITAL"]
    if not itens:
        return None
    processados = [x for x in itens if _status(x) == "PROCESSADO"]
    candidatos = processados or itens

    unicos: list[dict[str, Any]] = []
    fontes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in candidatos:
        fp = _fingerprint(item); duplicate = fp in seen
        fontes.append(_source(item, fp, duplicate))
        if not duplicate:
            seen.add(fp); unicos.append(item)

    cobertos: set[int] = set()
    comps = [_components(_dados(x)) for x in unicos]
    for i, ca in enumerate(comps):
        for j, cb in enumerate(comps):
            if i != j and _is_subset(ca, cb):
                cobertos.add(i); break
    efetivos = [x for i, x in enumerate(unicos) if i not in cobertos]
    efetivos_comp = [_components(_dados(x)) for x in efetivos]

    conflitos: list[dict[str, Any]] = []
    agregado: dict[str, float] = {}
    for key in ("mensal", "rescisorio", "indenizacao", "encargos", "consignado"):
        vals = [round(float(c[key] or 0), 2) for c in efetivos_comp if abs(float(c[key] or 0)) > 0.02]
        distintos = sorted(set(vals))
        if not vals:
            agregado[key] = 0.0
        elif len(vals) == 1:
            agregado[key] = vals[0]
        elif len(distintos) == 1:
            agregado[key] = distintos[0]
        else:
            agregado[key] = 0.0
            conflitos.append({"componente": key, "valores": vals})

    fgts_total = round(agregado["mensal"] + agregado["rescisorio"] + agregado["indenizacao"] + agregado["encargos"], 2)
    guia_total = round(fgts_total + agregado["consignado"], 2)
    return {
        "fgts_mensal": agregado["mensal"],
        "fgts_rescisorio": agregado["rescisorio"],
        "indenizacao_compensatoria": agregado["indenizacao"],
        "encargos_fgts": agregado["encargos"],
        "fgts_total": None if conflitos else fgts_total,
        "consignado_total": agregado["consignado"],
        "guia_total": None if conflitos else guia_total,
        "_composicao_gfd": {
            "quantidade_documentos": len(candidatos),
            "quantidade_unicos": len(unicos),
            "quantidade_efetivos": len(efetivos),
            "duplicatas_equivalentes": len(candidatos) - len(unicos),
            "guias_cobertas_por_sucessora": len(cobertos),
            "conflitos": conflitos,
            "fontes": fontes,
        },
    }


__all__ = ["compor_guias_fgts"]
