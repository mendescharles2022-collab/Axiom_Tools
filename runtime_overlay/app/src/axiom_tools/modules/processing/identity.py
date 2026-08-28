"""Especialista canônico de identidade documental do Processamento.

A identidade do cliente é o cadastro principal (CPF/CNPJ). Inscrições como
CAEPF, CEI, CNO e IE são chaves vinculadas 1:N ao mesmo cliente e jamais devem
criar um segundo cliente por inferência.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any


def _digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))


def _cliente_row(con: sqlite3.Connection, cliente_id: int):
    return con.execute(
        "SELECT id,documento,nome,nome_apresentacao FROM clientes WHERE id=?",
        (int(cliente_id),),
    ).fetchone()


def resolver_cliente_documento(con: sqlite3.Connection, documento: str | None):
    """Resolve documento principal, inscrição oficial ou vínculo manual.

    Retorna ``(cliente_row, metodo)``. Qualquer chave que aponte para mais de um
    cliente é tratada como ambígua e não gera vínculo silencioso.
    """
    digits = _digits(documento)
    if not digits:
        return None, None

    rows = con.execute(
        """SELECT id,documento,nome,nome_apresentacao FROM clientes
           WHERE REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(documento,''),'.',''),'/',''),'-',''),' ','')=?""",
        (digits,),
    ).fetchall()
    ids = {int(r["id"]) for r in rows}
    if len(ids) == 1:
        return _cliente_row(con, next(iter(ids))), "DOCUMENTO_PRINCIPAL"
    if len(ids) > 1:
        return None, "AMBIGUO_DOCUMENTO_PRINCIPAL"

    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='cliente_inscricoes'").fetchone():
        rows = con.execute(
            """SELECT DISTINCT c.id,c.documento,c.nome,c.nome_apresentacao,i.tipo
               FROM cliente_inscricoes i JOIN clientes c ON c.id=i.cliente_id
               WHERE REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(i.numero,''),'.',''),'/',''),'-',''),' ','')=?""",
            (digits,),
        ).fetchall()
        ids = {int(r["id"]) for r in rows}
        if len(ids) == 1:
            tipo = str(rows[0]["tipo"] or "INSCRICAO").upper()
            return _cliente_row(con, next(iter(ids))), f"INSCRICAO_{tipo}"
        if len(ids) > 1:
            return None, "AMBIGUO_INSCRICAO"

    if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='processamento_identidade_vinculo'").fetchone():
        rows = con.execute(
            """SELECT DISTINCT c.id,c.documento,c.nome,c.nome_apresentacao
               FROM processamento_identidade_vinculo v JOIN clientes c ON c.id=v.cliente_id
               WHERE REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(v.documento,''),'.',''),'/',''),'-',''),' ','')=?""",
            (digits,),
        ).fetchall()
        ids = {int(r["id"]) for r in rows}
        if len(ids) == 1:
            return _cliente_row(con, next(iter(ids))), "VINCULO_MANUAL"
        if len(ids) > 1:
            return None, "AMBIGUO_VINCULO_MANUAL"
    return None, None


def _rotulado(texto: str, rotulos: tuple[str, ...], tamanhos: tuple[int, ...]) -> str | None:
    labels = "|".join(rotulos)
    for m in re.finditer(rf"(?:{labels})\s*[:\-]?\s*([0-9.\-/ ]{{11,22}})", texto, re.I):
        bruto = m.group(1).strip()
        if len(_digits(bruto)) in tamanhos:
            return bruto
    return None


def detectar_identificadores(texto: str | None) -> dict[str, str | None]:
    """Extrai identificadores do empregador/contribuinte de forma conservadora.

    CPF genérico só é aceito quando é único e não existe CNPJ/CAEPF; isso evita
    confundir CPF de empregado com identidade do cliente em relatórios de folha.
    """
    texto = str(texto or "")

    cnpj = _rotulado(texto, (r"CNPJ(?:\s+do\s+Empregador)?", r"CPF/CNPJ(?:\s+do\s+Empregador)?"), (14,))
    if not cnpj:
        m = re.search(r"(?<!\d)(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})(?!\d)", texto)
        cnpj = m.group(1) if m else None

    caepf = _rotulado(texto, (r"CAEPF", r"Inscri[cç][aã]o\s+CAEPF"), (14,))
    if not caepf:
        m = re.search(r"(?<!\d)(\d{3}\.\d{3}\.\d{3}/\d{3}-\d{2})(?!\d)", texto)
        caepf = m.group(1) if m else None

    cpf = _rotulado(
        texto,
        (r"CPF\s+do\s+Empregador", r"CPF\s+do\s+Contribuinte", r"CPF/CNPJ\s+do\s+Empregador"),
        (11,),
    )
    if not cpf and not cnpj and not caepf:
        cpfs = list(dict.fromkeys(re.findall(r"(?<!\d)(\d{3}\.\d{3}\.\d{3}-\d{2})(?!\d)", texto)))
        if len(cpfs) == 1:
            cpf = cpfs[0]

    return {"cnpj": cnpj, "caepf": caepf, "cpf": cpf}


__all__ = ["resolver_cliente_documento", "detectar_identificadores"]
