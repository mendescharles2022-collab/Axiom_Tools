# Auditoria canônica V8 — Etapa 17

Data: 28/08/2026
Status: **auditoria em andamento / pacote final bloqueado**

## 1. Escopo

Esta etapa fechou três lacunas horizontais:

- integração entre camadas;
- integridade/invariantes do banco;
- separação das máquinas de estado.

## 2. Integração ponta a ponta

Foi criado `CONTRATO_INTEGRACAO_CAMADAS_V8.md`.

A motivação é histórica e atual: o Axiom Tools já apresentou defeitos em que schema, repository, service, provider e view existiam, porém estavam desconectados. A V8 volta a mostrar sinais desse padrão em Fechamento, Processamento, eConsignado e saídas.

Nenhuma funcionalidade será aceita apenas porque seu método/tabela/tela existe; o efeito de negócio completo precisa ser testado.

## 3. Banco — lacuna de validação

Foi criado `CONTRATO_INVARIANTES_BANCO_V8.md`.

A fundação antiga já habilita foreign keys/WAL e versões anteriores executaram `integrity_check`.

Não foi encontrada nesta sessão evidência de execução de `foreign_key_check` e de invariantes lógicas completas do fechamento/processamento.

Isso não significa que existam órfãos; significa que a homologação deve verificar:

- integridade estrutural;
- foreign keys;
- vínculos lógicos de fechamento/versionamento;
- documentos/arquivos;
- obrigações;
- jobs;
- saídas autorizadas.

## 4. Máquinas de estado

Foi criado `CONTRATO_MAQUINAS_ESTADO_V8.md`.

A V8 deve separar explicitamente:

1. sessão técnica de processamento;
2. documento individual;
3. obrigação/fonte na Conferência;
4. ciclo mensal do cliente;
5. resultado de consulta externa;
6. retificação;
7. autorização derivada de saída.

## 5. Defeito confirmado do Monitor

A auditoria canônica já comprovou duas verdades para a mesma sessão:

- persistência pode registrar `COM_PENDENCIAS` pela existência de documento em `REVISAO`;
- camada de apresentação mostra `PROCESSAMENTO_CONCLUIDO` quando chega a 100%.

Isso é mistura de estado técnico com resultado da Conferência.

A correção deve deixar o status técnico único e mover pendências de negócio para sua máquina apropriada.

## 6. Relação com casos reais

A separação de estados resolve estruturalmente situações como:

- DARF justificada e FGTS ainda pendente;
- eConsignado consultado, mas ainda divergente;
- documento processado tecnicamente sem cliente fechado;
- cliente em chamada futura com documentos já existentes;
- retificação candidata sem substituir a versão fechada;
- sessão concluída com ocorrências ainda abertas na Conferência.

## 7. Estado

Continuam críticos e não homologados:

- reprocessamento candidato/versionado;
- Conference GET read-only;
- gate único de saída;
- universo canônico;
- recuperação Jair 449/450;
- composição multi-documento;
- decisão por fonte;
- eConsignado contextual;
- chamadas;
- regressão dos 28 casos;
- reconciliação do repositório com runtime;
- migração e instalação final.

Próximo eixo: retenção/limpeza operacional e garantia de que rotinas de manutenção não apaguem evidências necessárias à auditoria, retificação e reprocessamento.
