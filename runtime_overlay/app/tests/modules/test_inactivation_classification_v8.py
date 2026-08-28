from __future__ import annotations

import sqlite3
import unittest

from axiom_tools.db.schema import criar_schema
from axiom_tools.modules.clients.models import ClassificacaoInativacao, TipoPessoa
from axiom_tools.modules.clients.repository import ClienteRepository
from axiom_tools.modules.clients.service import ClienteService


class InactivationClassificationV8Tests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        criar_schema(self.con)
        self.repo = ClienteRepository(self.con)
        self.service = ClienteService(self.repo)
        self.cliente = self.service.criar_cliente(
            tipo_pessoa=TipoPessoa.PF,
            nome="Teste Classificacao",
            documento="52998224725",
        )

    def tearDown(self):
        self.con.close()

    def test_service_accepts_canonical_string(self):
        cliente = self.service.inativar_cliente(
            self.cliente.id,
            motivo="Baixa",
            classificacao="BAIXADA",
        )
        self.assertEqual(cliente.classificacao_inativacao, ClassificacaoInativacao.BAIXADA)
        raw = self.con.execute(
            "SELECT classificacao_inativacao FROM clientes WHERE id=?",
            (self.cliente.id,),
        ).fetchone()[0]
        self.assertEqual(raw, "BAIXADA")

    def test_service_normalizes_lowercase_string(self):
        cliente = self.service.inativar_cliente(
            self.cliente.id,
            classificacao="transferida",
        )
        self.assertEqual(cliente.classificacao_inativacao, ClassificacaoInativacao.TRANSFERIDA)

    def test_invalid_string_is_rejected_before_mutation(self):
        with self.assertRaises(ValueError):
            self.service.inativar_cliente(
                self.cliente.id,
                classificacao="QUALQUER",
            )
        cliente = self.repo.buscar_por_id(self.cliente.id)
        self.assertEqual(cliente.situacao.value, "ATIVO")
        self.assertIsNone(cliente.classificacao_inativacao)

    def test_repository_defensively_serializes_string_entity(self):
        cliente = self.repo.buscar_por_id(self.cliente.id)
        cliente.classificacao_inativacao = "SEM_MOVIMENTO"
        self.repo.atualizar(cliente)
        raw = self.con.execute(
            "SELECT classificacao_inativacao FROM clientes WHERE id=?",
            (cliente.id,),
        ).fetchone()[0]
        self.assertEqual(raw, "SEM_MOVIMENTO")

    def test_repository_rejects_invalid_string_entity(self):
        cliente = self.repo.buscar_por_id(self.cliente.id)
        cliente.classificacao_inativacao = "INVALIDA"
        with self.assertRaises(ValueError):
            self.repo.atualizar(cliente)


if __name__ == "__main__":
    unittest.main()
