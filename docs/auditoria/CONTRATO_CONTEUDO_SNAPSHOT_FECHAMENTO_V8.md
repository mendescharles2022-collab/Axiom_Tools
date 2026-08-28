# Contrato V8 — Conteúdo mínimo do snapshot de fechamento

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / suficiência do payload atual ainda não comprovada**

## 1. Evidência recuperada

A V5.6.14V4 comprovadamente possui:

- tabela `fechamento_mensal_versao`;
- tabela `fechamento_mensal_retificacao`;
- snapshot versionado por cliente + competência;
- comparação material envolvendo folha, pessoas, INSS, DARF esperado, DARF e-CAC, FGTS, eConsignado e S-1299;
- preservação da versão anterior;
- backfill V1 para fechamentos legados;
- bloqueio de saídas durante retificação.

Evidência da instalação real mostra `retification.py` criando as tabelas, porém o DDL/payload completo do snapshot não foi recuperado nesta auditoria.

Portanto:

**o versionamento V4 está comprovado; a suficiência do conteúdo do snapshot para o contrato V8 não está comprovada.**

## 2. Objetivo V8

Uma versão fechada precisa permitir reconstruir, no futuro:

- quem era o cliente naquele fechamento;
- quais inscrições/unidades participaram;
- quais obrigações eram aplicáveis;
- quais documentos/evidências sustentaram cada obrigação;
- quais valores foram esperados e encontrados;
- quais justificativas/impedimentos foram aceitos;
- por que o agregador concluiu `FECHADA`;
- qual versão autorizou uma impressão/entrega.

Não basta congelar apenas totais monetários.

## 3. Identidade histórica mínima

Snapshot deve preservar, conforme aplicável:

- cliente_id de origem;
- nome/razão social no momento do fechamento;
- CPF/CNPJ principal;
- tipo PF/PJ;
- perfil operacional relevante;
- inscrições relevantes: CAEPF, IE, CNO, CEI etc.;
- matriz/filial/unidade econômica quando pertinente;
- competência;
- chamada em que o fechamento foi concluído.

Alteração cadastral futura não reescreve esses valores históricos.

## 4. Composição mensal

Preservar:

- situação de movimento mensal;
- motivo de inclusão na composição;
- chamada;
- eventuais decisões mensais relevantes;
- versão/revisão da composição usada.

## 5. Obrigações por fonte

Para cada fonte/obrigação aplicável, congelar pelo menos:

- código/tipo da obrigação;
- aplicabilidade;
- motivo/regra de aplicabilidade;
- estado terminal;
- valor esperado;
- valor encontrado/composto;
- tolerância aplicada, quando existir;
- justificativa/impedimento, quando existir;
- responsabilidade operacional, quando parametrizada;
- proveniência.

Exemplos:

- DARF/federal;
- FGTS mensal;
- FGTS rescisório/antecipado;
- DAE;
- eConsignado.

## 6. Evidências documentais

Para cada documento utilizado no fechamento, preservar referência suficiente para reidentificá-lo:

- processamento_arquivo_id ou identificador equivalente;
- hash físico;
- fingerprint lógico quando existente;
- tipo documental;
- competência interpretada;
- identidade/inscrição/matrícula;
- versão documental vigente usada;
- origem/caminho lógico;
- valores relevantes extraídos;
- proveniência dos campos principais.

O snapshot não precisa duplicar os bytes do PDF dentro do SQLite, mas precisa apontar inequivocamente para a evidência preservada.

## 7. Pessoas e vínculos materiais

Quando influenciam o fechamento/retificação, preservar resumo estruturado suficiente para comparação, como:

- empregado/contribuinte;
- matrícula/vínculo;
- admissão/desligamento;
- afastamento relevante;
- remuneração/base relevante;
- informação material de consignado/rescisão.

Não é obrigatório congelar toda a ficha completa se não for necessária; é obrigatório congelar o que sustenta a conclusão e a materialidade.

## 8. Composição multi-documento

Snapshot deve preservar como o valor consolidado foi formado.

Exemplo Jair:

```text
federal = 511,43
regra = CONSOLIDADO_NAO_SOMAR_REPETICAO
extratos = [449,450]

fgts = 389,04
componentes = [
  CAEPF_A -> 129,68,
  CAEPF_B -> 259,36
]
```

Assim uma Vn futura pode comparar a composição, não apenas o total.

## 9. Justificativas por fonte

Preservar:

- fonte;
- tipo da decisão;
- motivo padronizado;
- observação;
- usuário;
- data/hora;
- evidência que suportava a decisão.

Uma justificativa global antiga não pode aparecer no snapshot V8 como se tivesse resolvido todas as fontes.

## 10. Resultado agregado

Snapshot deve registrar:

- estado final `FECHADA`;
- resultado das obrigações;
- regra/versão do agregador;
- data/hora do fechamento;
- usuário/evento/processo;
- correlação;
- hash/fingerprint lógico do próprio snapshot, quando tecnicamente adequado.

## 11. Saídas

A versão deve ser referenciável por:

- impressão;
- entrega;
- PDF consolidado;
- saída automática.

Não é necessário embutir saídas no snapshot; a saída aponta para a versão que a autorizou.

## 12. Evolução do formato

O snapshot precisa possuir versão de schema/formato independente do número da versão de fechamento, por exemplo:

```text
snapshot_schema_version = 2
```

Isso permite evoluir V8/V9 sem interpretar payload antigo como se tivesse campos que nunca existiram.

## 13. Backfill legado

Snapshots V1 legados criados pela V4 não devem receber dados inventados.

Migração deve:

- preservar payload original;
- marcar versão de schema legado;
- enriquecer somente campos reconstruíveis com prova determinística;
- deixar `NAO_DISPONIVEL_NO_LEGADO` quando a informação não existia;
- nunca fabricar decisão por fonte retroativamente.

## 14. Regressões mínimas

1. alteração de nome cadastral não muda snapshot antigo;
2. exclusão do cadastro mestre não torna snapshot ilegível;
3. Jair conserva componentes por matrícula;
4. Leosmar conserva documentos equivalentes sem soma fictícia;
5. decisão DARF não aparece como decisão FGTS;
6. MEI snapshot registra DAE como obrigação aplicável correta;
7. versão fechada aponta para documentos usados;
8. retificação Vn+1 compara deltas estruturados com Vn;
9. saída registra qual versão a autorizou;
10. snapshot legado não recebe campos inventados durante migração.

## 15. Prova ainda necessária

No runtime reconciliado, inspecionar:

- DDL completo de `fechamento_mensal_versao`;
- função que monta o snapshot;
- função que calcula materialidade;
- conteúdo de snapshots reais de 05/2026 e 08/2026;
- dependências com cadastro atual;
- capacidade de representar decisões por fonte e composição multi-documento.

## 16. Relação com bloqueadores

Principalmente B04, B05, B12, B13, B14, B18, B35, B36, B39, B42 e B49.
