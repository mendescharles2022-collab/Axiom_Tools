# Auditoria canônica V8 — Etapa 62

Data: 31/08/2026  
Status: **B34 em correção / auditor de contrato string↔Enum implementado e testado / árvore operacional real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 62 criou um auditor estático específico para a inconsistência de representação de `classificacao_inativacao`.

Novo script:

`scripts/audit_classificacao_inativacao_contract.py`

O auditor é somente leitura e não executa autofix.

## 2. Representações reconhecidas

O tooling distingue explicitamente:

- membro Enum, por exemplo `ClassificacaoInativacao.INATIVA`;
- valor serializado do Enum, por exemplo `ClassificacaoInativacao.INATIVA.value`;
- string literal crua;
- `None`;
- valor dinâmico.

A representação canônica é configurável como:

- `ENUM_MEMBER`; ou
- `STRING_VALUE`.

## 3. Contextos auditados

São inventariados usos em:

- comparações;
- atribuições;
- atribuições anotadas;
- acesso por atributo;
- acesso por chave, como `row['classificacao_inativacao']`.

Mistura de membro Enum com representação string/`.value` no mesmo contrato é sinalizada como deriva semântica.

## 4. Política de borda

String literal pode ser autorizada apenas quando a política declarar explicitamente que aquela árvore representa uma borda de armazenamento/serialização.

Valor dinâmico também só é aceito quando explicitamente permitido.

O auditor não converte valores, não altera banco e não modifica código.

## 5. Regressões

Foram adicionados oito testes cobrindo:

1. comparação Enum válida em contrato Enum;
2. string crua recusada em contrato Enum;
3. `.value` válido em contrato string;
4. membro Enum recusado em contrato string;
5. string crua explicitamente permitida na borda de armazenamento;
6. mistura Enum/string bloqueada;
7. atribuição dinâmica exigindo política explícita;
8. erro de sintaxe bloqueando a auditoria.

## 6. Marco CI

Run:

`33443562347`

Commit:

`1b5bae6ef30ec9a501cffb98785bfd0fecd5093f`

Python:

`3.12.14`

Resultado:

```text
Ran 253 tests in 1.210s
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

- `v8-release-preflight`;
- ID `9777159518`;
- SHA-256 `c98fba7ecba54343a19cf486ccff2e62bb6b8b5a7e803550ef2a52d49abeec43`.

## 7. Impacto sobre B34

B34 pode avançar de `PRONTO_PARA_CORRIGIR` para `EM_CORRECAO`.

O tooling agora consegue localizar deriva string↔Enum sem realizar conversões arriscadas.

Ainda faltam para homologação:

1. reconciliar a árvore operacional integral por B06;
2. identificar o tipo real do campo/modelo no runtime;
3. definir a representação canônica por camada;
4. executar o auditor sobre a árvore real;
5. corrigir todos os pontos incompatíveis;
6. testar persistência, leitura, filtros e templates;
7. executar regressão operacional correspondente.

## 8. Regra preservada

**Auditor verde em fixtures não equivale a B34 corrigido.**

Nenhuma conversão automática foi adicionada enquanto o contrato real do campo não estiver reconciliado.

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
