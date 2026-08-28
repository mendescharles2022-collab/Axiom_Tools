"""Identidade lógica compartilhada para deduplicação documental.

Hash físico e obrigação econômica são dimensões distintas. Os especialistas de
cada família definem o payload econômico; este módulo apenas canonicaliza,
calcula fingerprint e classifica a relação entre duas evidências.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


def fingerprint_logico(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def relacao_documental(*, sha_a: str | None = None, sha_b: str | None = None,
                       fingerprint_a: str | None = None, fingerprint_b: str | None = None) -> str:
    """Classifica relação sem confundir bytes com obrigação."""
    sa = str(sha_a or "").strip().lower(); sb = str(sha_b or "").strip().lower()
    fa = str(fingerprint_a or "").strip().lower(); fb = str(fingerprint_b or "").strip().lower()
    if sa and sb and sa == sb:
        return "MESMOS_BYTES"
    if fa and fb:
        return "EQUIVALENTE_LOGICO" if fa == fb else "DISTINTO_LOGICO"
    return "INDETERMINADO"


def deduplicar_por_fingerprint(itens: Iterable[Mapping[str, Any]], fingerprint_fn) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Retorna itens econômicos únicos e trilha de classificação."""
    unicos: list[dict[str, Any]] = []
    trilha: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for raw in itens:
        item = dict(raw)
        fp = str(fingerprint_fn(item))
        duplicata = fp in vistos
        trilha.append({
            "fingerprint_economico": fp,
            "duplicata_equivalente": duplicata,
            "sha256": item.get("sha256") or item.get("sha256_anterior"),
        })
        if duplicata:
            continue
        vistos.add(fp)
        unicos.append(item)
    return unicos, trilha


__all__ = ["fingerprint_logico", "relacao_documental", "deduplicar_por_fingerprint"]
