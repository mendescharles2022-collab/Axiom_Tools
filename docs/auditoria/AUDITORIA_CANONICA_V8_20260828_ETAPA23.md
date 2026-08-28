# Auditoria canônica V8 — Etapa 23

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa aprofundou:

- payload real do snapshot/versionamento V4;
- suficiência desse snapshot para os requisitos V8;
- acoplamento entre cadastro mestre e Fechamento/Retificação;
- investigação da transição de chamadas relacionada ao caso T L Empreendimentos Agrícolas.

## 2. Versionamento V4 — existência confirmada

A evidência do runtime confirma `retification.py` com:

- criação de `fechamento_mensal_versao`;
- criação de `fechamento_mensal_retificacao`;
- leitura de `MAX(versao)`;
- `INSERT INTO fechamento_mensal_versao(competencia, cliente_id, versao, natureza, snap...)`;
- atualização de `versao_atual`;
- conclusão de retificação;
- consulta da versão base;
- detecção de retificação existente;
- backfill de FECHADA sem versão.

O relatório V4 comprova que snapshot, materialidade, Vn→Vn+1 e bloqueio de saída foram testados em cópia real do SQLite.

## 3. Payload do snapshot — limite da evidência

As buscas recuperaram o início do campo `snap...`, mas não o DDL completo nem a função integral que monta o snapshot.

Também não foi possível recuperar a granularidade interna que representa:

- identidade histórica;
- inscrições/matrículas;
- decisão por fonte;
- composição multi-documento;
- proveniência documental;
- versão de schema do snapshot.

Conclusão:

> **Versionamento V4 comprovado. Suficiência do payload para V8 ainda NÃO comprovada.**

Foi criado anteriormente `CONTRATO_CONTEUDO_SNAPSHOT_FECHAMENTO_V8.md` para definir o mínimo necessário sem inventar que o schema legado já atende.

## 4. Acoplamento Clientes ↔ Fechamento/Retificação — confirmado

Evidência de runtime:

- `closing/service.py`: `fechamento_mensal_cliente f JOIN clientes c ON c.id=f.cliente_id`;
- `closing/retification.py`: `fechamento_mensal_retificacao r JOIN clientes c ON c.id=r.cliente_id`;
- `closing/service.py` histórico: `fechamento_mensal_historico h LEFT JOIN clientes c ON c.id=h.cliente_id`.

Isso prova dependências semânticas diferentes:

- o histórico tolera ausência do cadastro atual;
- a visão mensal e retificação ativa dependem do cadastro existir.

Foi criado `ACHADO_ACOPLAMENTO_CLIENTES_FECHAMENTO_RETIFICACAO_V8.md`.

## 5. Conflito com exclusão administrativa

A AXT-003 original autorizava exclusão de cliente inclusive com histórico, removendo dependências de FK conforme a política daquele momento.

Depois o produto passou a possuir Fechamento, snapshots, retificações e saídas.

Logo, a política antiga não pode ser aplicada cegamente às entidades novas.

A correção precisa preservar identidade histórica e não pode se resumir a trocar `JOIN` por `LEFT JOIN`.

## 6. T L Empreendimentos — investigação da chamada

Evidência do runtime em `closing/service.py`:

1. há `UPDATE fechamento_mensal SET chamada_atual=?` na região da linha 202;
2. logo depois há `UPDATE fechamento_mensal_cliente SET status='PRONTA', chamada=?` na região da linha 205.

Esse bloco é compatível com uma rotina que libera/avança a chamada.

Porém a cláusula `WHERE` completa e o nome da função não foram recuperados.

Portanto:

- é possível afirmar que existe um ponto de código que reclassifica clientes para `PRONTA` ao redor da mudança da chamada atual;
- **não é possível afirmar ainda que esse ponto específico causou a regressão da T L**.

O diagnóstico causal permanece aberto até inspeção do código integral.

## 7. Regra de proteção já definida

Independentemente da causa específica, o contrato V8 exige:

- decisão de chamada persistida e auditada;
- cliente de 2ª chamada fora da 1ª imediatamente;
- avanço de chamada libera somente o universo correspondente;
- worker/sincronização com estado antigo não pode desfazer decisão posterior;
- optimistic locking/revisão em mutações de chamada.

## 8. Provas de runtime ainda necessárias

1. DDL completo de `fechamento_mensal_versao`;
2. função que monta snapshot;
3. conteúdo de snapshots reais;
4. FKs e `ON DELETE` das tabelas de closing;
5. exclusão de cliente com histórico em cópia do banco;
6. cláusula `WHERE` completa do `UPDATE status='PRONTA'`;
7. nome e contrato da rotina de avanço de chamada;
8. reprodução do caso T L com histórico de transições.

## 9. Estado

Nenhuma correção de código foi declarada.

V8 permanece NÃO HOMOLOGADA e nenhum pacote final está autorizado.
