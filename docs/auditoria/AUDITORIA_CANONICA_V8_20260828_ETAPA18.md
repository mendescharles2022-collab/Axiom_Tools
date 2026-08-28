# Auditoria canônica V8 — Etapa 18

Data: 28/08/2026
Status: **auditoria em andamento / pacote final não autorizado**

## 1. Escopo

Esta etapa consolidou política de retenção/limpeza e encerrou uma lacuna operacional importante: diferenciar limpeza de temporários de exclusão de evidência documental/histórica.

## 2. Estrutura persistente já existente

A fundação do Axiom Tools já separa, no servidor:

- `data`;
- `logs`;
- `backups`;
- `documentos`;
- `temp`.

Essa separação deve ser preservada pela V8 e utilizada pela política de retenção.

## 3. Contrato criado

Foi criado `CONTRATO_RETENCAO_LIMPEZA_V8.md`.

O contrato classifica arquivos antes de qualquer exclusão:

- original documental;
- arquivo gerenciado;
- versão histórica;
- saída final;
- temporário de processamento;
- cache reconstruível;
- log;
- backup;
- upload transitório.

## 4. Regra central

Fechar uma competência não autoriza apagar os documentos daquele mês.

A própria arquitetura de retificação exige capacidade de comparar novo dado com versão/evidência anterior.

Portanto, uma futura ferramenta de limpeza mensal deve limpar **área operacional transitória**, não o acervo probatório.

## 5. Proteções obrigatórias

Não apagar automaticamente arquivo que esteja:

- ligado a fechamento/versionamento;
- ligado a retificação pendente;
- ligado a candidato de reprocessamento em análise;
- sendo usado por job ativo;
- sendo o único original persistido;
- sendo o último backup válido para rollback;
- fora das raízes autorizadas de manutenção.

## 6. Limpeza como fluxo auditável

A operação deve seguir:

`Simular -> revisar -> confirmar -> executar -> relatório`

A simulação deve informar o que seria removido, categoria, tamanho, idade e motivo de elegibilidade.

## 7. Arquivos de origem monitorados

Arquivos presentes nas conexões/pastas de entrada somente podem ser removidos/organizados depois de comprovados:

- hash registrado;
- ingestão concluída;
- vínculo ou pendência preservada;
- cópia gerenciada quando necessária;
- nenhuma retificação/candidato depende exclusivamente daquele original na origem.

Não usar exclusão como forma de resolver duplicidade.

## 8. Estado de evidência

Nesta sessão não foi recuperada implementação produtiva específica de uma ferramenta de limpeza mensal para inspecionar linha a linha.

Assim:

- **não é declarado defeito em uma rotina inexistente/não recuperada**;
- o contrato passa a ser obrigatório antes de implementar ou homologar tal ferramenta.

## 9. Relação com reprocessamento

A política de retenção reforça o reprocessamento candidato/versionado:

- rejeitar candidato não apaga a versão vigente;
- preservar metadados/evidência suficiente do candidato rejeitado;
- hash e arquivo físico permanecem rastreáveis;
- limpeza posterior só ocorre conforme política, nunca como efeito colateral do reprocessamento.

## 10. Estado final

A V8 permanece NÃO HOMOLOGADA.

Próximo passo da auditoria: consolidar matriz única de bloqueadores de homologação e, em seguida, aprofundar deduplicação documental e ciclo de vida dos jobs/workers.
