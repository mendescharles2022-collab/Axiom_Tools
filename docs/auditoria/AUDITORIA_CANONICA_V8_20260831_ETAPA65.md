# Auditoria canônica V8 — Etapa 65

Data: 31/08/2026  
Status: **B04 em correção / linhagem e vigência de versões implementadas no tooling / banco real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 65 criou auditoria read-only da linhagem de versões e retificações.

Novo script:

`scripts/audit_sqlite_version_lineage.py`

## 2. Contrato

A política descreve:

- tabela pai;
- tabela de versões;
- chave do cliente/competência;
- coluna de versão vigente no pai;
- coluna de número da versão;
- estados do pai que obrigam versão vigente;
- flag de versão vigente, quando o schema possuir essa representação.

## 3. Proteções

O auditor verifica:

1. índice único da identidade `chave + versão`;
2. versões duplicadas;
3. número de versão inválido;
4. ponteiro vigente sem versão correspondente;
5. versão órfã sem registro pai;
6. estado que exige versão vigente com ponteiro nulo;
7. múltiplas versões marcadas como vigentes;
8. divergência entre ponteiro do pai e flag de vigente;
9. hash do banco antes/depois da auditoria.

## 4. Regra crítica preservada

**A versão numericamente mais nova não se torna vigente automaticamente.**

Uma versão candidata/retificação pode existir com número superior sem substituir a versão promovida.

Isso é necessário para B01/B04: candidato deve ser preparado e validado antes de promoção atômica.

## 5. Regressões

Foram adicionados dez testes, incluindo explicitamente o cenário em que existe versão candidata mais nova sem promoção.

## 6. Marco CI combinado

Run:

`33444141491`

Commit:

`09f331ea07c222388b3911ba8e43587e495284c2`

Resultado:

```text
Ran 280 tests in 1.211s
OK
```

Artifact:

- ID `9777371725`;
- SHA-256 `e1b7dc55a87fb80cc7755f7ceefa18b90a74c326e697aed5afe223a43302ad6d`.

## 7. Impacto sobre B04

B04 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Ainda faltam:

1. schema de versionamento real reconciliado;
2. configuração da política contra esse schema;
3. auditoria da cópia real;
4. correção das divergências encontradas;
5. teste de retificação material;
6. teste de candidato não promovido;
7. promoção atômica;
8. regressões C01 e C12.

## 8. Limite

**Linhagem válida em fixture não equivale a versionamento homologado.**

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
