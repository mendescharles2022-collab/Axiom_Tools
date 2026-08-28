# Protocolo executável — Migração, integridade e rollback V8

Data: 28/08/2026
Status: **protocolo de homologação / execução pendente no Windows runtime reconciliado**

## 1. Objetivo

Unificar em uma sequência executável os contratos de:

- schema/migração aditiva;
- invariantes do SQLite;
- instalação/backup/rollback;
- proveniência do build.

Nenhum pacote V8 pode ser liberado sem percorrer esta sequência sobre uma cópia realista e depois no ambiente Windows alvo.

## 2. Identificação do build

Antes de qualquer migração registrar:

- versão do pacote;
- commit exato;
- hash do manifesto/payload;
- versão/schema alvo;
- data/hora da build;
- versão mínima de origem suportada.

O mesmo build deve ser usado na migração testada e na instalação final.

## 3. Inventário baseline

Na base origem, coletar com Python `sqlite3`:

- caminho/tamanho/hash do banco;
- `PRAGMA user_version` ou versão de schema equivalente;
- lista de tabelas;
- lista de índices;
- contagens das tabelas críticas;
- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- invariantes lógicas baseline.

Também registrar estado das competências, principalmente 08/2026:

- participantes;
- status por cliente;
- chamadas;
- versões;
- retificações;
- documentos/processamentos;
- decisões/histórico;
- jobs/fotografias eConsignado quando existentes.

## 4. Backup consistente

Antes da mudança:

- suspender novas mutações;
- parar/pausar workers;
- garantir encerramento de conexões relevantes;
- criar backup do banco por método consistente;
- guardar código/configurações necessários ao rollback;
- gerar manifesto com hashes.

Não confiar em simples cópia de arquivo SQLite enquanto processos ainda escrevem nele.

## 5. Migração em cópia

Criar cópia de homologação do banco baseline e executar a migração V8 nela.

A migração deve ser:

- aditiva;
- reproduzível;
- idempotente quando a política permitir nova execução segura;
- sem reprocessar PDFs reais apenas para preencher schema;
- sem fabricar estados por fonte a partir de decisão global ambígua;
- sem apagar históricos antigos.

## 6. Validação pós-migração em cópia

Executar:

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

Depois executar invariantes lógicas de:

- Clientes/inscrições;
- Fechamento Mensal;
- versões/retificações;
- processamento/documentos;
- obrigações por fonte;
- eConsignado;
- saídas;
- auditoria/histórico;
- banco ↔ filesystem quando aplicável.

## 7. Comparação baseline × migrado

Gerar diff de contagens e estados.

Diferença só é aceita se:

- prevista pela migração;
- explicada no relatório;
- não representar perda de histórico/documento/cliente;
- não transformar ambiguidade legada em falsa certeza.

Verificações mínimas:

- clientes não desaparecem indevidamente;
- 08/2026 mantém participantes/status/chamadas coerentes;
- FECHADA mantém versão correspondente;
- retificações permanecem;
- histórico 449/450 permanece recuperável;
- decisões globais antigas não viram justificativa automática de todas as fontes;
- documentos físicos não são alterados.

## 8. Regressão funcional da cópia migrada

Antes de tocar o banco operacional:

- rodar suíte automatizada;
- executar regressões críticas dos 28 casos;
- testar Conference GET sem escrita;
- gate único de saída;
- reprocessamento candidato;
- mudança de chamada;
- eConsignado limitado ao ciclo;
- inativação string/Enum;
- MEI/DAE;
- multi-documento Jair/FGTS.

## 9. Ensaio de rollback

Sobre ambiente de teste:

1. instalar/migrar;
2. confirmar novo schema;
3. simular condição de rollback;
4. restaurar código anterior + banco anterior + configurações compatíveis;
5. iniciar serviços;
6. verificar integridade;
7. abrir funções essenciais;
8. comparar hash/estado esperado.

Rollback não é considerado comprovado apenas porque existe pasta `backup`.

## 10. Aplicação operacional

Somente após a cópia passar:

1. bloquear operação;
2. criar novo backup consistente do banco operacional atual;
3. aplicar o mesmo build testado;
4. migrar o banco;
5. rodar checks de integridade;
6. iniciar serviços;
7. executar smoke;
8. executar regressão crítica curta;
9. somente então liberar usuários/workers.

## 11. Smoke mínimo Windows

- backend/gateway iniciam;
- login/sessão funcionam;
- Clientes abre;
- Fechamento abre sem mutação;
- Processamento herda competência;
- Conferência abre somente leitura;
- banco íntegro;
- worker inicia sem job duplicado;
- gate bloqueia saída não autorizada;
- nenhuma migração fica pendente silenciosamente.

## 12. Gatilhos de rollback imediato

- `integrity_check` diferente de `ok`;
- violações FK novas;
- invariantes críticas falham;
- perda de cliente/documento/histórico;
- FECHADA sem versão;
- retificação perdida;
- serviços não iniciam de forma confiável;
- gate de saída falha;
- reprocessamento destrutivo permanece;
- regressão crítica dos casos reais.

## 13. Relatório obrigatório

Salvar por instalação:

- build/commit/hash;
- baseline do banco;
- backup gerado;
- resultado da migração em cópia;
- checks SQL;
- invariantes;
- regressões;
- resultado do ensaio de rollback;
- instalação operacional;
- smoke final;
- conclusão PASS/FAIL.

## 14. Critério de homologação

B05, B35 e B41 só podem ser marcados `CORRIGIDO_HOMOLOGADO` quando este protocolo for executado com sucesso sobre a mesma árvore/pacote que será usado no servidor.
