# Axiom Tools — Status Atual

Data: 28/08/2026  
Status: **V5.6.14V7 estável em servidor / V8 em auditoria e correção / V8 NÃO HOMOLOGADA**

## 1. Instalação estável confirmada

A referência operacional estável continua sendo:

**V5.6.14V7 — Ciclo Mensal com Fechamento Automático**

A V7 foi instalada no servidor em 26/08/2026 preservando banco, serviços, histórico e retificações.

A existência posterior de builds experimentais/auditados da família V8 não substitui automaticamente essa referência de estabilidade.

## 2. Situação atual da V8

A V8 passou por auditoria funcional, arquitetural, documental e de governança em 28/08/2026.

Resultado atual:

- 50 bloqueadores catalogados (`B01` a `B50`);
- todos possuem regra de tratamento e critério objetivo de prova;
- 28 casos reais da competência 08/2026 foram transformados em matriz de regressão;
- existem protocolos específicos para segurança, migração/rollback, benchmark, regressão dos casos e reconciliação runtime ↔ repositório;
- nenhum bloqueador foi promovido para `CORRIGIDO_HOMOLOGADO` sem execução no runtime reconciliado;
- nenhum pacote final V8 está autorizado.

Estado vivo da fase de correção:

- `docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md`

Mapas e regressão:

- `docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md`
- `docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`
- `docs/auditoria/PROTOCOLO_REGRESSAO_28_CASOS_V8.md`

## 3. Bloqueador de governança — repositório ≠ runtime

O `main` ainda não espelha integralmente a árvore operacional auditada.

Inventário atual do repositório confirma que:

- `src/axiom_tools` contém apenas a fundação reduzida (`core`, `modules`, `utils` e módulos mínimos);
- não estão versionadas na árvore atual as implementações operacionais completas de fechamento, processamento, conferência, entregas e demais módulos V8 auditados no runtime;
- `tests/` ainda não contém a suíte operacional empacotada do runtime auditado;
- `pyproject.toml` ainda não representa corretamente a identidade/versionamento operacional da família V8.

Consequência:

**documentação no GitHub não é prova de correção do runtime.**

Antes da implementação/homologação final é obrigatório reconciliar a árvore operacional com o repositório oficial, sem versionar banco real, documentos de clientes, certificados, credenciais, logs, caches ou outros dados sensíveis.

Contrato/protocolo:

- `docs/auditoria/DIVERGENCIA_REPOSITORIO_BASE_CANONICA_20260828.md`
- `docs/auditoria/PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md`
- `docs/auditoria/CONTRATO_PROVENIENCIA_BUILD_V8.md`

### Tooling de reconciliação já preparado

Foram versionados:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- testes unitários do exportador e auditor;
- testes ponta a ponta do pipeline;
- workflow de CI para a suíte de reconciliação.

Estado de validação dessa infraestrutura:

- 18 testes já aprovados nas revisões executadas;
- 3 testes end-to-end adicionais estão versionados, aguardando execução comprovada;
- total atual definido: 21 testes de reconciliação;
- o workflow GitHub Actions existe, mas nenhum run automático foi observado para os commits feitos pela integração até esta atualização;
- a execução real do launcher PowerShell continua pendente no Windows.

Isso reduz o risco da reconciliação, mas **não muda B06 para resolvido** enquanto o runtime real não for exportado, auditado e incorporado de forma controlada.

## 4. Arquitetura funcional V8 preservada

A divisão aprovada permanece:

1. **Fechamento Mensal** — abre competência e acompanha o ciclo; não processa arquivos.
2. **Processamento de Arquivos** — trabalha somente no universo da competência/chamada aberta e produz evidências técnicas.
3. **Central de Conferência** — resolve divergências, ausências, justificativas, sem movimento mensal, anexos e reprocessamento.
4. **Fechado** — consequência do estado canônico das obrigações aplicáveis, nunca simples tradução de `PROCESSADO`.

A Conferência deve ser leitura sem efeitos colaterais ao abrir a tela. Mudanças de fechamento são dirigidas por eventos de negócio.

## 5. Máquinas de estado separadas

A V8 deve manter separados:

- estado da sessão técnica;
- estado do documento/processamento;
- estado da obrigação/fonte;
- estado do ciclo mensal do cliente;
- estado da consulta externa;
- estado de retificação;
- autorização de saída.

`PROCESSADO`, `100%`, `COM_CONSIGNADO`, `PRONTA` ou qualquer outro estado técnico/intermediário não autorizam impressão, entrega ou fechamento por si sós.

## 6. Regras operacionais centrais já consolidadas

- sem movimento permanente do cadastro ≠ sem movimento daquela competência;
- sem movimento mensal não é herdado silenciosamente no mês seguinte;
- decisões manuais são por fonte/obrigação, não globais por cliente;
- uma justificativa de DARF não libera FGTS/eConsignado;
- cliente de 2ª chamada fica fora do universo da 1ª chamada;
- cliente fechado não pertence à mesa viva de Conferência;
- nova evidência material em cliente fechado gera retificação candidata e preserva a versão anterior;
- saída final exige gate único de backend e versão de fechamento autorizadora;
- FGTS zero pode ser `NAO_APLICAVEL` conforme o contexto;
- MEI usa DAE como referência normal e não cria expectativa artificial de GFD autônoma;
- afastamento integral/faltas integrais com bases zeradas não devem gerar guias artificiais;
- eConsignado consulta apenas o universo da competência/chamada e o retorno da API é evidência, não conclusão;
- hash identifica conteúdo físico; não define sozinho identidade econômica da obrigação;
- limpeza mensal não apaga acervo probatório, versões, retificações ou documentos de fechamento.

## 7. Casos reais de agosto

A matriz de 08/2026 possui 28 casos reais e um controle adicional documental.

Ela cobre, entre outros:

- reprocessamento e promoção de candidato;
- retificação;
- chamadas mensais;
- produtor rural PF/CAEPF;
- múltiplos Extratos/matrículas;
- MEI/DAE;
- FGTS zero;
- deduções previdenciárias;
- afastamentos e faltas integrais;
- responsabilidade do Fiscal;
- procuração revogada/expirada;
- eConsignado e rescisão;
- múltiplas evidências de FGTS;
- descoberta → leitura → identidade → competência → vínculo → Conferência.

Nenhum desses casos pode ser considerado corrigido apenas porque uma ocorrência deixou de aparecer na tela.

## 8. Ordem oficial da fase de correção

Após reconciliação do runtime com o repositório:

1. estabelecer baseline reproduzível e rodar suíte original;
2. corrigir B01 — reprocessamento candidato/versionado;
3. corrigir B02 — Conference GET somente leitura;
4. corrigir B03 — gate único de saída;
5. corrigir B07/B08 — universo operacional e chamadas;
6. corrigir B12–B20 — identidade, composição, aplicabilidade e documentos;
7. corrigir B24–B28 — eConsignado;
8. concluir schema/migração aditiva e invariantes;
9. executar regressão completa dos 28 casos;
10. executar benchmark de escala;
11. validar segurança das rotas V8;
12. gerar pacote somente da mesma árvore testada;
13. instalar no Windows com backup, migração em cópia, smoke e rollback comprovado.

## 9. Critério para mudar status de um bloqueador

Um item só pode passar para `CORRIGIDO_HOMOLOGADO` quando houver:

1. código corrigido na árvore oficial;
2. teste/regressão executado;
3. evidência do resultado;
4. atualização do mapa/matriz de bloqueadores;
5. ausência de regressão nos casos relacionados.

`Documentado`, `contratado`, `implementado` e `homologado` são estados diferentes.

## 10. Estado de entrega

Neste momento:

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback final **não comprovado**;
- árvore runtime **ainda não reconciliada integralmente com o GitHub**.

A documentação de auditoria no `main` e o rastreador canônico são a referência das regras e do andamento até que a árvore operacional completa seja reconciliada e testada.
