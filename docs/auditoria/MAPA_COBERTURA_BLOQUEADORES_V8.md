# Mapa de cobertura dos bloqueadores — Auditoria V8

Data: 28/08/2026
Status: **controle de cobertura da auditoria / nenhuma correção de runtime inferida deste documento**

## 1. Objetivo

Verificar se algum dos 50 bloqueadores da matriz central ainda está sem:

- evidência/razão de existência;
- regra de correção;
- critério ou protocolo de prova.

Este mapa não muda nenhum bloqueador para `CORRIGIDO_HOMOLOGADO`.

## 2. Legenda de cobertura

- `E` — há evidência/achado que fundamenta o bloqueador;
- `C` — há contrato/regra canônica de correção;
- `P` — há protocolo/regressão objetiva para provar a correção;
- `R` — depende de inspeção/execução no runtime reconciliado.

`ECPR` significa que o problema está plenamente especificado para implementação/homologação, não que esteja corrigido.

## 3. Cobertura B01–B10

| ID | Tema | Cobertura | Referências principais |
|---|---|---|---|
| B01 | Reprocessamento destrutivo | ECPR | continuação canônica; contrato de candidato; plano 449/450; protocolo 28 casos |
| B02 | Conference GET com mutação | ECPR | achado runtime; contrato event-driven; protocolo segurança/28 casos |
| B03 | Gate único de saída | ECPR | achado runtime; contrato gate único; protocolo segurança |
| B04 | Versão/retificação vigente | ECPR | V4 + achado V8; snapshot/materialidade; migração/28 casos |
| B05 | Migração V8 | CPR | contrato schema/migração; invariantes; protocolo migração/rollback |
| B06 | Repositório ≠ runtime | ECPR | divergência registrada; protocolo reconciliação; proveniência build |
| B07 | Universo operacional duplicado | ECPR | SQL duplicado auditado; contrato universo operacional; benchmark/eConsignado |
| B08 | T L / 2ª chamada | ECPR | snapshot runtime; máquina/transições; concorrência; protocolo 28 casos |
| B09 | Fechados na mesa viva | ECPR | escopo runtime; arquitetura Fechamento V8; máquinas de estado; 28 casos |
| B10 | Retificação misturada ao ciclo | ECPR | escopo runtime; contratos retificação/snapshot; máquinas de estado |

## 4. Cobertura B11–B20

| ID | Tema | Cobertura | Referências principais |
|---|---|---|---|
| B11 | Estado antecipado | ECPR | legado PRONTA→conferência; arquitetura operacional; máquinas de estado |
| B12 | Multi-Extrato | ECPR | `_ultimo_tipo`; deduplicação; identidade/consolidação; 28 casos |
| B13 | Federal x FGTS rural | ECPR | Jair 449/450; parser Domínio; deduplicação; matriz 28 casos |
| B14 | Multi-GFD/FGTS rescisório | CPR | contrato composição FGTS; deduplicação; protocolo 28 casos |
| B15 | Descoberta→vínculo | ECPR | V8F2; contrato pipeline documental; protocolo 28 casos |
| B16 | Identidade PF/CAEPF | ECPR | AXT-003/carga real; contrato identidade; pipeline; 28 casos |
| B17 | Deduplicação lógica | CPR | contrato deduplicação; acervo físico; composição FGTS |
| B18 | Decisão por fonte | CPR | contrato decisão por fonte; schema; protocolo segurança/28 casos |
| B19 | FGTS zero | ECPR | V8F2; matriz de aplicabilidade; Etapa 28; 28 casos |
| B20 | MEI/DAE | ECPR | V8F2 Elenice; aplicabilidade; arquitetura Fechamento; 28 casos |

## 5. Cobertura B21–B30

| ID | Tema | Cobertura | Referências principais |
|---|---|---|---|
| B21 | Deduções previdenciárias | CPR | parser Domínio; aplicabilidade; casos Denes/Ponto Kent |
| B22 | Afastamentos/faltas | CPR | aplicabilidade; matriz 28 casos; decisão por fonte |
| B23 | DARF Fiscal/impedimento RFB | CPR | decisão por fonte; casos operacionais; matriz 28 casos |
| B24 | eConsignado fora do orquestrador | ECPR | contrato eConsignado; Etapa 26; jobs/workers |
| B25 | Universo eConsignado excessivo | ECPR | 840 x 339; universo operacional; eConsignado; benchmark |
| B26 | Falso CONFERIDO eConsignado | ECPR | V8F2 D A F Castro; eConsignado; máquinas de estado; 28 casos |
| B27 | Retorno residual | CPR | eConsignado; matriz 28 casos |
| B28 | Idempotência/retry eConsignado | CPR | eConsignado; jobs/workers; concorrência |
| B29 | Diretor ≠ empregado | ECPR | P DA SILVA CARMO; parser Domínio; protocolo 28 casos |
| B30 | Federal autoritativo | ECPR | Extrato real; parser Domínio; contrato temporal federal |

## 6. Cobertura B31–B40

| ID | Tema | Cobertura | Referências principais |
|---|---|---|---|
| B31 | Competência/proveniência | CPR | contrato competência/proveniência; pipeline; parser |
| B32 | IRRF competência pagamento | ECPR | Extratos reais; contrato temporal federal; regressão pendente de parser runtime |
| B33 | Dezembro/13º | CPR | competência/proveniência + calendário configurável/exceções |
| B34 | `classificacao_inativacao` string/Enum | ECPR | falha da suíte; contrato inativação; Etapa 31 |
| B35 | Foreign keys/invariantes | CPR | contrato invariantes; protocolo migração/rollback |
| B36 | Estado global antigo → fonte | CPR | schema/migração; decisão por fonte; Etapa 25 |
| B37 | Máquinas de estado misturadas | ECPR | contrato máquinas de estado; Etapa 38 |
| B38 | Auth/CSRF novas rotas | CPR | contrato autenticação; protocolo segurança; execução runtime pendente |
| B39 | Seleção manual por IDs | ECPR | achado de saída; gate único; protocolo segurança |
| B40 | Concorrência lógica | CPR | contrato concorrência; Etapa 37; protocolo segurança/28 casos |

## 7. Cobertura B41–B50

| ID | Tema | Cobertura | Referências principais |
|---|---|---|---|
| B41 | Backup/rollback | CPR | contrato instalação/rollback; protocolo migração/rollback |
| B42 | Proveniência de build | ECPR | versão 0.1.0 x runtime; contrato proveniência; protocolo reconciliação |
| B43 | Pendências orientada por PROC | ECPR | V8F2; contrato Pendências técnicas x Conferência; Etapa 33 |
| B44 | Relatório A4 retrato | ECPR | V8F2; contrato relatórios/impressão; Etapa 33 |
| B45 | Escala >600 | ECPR | V7; contrato capacidade; protocolo benchmark |
| B46 | Monitor duplicado/confuso | ECPR | runtime/status; contrato Pendências/Monitor; máquinas de estado |
| B47 | Sintegra atalhos/fluxo GO | ECPR | regressão visual; arquitetura Sintegra atualizada; Etapa 33 |
| B48 | Limpeza/retenção | CPR | contrato retenção/limpeza; acervo físico; Etapa 39 |
| B49 | Banco ↔ filesystem | CPR | pipeline documental; acervo físico; invariantes; Etapa 39 |
| B50 | Hash ≠ obrigação | CPR | deduplicação; acervo físico; composição FGTS; Etapa 39 |

## 8. Resultado da auditoria de cobertura

Nenhum dos 50 bloqueadores ficou sem regra de tratamento ou critério de prova.

Isso NÃO significa que os 50 estejam corrigidos.

Significa que a fase de descoberta funcional/arquitetural atingiu cobertura suficiente para a próxima fase controlada:

1. reconciliar a árvore runtime com o repositório;
2. estabelecer baseline reproduzível;
3. corrigir os bloqueadores sobre a árvore oficial;
4. executar protocolos e regressões;
5. promover itens para `CORRIGIDO_HOMOLOGADO` somente com evidência.

## 9. Lacunas que ainda dependem do runtime

Apesar da cobertura conceitual, permanecem sem prova direta suficiente até a reconciliação:

- limites transacionais completos do reprocessamento atual;
- claim/lease real dos workers;
- proteção Auth/CSRF de todas as rotas V8 novas;
- implementação exata do parser IRRF temporal;
- query plans/índices e benchmark final;
- schema/colunas exatas de algumas decisões legadas;
- conteúdo completo do snapshot V4/V8 e sua suficiência após migração;
- cláusula exata que causou a reversão de chamada no caso T L;
- comportamento físico integral do arquivador/gerenciador documental;
- regressão visual/funcional no Windows final.

Essas lacunas são de inspeção/execução, não de definição de regra.

## 10. Regra para a próxima fase

A partir deste ponto, evitar criar novos contratos para temas já cobertos, salvo descoberta realmente nova.

Priorizar:

- evidência de código;
- implementação;
- testes;
- migração em cópia;
- regressão dos 28 casos;
- benchmark;
- instalação/rollback Windows.

`Documentado` não será usado como sinônimo de `implementado`, `testado` ou `homologado`.
