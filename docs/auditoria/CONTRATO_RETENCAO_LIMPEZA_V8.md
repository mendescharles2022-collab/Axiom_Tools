# Contrato V8 — Retenção, limpeza e manutenção de arquivos

Data: 28/08/2026
Status: **contrato de auditoria / política final de prazos depende da operação do escritório**

## 1. Princípio central

Limpeza operacional não pode apagar evidência necessária para:

- auditoria;
- reprocessamento;
- conferência;
- retificação;
- rastreabilidade de saída;
- rollback;
- recuperação de falha.

O Axiom Tools já separa estruturalmente `data`, `logs`, `backups`, `documentos` e `temp`. A política de limpeza deve respeitar esses domínios.

## 2. Classificação obrigatória antes de apagar

Todo arquivo gerenciado deve pertencer a uma categoria de retenção, por exemplo:

```text
ORIGINAL_DOCUMENTAL
ARQUIVO_GERENCIADO
VERSAO_HISTORICA
SAIDA_FINAL
TEMPORARIO_PROCESSAMENTO
CACHE_RECONSTRUIVEL
LOG
BACKUP
UPLOAD_TRANSITORIO
```

Rotina de limpeza não pode decidir apenas pela pasta ou idade sem conhecer a categoria.

## 3. Originais e documentos gerenciados

Não apagar automaticamente:

- PDF original ingerido;
- documento que sustenta obrigação/conferência;
- arquivo vinculado a fechamento versionado;
- evidência usada em retificação;
- documento ligado a entrega/impressão auditável.

Se houver política futura de arquivamento externo, a exclusão local só pode ocorrer após comprovação do destino e atualização atômica do vínculo.

## 4. Temporários

Podem ser candidatos à limpeza automática:

- arquivos temporários de merge/preview;
- cópias transitórias de upload já incorporadas com segurança;
- arquivos intermediários de OCR;
- payloads reconstruíveis;
- locks/staging abandonados comprovadamente sem job ativo.

Regras:

- nunca apagar temporário pertencente a job ativo;
- registrar idade mínima;
- preferir limpeza por job concluído + TTL;
- falha de limpeza não deve quebrar a operação principal.

## 5. Cache

Cache reconstruível pode expirar, desde que:

- resultado canônico necessário esteja persistido em outra camada;
- invalidar cache não apague histórico;
- próxima execução consiga reconstruí-lo;
- origem/cache age permaneça explicável enquanto usado.

## 6. Logs

Logs devem ser rotativos, não infinitos.

Política deve considerar:

- retenção suficiente para auditoria operacional e diagnóstico;
- rotação por tamanho/data;
- compressão quando útil;
- não registrar segredos;
- preservar referências de erros relevantes enquanto ainda houver evento de auditoria associado.

Prazo exato é configuração administrativa, não hardcode espalhado.

## 7. Backups

Backups possuem política diferente de temporários.

Rotina automática não deve remover o último backup válido de:

- versão instalada anterior;
- banco anterior a migração;
- versão estável necessária para rollback.

A retenção deve preservar marcos de versão, não somente 'últimos N arquivos'.

Antes de excluir backup antigo:

- validar que há backup posterior íntegro;
- respeitar retenção mínima configurada;
- não excluir backup marcado como protegido/homologação.

## 8. Pastas de entrada/conexões

Arquivos em pastas monitoradas de Domínio/Guias podem ter tratamento operacional de limpeza/organização, mas somente após o Tools conseguir provar:

- hash registrado;
- ingestão concluída;
- cópia/arquivo gerenciado disponível quando exigido;
- vínculo cliente/competência conhecido ou pendência explicitamente preservada;
- nenhuma retificação/candidato depende exclusivamente daquele arquivo na origem.

Não apagar arquivo de origem para 'resolver duplicidade'.

## 9. Competência fechada

Fechar competência não autoriza apagar documentos daquele mês.

Retificação V4/V8 pressupõe capacidade de comparar novo dado com snapshot/evidências anteriores.

Logo, limpeza mensal deve limpar área operacional transitória, não o acervo probatório da competência.

## 10. Candidatos de reprocessamento

Candidato rejeitado pode exigir retenção de metadados e, conforme desenho final, referência ao conteúdo/hash que permitiu reproduzir a rejeição.

Não remover evidência do candidato imediatamente após rejeição se isso impedir auditoria da decisão.

## 11. Saídas geradas

PDFs de impressão/entrega podem ser:

- regeneráveis a partir de documentos + versão de fechamento; ou
- artefatos finais que precisam ser preservados por política operacional.

O sistema deve marcar essa natureza explicitamente.

Se regenerável, pode existir política de expiração da cópia temporária sem apagar o registro do lote/manifesto.

## 12. Limpeza segura — modo simulação

Toda rotina administrativa de limpeza deve possuir:

```text
Simular -> revisar -> confirmar -> executar -> relatório
```

A simulação informa:

- quantidade;
- categoria;
- tamanho;
- idade;
- motivo de elegibilidade;
- arquivos bloqueados e motivo.

## 13. Proteções

Bloquear exclusão quando o arquivo estiver:

- ligado a job ativo;
- único original de documento persistido;
- usado por versão fechada sem cópia segura;
- ligado a retificação pendente;
- ligado a candidato em análise;
- protegido por backup/versionamento;
- fora das raízes permitidas de manutenção.

## 14. Segurança de caminho

Limpeza nunca opera em caminho arbitrário recebido do navegador.

- resolver caminho contra raízes configuradas;
- impedir path traversal;
- tratar junction/symlink/reparse point conforme política Windows;
- não seguir referência para fora da raiz permitida sem validação explícita.

## 15. Auditoria

Cada execução registra:

- usuário/job;
- política aplicada;
- data/hora;
- quantidade elegível;
- quantidade excluída;
- bytes liberados;
- itens ignorados/bloqueados;
- falhas;
- manifesto dos itens removidos ou hash/resumo suficiente conforme política.

## 16. Regressões obrigatórias

1. limpeza não apaga PDF original ligado a fechamento;
2. não apaga evidência de retificação;
3. não apaga arquivo de job ativo;
4. temporário expirado e órfão é removível;
5. cache expirado é reconstruível;
6. último backup válido é protegido;
7. simulação não altera filesystem;
8. caminho fora da raiz é rejeitado;
9. arquivo de origem não identificado não é apagado silenciosamente;
10. após limpeza, invariantes banco ↔ filesystem continuam válidas.

## 17. Critério de aceite

A ferramenta de manutenção não estará homologada enquanto a operação 'limpar' puder significar simplesmente 'apagar arquivos antigos da pasta'.

A exclusão precisa ser orientada por categoria, estado e evidência de segurança.
