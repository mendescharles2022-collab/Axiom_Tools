# Auditoria canônica V8 — Etapa 35

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 35 consolida B38 — autenticação, CSRF/mecanismo equivalente e autorização das novas mutações V8 — sem declarar falha onde a árvore runtime ainda não foi inspecionada integralmente.

## 2. Evidência disponível

A fundação do produto já estabeleceu login, sessão e proteção das telas internas.

O contrato `CONTRATO_AUTENTICACAO_MUTACOES_V8.md` também já definiu que novas rotas V8 precisam manter o mesmo piso.

Porém o `main` atual não espelha integralmente a árvore operacional V8.

Logo:

- ausência de decorator/dependência no repositório reduzido não prova ausência no runtime;
- B38 permanece `TESTE_PENDENTE_RUNTIME`;
- a homologação deve ocorrer sobre a árvore reconciliada que será empacotada.

## 3. Protocolo criado

Foi criado `PROTOCOLO_SEGURANCA_MUTACOES_V8.md`.

Ele exige inventário rota por rota de:

- método/endpoint;
- autenticação;
- proteção CSRF ou mecanismo apropriado;
- autorização de negócio;
- transação/rollback;
- auditoria;
- idempotência/concorrência;
- escopo afetado.

## 4. Mutações críticas cobertas

A bateria inclui:

- competência/movimento/chamadas;
- decisão por fonte;
- anexar/reprocessar;
- candidatos/retificações;
- jobs/eConsignado;
- inativação/reativação/exclusão;
- aplicação SEFAZ/Sintegra;
- impressão/entrega/saídas automáticas.

## 5. Autorização de negócio

Autenticação não substitui autorização.

A regressão deverá manipular IDs/competência/chamada/versão manualmente e provar bloqueio no backend.

Isso integra B38 com B03, B08, B39 e B40.

## 6. Concorrência

O protocolo inclui escrita obsoleta deliberada:

- request A lê estado N;
- request B grava N+1;
- request A tenta sobrescrever baseado em N;
- a aplicação deve rejeitar/reavaliar a transição.

O caso T L permanece cenário obrigatório desta proteção.

## 7. GET somente leitura

A bateria também verifica que GET/list/detail/search/filter não produzem mutação de negócio.

A Central de Conferência permanece regressão conhecida e deverá zerar deltas de banco após navegação repetida.

## 8. Estado do bloqueador

B38 continua `TESTE_PENDENTE_RUNTIME`.

Não foi marcado como falha confirmada nem como corrigido.

B39 continua `CONFIRMADO_RUNTIME` pelo bypass de seleção de saída já auditado.

## 9. Próxima frente

Auditar proveniência do build e reconciliação da árvore `main` com o runtime, pois todos os protocolos finais dependem de provar que código testado, schema migrado e pacote instalado são o mesmo artefato rastreável.
