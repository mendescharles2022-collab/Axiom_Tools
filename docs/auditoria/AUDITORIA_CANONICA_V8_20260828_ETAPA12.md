# Auditoria canônica V8 — Etapa 12

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo

A Etapa 12 auditou o contrato entre:

- arquivo físico;
- hash;
- processamento;
- versões de extração;
- evidências da Conferência;
- snapshots de fechamento;
- retificações.

## 2. Princípio permanente preservado

A base homologada anterior já determinava:

- nunca excluir automaticamente arquivo original;
- nunca sobrescrever silenciosamente arquivo existente;
- nunca mover/renomear legado sem confirmação;
- cadastro, pasta e documentos são domínios distintos.

Essas regras permanecem vinculantes para o processamento V8.

## 3. Separação necessária

A V8 deve distinguir:

```text
arquivo físico
registro de processamento
versão da extração
evidência da obrigação
```

Reprocessar o mesmo PDF não exige duplicar fisicamente o arquivo.

Novo arquivo físico com mesmo nome não significa mesmo conteúdo.

## 4. Hash

Hash de conteúdo identifica igualdade física, mas não igualdade econômica.

Regras:

- hash igual = mesmo conteúdo byte a byte;
- hash diferente pode ser reemissão da mesma obrigação;
- caminho/nome não é chave suficiente;
- mudança de hash em caminho conhecido deve ser tratada como mudança real e versionada.

## 5. Reprocessamento

Para o mesmo arquivo físico:

- versão vigente de extração permanece;
- candidato aponta para o mesmo hash;
- promoção/rejeição muda apenas a interpretação vigente;
- físico não é sobrescrito como efeito do reprocessamento.

Isso complementa a correção do caso Jair.

## 6. Reemissão x componente aditivo

A relação documental deve distinguir:

- reemissão equivalente;
- sucessora;
- matrícula/unidade distinta;
- evidência complementar;
- natureza econômica distinta.

Essa classificação acontece antes de somar/deduplicar valores.

## 7. Arquivamento gerenciado

Se houver cópia para área gerenciada, exigir:

- escrita temporária;
- validação de hash/tamanho;
- promoção segura;
- colisão de nome sem overwrite;
- origem preservada;
- falha não remove origem.

O código integral desta camada não foi recuperado nesta sessão, então não foi atribuído defeito físico sem prova.

## 8. Retificação

Snapshot antigo continua ligado às evidências antigas.

Nova retificação aponta para novas evidências/candidatas.

Não reescrever retroativamente o conjunto de documentos usado por fechamento anterior.

## 9. Limpeza mensal

Qualquer futura limpeza deve distinguir temporário/cache de acervo permanente.

Documento referenciado por fechamento, retificação ou auditoria não pode ser apagado como limpeza comum.

## 10. Segurança de caminho

Preview/Impressão devem resolver arquivo a partir de referência autorizada do banco e não aceitar caminho arbitrário fornecido pelo navegador.

Path traversal e colisão de nomes entram na regressão de segurança.

## 11. Documento produzido

- `CONTRATO_ACERVO_FISICO_VERSIONAMENTO_V8.md`;
- este documento.

## 12. Estado ao final da Etapa 12

A integridade lógica do acervo está contratada, mas a implementação física precisa ser confrontada diretamente na árvore canônica.

Pendências específicas:

- confirmar hash/persistência no processamento V8;
- confirmar comportamento do arquivador em colisões;
- confirmar inexistência de sobrescrita física em reprocessamento;
- confirmar vínculo de snapshot antigo com evidência antiga;
- testar preview/path traversal;
- testar limpeza sem perda de acervo.

Nenhum pacote V8 deve ser liberado antes da regressão integral.
