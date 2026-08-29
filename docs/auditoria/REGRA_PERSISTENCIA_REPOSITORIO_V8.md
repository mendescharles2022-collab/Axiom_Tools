# Regra de persistência — Auditoria Canônica V8

A partir da continuidade da Auditoria Canônica V8 em 28/08/2026, toda alteração tecnicamente relevante deve ser persistida no repositório `mendescharles2022-collab/Axiom_Tools`, branch `audit-v8-runtime-reconciliation`.

Devem ser versionados, conforme aplicável:

- código-fonte;
- testes;
- scripts de migração, rollback, benchmark e validação;
- contratos técnicos;
- checkpoints de execução;
- evidências reproduzíveis;
- decisões arquiteturais que alterem comportamento;
- correções de CI;
- notas de bloqueadores e critérios de promoção.

Arquivos temporários usados somente para inspeção ou extração não precisam ser copiados ao GitHub quando já existirem na Biblioteca ou quando forem artefatos binários históricos; nesses casos, o repositório deve registrar o nome da fonte, a finalidade da consulta e a conclusão técnica extraída dela.

Nenhum bloqueador pode ser considerado resolvido apenas com informação mantida no chat.

A branch `main` permanece protegida de alterações desta auditoria até que a reconciliação e os gates aplicáveis estejam concluídos.
