# Auditoria canônica V8 — Etapa 68

Data: 31/08/2026  
Status: **B32 em correção / contrato temporal de competência testável / parser real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 68 criou um validador de competência temporal e proveniência para resultados de parser.

Novo script:

`scripts/validate_temporal_competence_evidence.py`

## 2. Princípio

O validador não embute uma regra tributária silenciosa.

A política declara:

- tipos documentais abrangidos;
- campo que contém a data-base temporal;
- regra de formação da competência;
- métodos de competência permitidos;
- evidências obrigatórias.

O tooling apenas prova que o resultado extraído respeita esse contrato.

## 3. Contrato IRRF auditado

Para o cenário B32, a política de teste usa a data de pagamento como base temporal e a regra:

`SAME_MONTH_AS_BASIS_DATE`

Assim, uma folha/referência de agosto paga em setembro deve produzir competência temporal de setembro quando esse for o contrato configurado.

## 4. Verificações

São bloqueados:

- data-base ausente/inválida;
- competência ausente ou malformada;
- competência divergente da data-base;
- método de competência não autorizado;
- ausência de evidência temporal;
- evidência incompleta;
- execução sem nenhum documento-alvo.

## 5. Regressões

Foram adicionados dez testes, incluindo explicitamente:

- competência coerente com pagamento;
- referência de folha em mês anterior sem sobrescrever a base pagamento;
- competência indevidamente derivada do mês da folha;
- método incorreto;
- evidência ausente/incompleta;
- mistura com documentos não alvo.

## 6. Marco CI

Run `33444873556`  
Commit `af23e64da69ac69fe92db9ec39a56ba98dbad03e`

```text
Ran 312 tests in 1.368s
OK
```

Preflight:

```text
Final OK: False
Bloqueadores homologados: 0/50
Casos PASS: 0/28
Mapa causal: 28/28
Evidências PASS: 1/10
Release READY: False
Build OK: False
```

Artifact:

- ID `9777628205`;
- SHA-256 `9fe1d37c0e51e17920f1dca7a706356a77bffa25ea1285fff920f8af4e63fdec`.

## 7. Impacto sobre B32

B32 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Ainda faltam:

1. árvore/parser operacional reconciliados por B06;
2. política temporal real confirmada para cada documento/código aplicável;
3. export dos resultados reais do parser;
4. execução do validador sobre fixtures reais;
5. correção do parser/proveniência quando divergente;
6. regressão end-to-end C23.

## 8. Limite

**Contrato temporal verde em fixtures não equivale a parser homologado.**

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
