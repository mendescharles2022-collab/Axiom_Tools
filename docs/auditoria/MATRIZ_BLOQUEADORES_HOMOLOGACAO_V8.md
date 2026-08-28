# Matriz de bloqueadores de homologação — V8

Data: 28/08/2026
Status: **controle canônico da auditoria / V8 NÃO HOMOLOGADA**

## 1. Objetivo

Concentrar em um único ponto os bloqueadores que precisam ser resolvidos e comprovados antes de qualquer pacote final da V8.

Classificações de evidência:

- `CONFIRMADO_RUNTIME` — comprovado no ZIP/banco/runtime operacional;
- `REGRESSAO_CONFIRMADA` — garantia anterior validada e quebrada na V8;
- `CONTRATO_OBRIGATORIO` — regra aprovada necessária à correção/homologação;
- `TESTE_PENDENTE_RUNTIME` — não existe prova suficiente nesta sessão para declarar defeito ou correção;
- `CORRIGIDO_HOMOLOGADO` — somente após regressão executada na árvore reconciliada/instalada.

Nenhum item abaixo está marcado `CORRIGIDO_HOMOLOGADO` nesta data.

## 2. Bloqueadores críticos

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B01 | Reprocessamento destrutivo | `reprocessar_arquivo()` remove vigente antes de validar candidato; Jair 449/450 degradados | REGRESSAO_CONFIRMADA | candidato pior rejeitado; vigente preservado; histórico intacto; 449/450 recuperados |
| B02 | Conference GET com mutação | montagem chama sincronização de fechamento | CONFIRMADO_RUNTIME | GET/read da Conference produz zero alterações no banco |
| B03 | Gate único de saída | impressão/entrega/saída possuem proteções diferentes; `PROCESSADO` usado como validado | REGRESSAO_CONFIRMADA | backend bloqueia PRONTA/RETIFICACAO em todos os caminhos; FECHADA correta libera |
| B04 | Versão/retificação vigente | reprocessamento pode degradar estado fechado/histórico | REGRESSAO_CONFIRMADA | versão anterior sempre preservada; retificação material candidata; promoção atômica |
| B05 | Migração V8 | novos estados/decisões por fonte exigem schema seguro | CONTRATO_OBRIGATORIO | migração em cópia, integrity + FK + invariantes, rollback comprovado |
| B06 | Repositório ≠ runtime | `main` não espelha árvore operacional auditada | CONFIRMADO_RUNTIME | árvore reconciliada; mesmo commit testado e empacotado |

## 3. Bloqueadores altos — ciclo e escopo

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B07 | Universo operacional duplicado | SQL direto de fechamento em processing/operations/documents_views | CONFIRMADO_RUNTIME | módulos consomem fachada canônica de Closing; sem filtros paralelos de autorização |
| B08 | T L / 2ª chamada | cliente deveria estar chamada 2 e ficou PRONTA chamada 1 | REGRESSAO_CONFIRMADA | sequência 1→2 persistida; excluída da chamada 1 em todos os módulos; só liberada após avanço global |
| B09 | Fechados na mesa viva | escopo comum inclui FECHADA | CONFIRMADO_RUNTIME | FECHADA só histórico; mudança material vai para retificação própria |
| B10 | Retificação misturada ao ciclo | RETIFICACAO incluída no escopo comum | CONFIRMADO_RUNTIME | área/fluxo próprio de retificação |
| B11 | Estado antecipado | legado PRONTA→Em conferência não reflete estágio real | CONTRATO_OBRIGATORIO | sem evidência processada = aguardando/em processamento, nunca conferência artificial |

## 4. Bloqueadores altos — composição e documentos

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B12 | Multi-Extrato | `_ultimo_tipo(... EXTRATO_MENSAL)` usa um documento apenas | CONFIRMADO_RUNTIME | Jair usa dois extratos corretamente; Leosmar não duplica equivalente |
| B13 | Federal x FGTS rural | Jair federal repetido e FGTS aditivo | CONFIRMADO_RUNTIME | federal R$ 511,43 uma vez; FGTS R$ 389,04; origem por CAEPF preservada |
| B14 | Multi-GFD/FGTS rescisório | casos reais exigem múltiplas evidências | CONTRATO_OBRIGATORIO | mensal/rescisório/antecipado compostos sem duplicar reemissão |
| B15 | Descoberta→vínculo | guias/extratos existentes não chegaram à Conference | CONFIRMADO_RUNTIME | cadeia completa identifica estágio de falha; arquivos novos recompõem Conference |
| B16 | Identidade PF/CAEPF | cadastro já suporta CPF + CAEPF 1:N, processamento perde vínculo | CONFIRMADO_RUNTIME | múltiplos CAEPFs continuam um cliente; inscrição documental preservada |
| B17 | Deduplicação lógica | hash diferente pode ser reemissão equivalente | CONTRATO_OBRIGATORIO | classificar idêntico/reemissão/sucessor/unidade distinta antes de compor valor |

## 5. Bloqueadores altos — aplicabilidade das obrigações

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B18 | Decisão por fonte | decisão global é insuficiente nos casos reais | CONTRATO_OBRIGATORIO | DARF/FGTS/DAE/eConsignado possuem estados independentes; agregado deriva deles |
| B19 | FGTS zero | V8F2 pode exigir guia mesmo com FGTS Domínio zero | CONFIRMADO_RUNTIME | obrigação zero/N/A não cria ausência artificial |
| B20 | MEI/DAE | Elenice ainda passa por lógica genérica FGTS/DARF | CONFIRMADO_RUNTIME | perfil MEI usa DAE e não GFD autônoma padrão |
| B21 | Deduções previdenciárias | Denes/Ponto Kent provam saldo após salário-família | CONTRATO_OBRIGATORIO | `Saldo à recolher` dirige federal; saldo zero não exige DARF |
| B22 | Afastamentos/faltas | casos Gold/Marcos/Wilmar | CONTRATO_OBRIGATORIO | bases/remuneração zeradas explicadas resultam N/A, não incompleto |
| B23 | DARF responsabilidade Fiscal/impedimento RFB | Predileta/Casa Lago Azul/Maria Virginia | CONTRATO_OBRIGATORIO | justificação específica da fonte sem liberar outras obrigações |

## 6. Bloqueadores altos — eConsignado

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B24 | Fora do orquestrador | sync separado do processamento principal | CONFIRMADO_RUNTIME | eConsignado etapa 0 do mesmo ciclo/orquestrador |
| B25 | Universo excessivo | job 08/2026 consultou 840; ciclo tinha 339 | CONFIRMADO_RUNTIME | job usa apenas liberados da competência/chamada |
| B26 | Falso CONFERIDO | D A F Castro | CONFIRMADO_RUNTIME | consulta positiva só conclui após cruzamento contextual |
| B27 | Retorno residual | D&L e outros | CONTRATO_OBRIGATORIO | sem vínculo/remuneração compatível = observação/confirmação, não bloqueio cego |
| B28 | Idempotência/retry | integração externa | CONTRATO_OBRIGATORIO | retry não duplica contratos/resultados; fotografia anterior válida preservada |

## 7. Bloqueadores altos — parser/competência

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B29 | Diretor ≠ empregado | fixture P DA SILVA CARMO | CONFIRMADO_RUNTIME | `Situação: Trabalhando` não cria empregado/FGTS |
| B30 | Federal autoritativo | fixture Domínio | CONFIRMADO_RUNTIME | usar `Apuração Tributos Federais → Saldo à recolher` com proveniência |
| B31 | Competência/proveniência | arquitetura/calendário | CONTRATO_OBRIGATORIO | competência explícita vence heurística; origem/regra persistida |
| B32 | IRRF competência pagamento | documento real aponta semântica específica | TESTE_PENDENTE_RUNTIME | teste comprova associação correta sem assumir cabeçalho de cálculo |
| B33 | dezembro/13º | regra operacional exige exceções | CONTRATO_OBRIGATORIO | calendário versionado/configurável com exceções anuais |

## 8. Bloqueadores de dados/banco

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B34 | `classificacao_inativacao` string/Enum | suíte do ZIP | CONFIRMADO_RUNTIME | aceitar representação prevista; inativar/reativar com histórico e sem tocar filesystem |
| B35 | Foreign keys/invariantes | validation gap | TESTE_PENDENTE_RUNTIME | `integrity_check`, `foreign_key_check` e invariantes lógicas = aprovados |
| B36 | Estado global antigo → fonte | migração necessária | CONTRATO_OBRIGATORIO | legado não é replicado cegamente para todas as fontes; ambiguidades preservadas/revisadas |
| B37 | máquinas de estado misturadas | Monitor + saída + Conference | CONFIRMADO_RUNTIME | sessão/documento/obrigação/ciclo/consulta/retificação separados |

## 9. Bloqueadores de segurança/operacional

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B38 | Auth/CSRF novas rotas V8 | `main` incompleto | TESTE_PENDENTE_RUNTIME | todas as mutações autenticadas/autorizadas/CSRF no código reconciliado |
| B39 | seleção manual por IDs | saídas podem confiar em IDs/filtros | CONFIRMADO_RUNTIME | IDs sempre intersectados com universo permitido no backend |
| B40 | concorrência lógica | múltiplos writers/estado obsoleto | CONTRATO_OBRIGATORIO | transições críticas condicionais/versionadas; job velho não sobrescreve estado novo |
| B41 | backup/rollback | garantia antiga + contrato V8 | CONTRATO_OBRIGATORIO | backup + migração em cópia + restore/rollback testado no Windows |
| B42 | proveniência de build | `main` 0.1.0 vs runtime V5.6.14V8 | CONFIRMADO_RUNTIME | pacote contém versão, commit, schema e hashes; runtime mostra mesmo build |

## 10. Bloqueadores de UX/desempenho

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B43 | Pendências orientada por PROC | V8F2 | CONFIRMADO_RUNTIME | competência ativa como eixo principal; PROC detalhe avançado |
| B44 | relatório A4 retrato | V8F2 | CONFIRMADO_RUNTIME | preview/impressão real sem corte, cabeçalho repetido e quebra controlada |
| B45 | escala >600 clientes | V7 registrou tela pesada | CONFIRMADO_RUNTIME | paginação backend, query plans, sem N+1 explosivo, benchmark representativo |
| B46 | Monitor duplicado/confuso | sessão status duplo e excesso visual | CONFIRMADO_RUNTIME | uma verdade técnica; pendências separadas; detalhes técnicos secundários |
| B47 | Sintegra atalhos | regressão visual confirmada | CONFIRMADO_RUNTIME | Sintegra Nacional e Goiás restaurados e fluxo SEFAZ GO atualizado |

## 11. Bloqueadores de manutenção/acervo

| ID | Tema | Evidência | Estado | Prova mínima para liberar |
|---|---|---|---|---|
| B48 | limpeza/retention | ferramenta futura/solicitada | CONTRATO_OBRIGATORIO | simulação; temporários ≠ evidência; backups/retificações protegidos |
| B49 | banco ↔ filesystem | casos de arquivo existente invisível | CONTRATO_OBRIGATORIO | auditoria bidirecional e ocorrência para item não indexado |
| B50 | hash ≠ obrigação | multi-documento | CONTRATO_OBRIGATORIO | hash identifica bytes; fingerprint lógico identifica fato econômico |

## 12. Critério de liberação

O pacote final só pode ser gerado quando:

1. todos os bloqueadores críticos estiverem `CORRIGIDO_HOMOLOGADO`;
2. todos os bloqueadores altos que afetam competência 08/2026 e os 28 casos estiverem `CORRIGIDO_HOMOLOGADO`;
3. demais itens possuírem regressão aprovada ou justificativa explícita de não bloqueio;
4. árvore de código, testes, schema e instalador forem rastreáveis ao mesmo build;
5. regressão Windows real provar preservação do banco/documentos e rollback.

## 13. Regra de governança

`documentado`, `implementado`, `testado` e `homologado` são quatro estados diferentes.

Nenhum item desta matriz pode mudar para `CORRIGIDO_HOMOLOGADO` apenas porque foi alterado no código ou porque a tela deixou de mostrar o erro.
