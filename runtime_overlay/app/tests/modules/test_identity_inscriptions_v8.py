from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from axiom_tools.modules.processing.identity import detectar_identificadores, resolver_cliente_documento
from axiom_tools.modules.processing.ecac_rules import cliente_por_documento
from axiom_tools.modules.processing.motors.dominio_engine import _especialista_identidade

SOURCE_DB = Path('/mnt/data/axiom_tools_recovered_snapshot/Axiom_Tools/data/axiom_tools.db')


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    con.executescript('''
        CREATE TABLE clientes(
            id INTEGER PRIMARY KEY, documento TEXT, nome TEXT, nome_apresentacao TEXT
        );
        CREATE TABLE cliente_inscricoes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, numero TEXT NOT NULL
        );
        CREATE TABLE processamento_identidade_vinculo(
            documento TEXT PRIMARY KEY, cliente_id INTEGER NOT NULL, origem TEXT
        );
    ''')
    con.execute("INSERT INTO clientes VALUES(1,'10127380191','Jair Ferreira Camargo','Jair Ferreira Camargo')")
    con.execute("INSERT INTO cliente_inscricoes(cliente_id,tipo,numero) VALUES(1,'CAEPF','101.273.801/001-49')")
    con.execute("INSERT INTO cliente_inscricoes(cliente_id,tipo,numero) VALUES(1,'CAEPF','101.273.801/002-30')")
    con.execute("INSERT INTO clientes VALUES(2,'12345678909','Outro Cliente','Outro Cliente')")
    con.commit()
    return con


class IdentityInscriptionsV8Tests(unittest.TestCase):
    def test_two_caepfs_resolve_same_pf_client(self):
        con = make_con()
        for caepf in ('101.273.801/001-49', '101.273.801/002-30'):
            cli, metodo = resolver_cliente_documento(con, caepf)
            self.assertEqual(cli['id'], 1)
            self.assertEqual(metodo, 'INSCRICAO_CAEPF')
        con.close()

    def test_duplicate_official_inscription_is_ambiguous(self):
        con = make_con()
        con.execute("INSERT INTO cliente_inscricoes(cliente_id,tipo,numero) VALUES(2,'CAEPF','101.273.801/001-49')")
        con.commit()
        cli, metodo = resolver_cliente_documento(con, '101.273.801/001-49')
        self.assertIsNone(cli)
        self.assertEqual(metodo, 'AMBIGUO_INSCRICAO')
        con.close()

    def test_dominio_caepf_wins_over_employee_cpf(self):
        con = make_con()
        texto = '''EXTRATO MENSAL 08/2026\nCAEPF: 101.273.801/002-30\nNome do Funcionário\nCPF: 123.456.789-09'''
        ids = detectar_identificadores(texto)
        self.assertEqual(ids['caepf'], '101.273.801/002-30')
        self.assertIsNone(ids['cpf'])
        result = _especialista_identidade(texto, con)
        self.assertEqual(result['cliente_id'], 1)
        self.assertEqual(result['caepf'], '101.273.801/002-30')
        self.assertEqual(result['identidade_metodo'], 'INSCRICAO_CAEPF')
        con.close()

    def test_dominio_labeled_employer_cpf_resolves_pf(self):
        con = make_con()
        texto = 'CPF do Empregador: 101.273.801-91\nEXTRATO MENSAL 08/2026'
        result = _especialista_identidade(texto, con)
        self.assertEqual(result['cliente_id'], 1)
        self.assertEqual(result['cpf'], '101.273.801-91')
        self.assertEqual(result['identidade_metodo'], 'DOCUMENTO_PRINCIPAL')
        con.close()

    def test_ecac_wrapper_also_resolves_official_inscription(self):
        con = make_con()
        cli = cliente_por_documento(con, '101.273.801/001-49')
        self.assertEqual(cli['id'], 1)
        con.close()

    def test_ambiguous_caepf_does_not_fallback_by_name(self):
        con = make_con()
        con.execute("INSERT INTO cliente_inscricoes(cliente_id,tipo,numero) VALUES(2,'CAEPF','101.273.801/001-49')")
        con.commit()
        texto = 'CAEPF: 101.273.801/001-49\nJair Ferreira Camargo\nEXTRATO MENSAL 08/2026'
        result = _especialista_identidade(texto, con)
        self.assertIsNone(result['cliente_id'])
        self.assertEqual(result['identidade_metodo'], 'AMBIGUO_INSCRICAO')
        con.close()

    @unittest.skipUnless(SOURCE_DB.exists(), 'snapshot real indisponível')
    def test_real_jair_both_caepfs_resolve_client_826(self):
        con = sqlite3.connect(SOURCE_DB)
        con.row_factory = sqlite3.Row
        for caepf in ('101.273.801/001-49', '101.273.801/002-30'):
            cli, metodo = resolver_cliente_documento(con, caepf)
            self.assertEqual(cli['id'], 826)
            self.assertEqual(metodo, 'INSCRICAO_CAEPF')
        con.close()


if __name__ == '__main__':
    unittest.main()
