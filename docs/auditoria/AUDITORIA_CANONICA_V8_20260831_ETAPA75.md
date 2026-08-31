# Auditoria canônica V8 — Etapa 75

Data: 31/08/2026  
Status: **B12–B17/B50 com tooling executável e regressões / aplicação ao runtime ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 75 transformou a família de composição multi-documento e identidade de vínculo em dois toolings read-only:

- B12 — múltiplos Extratos não podem ser reduzidos ao último arquivo;
- B13 — federal consolidado e FGTS por matrícula têm granularidades diferentes;
- B14 — múltiplas GFD precisam ser classificadas antes da soma;
- B15 — descoberta física precisa chegar ao índice/vínculo antes da Conferência;
- B16 — PF rural exige identidade de pessoa e de unidade, quando aplicável;
- B17 — deduplicação física não substitui deduplicação lógica/econômica;
- B50 — hash não é identidade da obrigação.

## 2. Composição documental/econômica

Novo tooling:

`scripts/plan_document_obligation_composition.py`

O planner separa três níveis de identidade:

1. `physical_sha256` — identidade física;
2. `logical_fingerprint` — identidade documental;
3. `economic_key + component_key` — identidade econômica/componente.

Relações suportadas:

- `PRIMARY`;
- `IDENTICO_FISICO`;
- `REEMISSAO_EQUIVALENTE`;
- `VERSAO_SUCESSORA`;
- `SUBSTITUTIVO`;
- `COMPLEMENTAR`;
- `UNIDADE_DISTINTA`;
- `COMPONENTE_ADITIVO`;
- `RELACAO_INDETERMINADA`.

Regras centrais:

- SHA igual com mesma identidade física é contado uma vez;
- SHA igual com identidades econômicas conflitantes bloqueia;
- SHA diferente não autoriza soma automática;
- reemissão equivalente exige uma versão corrente e não dobra valor;
- sucessora/substitutiva exige grupo e corrente inequívocos;
- dois documentos primários no mesmo componente econômico não são somados cegamente;
- relação indeterminada produz revisão obrigatória;
- componentes economicamente distintos podem ser adicionados.

## 3. Regressões de composição

Arquivo:

`tests/test_plan_document_obligation_composition.py`

Foram incluídos cenários explícitos para:

- arquivo físico idêntico;
- conflito de identidade sob o mesmo SHA;
- reemissão equivalente com hashes diferentes;
- divergência de valor em reemissão;
- versão sem corrente inequívoca;
- duplicidade econômica sem relação declarada;
- relação indeterminada;
- mensal + rescisório como componentes distintos;
- Leosmar sem duplicação de obrigação equivalente;
- Jair com granularidade federal x FGTS.

### Jair

O cenário sintético aprovado produz:

```text
FEDERAL = R$ 511,43 uma única vez
FGTS matrícula 1 = R$ 129,68
FGTS matrícula 2 = R$ 259,36
FGTS composto = R$ 389,04
```

Isso protege a diferença entre obrigação federal consolidada e FGTS aditivo por unidade.

## 4. Descoberta, índice e vínculo — B15/B16

Novo tooling:

`scripts/validate_document_identity_binding.py`

O validador exige, quando o documento é elegível à Conferência:

- descoberta física confirmada;
- registro indexado;
- `client_id` vinculado;
- método e evidência de vínculo;
- confiança mínima configurável;
- coerência entre identidade extraída e cadastro.

Comparações cobertas:

- CPF;
- CNPJ;
- CAEPF;
- identidade de unidade configurável, como CAEPF/matrícula.

Para produtor rural PF, o contrato é explícito:

**CPF identifica a pessoa, mas não substitui CAEPF/matrícula quando a obrigação depende da unidade.**

Assim, CPF coincidente com CAEPF obrigatório ausente continua bloqueado.

## 5. Marco CI

Run `33447976729`  
Commit `d3df113b297c86db72531c70537eceb5b1e9f6f6`

```text
POWERSHELL_B06_SMOKE_OK
Ran 414 tests in 1.467s
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

- ID `9778709806`;
- SHA-256 `c341df455b483d37824709c8da1ddda75c3ea69130113b155edb867f90c59aaf`.

## 6. Impacto de estados

B12, B13, B14, B15, B16, B17 e B50 passam para:

`EM_CORRECAO`

Isso significa que a correção possui contrato executável e regressões que podem ser aplicados à árvore reconciliada.

Não significa que parser, banco e serviços operacionais já tenham sido alterados.

## 7. Snapshot após a Etapa 75

- `PRONTO_PARA_CORRIGIR`: 18;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 28;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

## 8. Próximo bloco

A próxima frente sem dependência física imediata é B18–B27:

- decisão por fonte/obrigação;
- aplicabilidade FGTS zero/MEI/DAE/deduções/afastamentos;
- responsabilidade Fiscal/impedimento RFB;
- integração eConsignado ao orquestrador;
- universo elegível, fontes e retorno residual.

B28 já possui auditor de idempotência/retry em `EM_CORRECAO`.

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
