# Auditoria canônica V8 — Etapa 16

Data: 28/08/2026
Status: **auditoria em andamento / V8 não homologada**

## 1. Escopo

Esta etapa consolidou a linha histórica de regressões, o contrato de integração entre camadas e a proveniência de build/pacote.

## 2. Linha de regressões V4 → V8

Foi criado `LINHA_TEMPO_REGRESSOES_V4_V8.md`.

Achados principais:

### Regressões de garantias antigas

- V4 já possuía retificação candidata/versionada; V8 permite reprocessamento destrutivo de documento vigente.
- V7 já excluía próxima chamada do ciclo corrente; V8 apresentou T L novamente em chamada 1.
- V7 liberava Impressão/Entregas a partir de `FECHADA`, e V4 bloqueava saída durante retificação; V8 possui caminhos que usam `PROCESSADO` ou não repetem o gate no backend.

Essas falhas recebem prioridade/severidade maior porque quebram comportamento anteriormente validado.

### Comportamentos legitimamente superados

Não são regressões:

- decisão manual global fechando cliente inteiro;
- `PRONTA` sempre apresentada como `Em conferência`;
- fechadas dentro da mesa operacional comum da Conferência.

A V8 substitui essas regras por decisão por fonte, estágio real e mesa de trabalho vivo.

## 3. Padrão recorrente — camadas desconectadas

A auditoria operacional anterior já havia encontrado recursos existentes, porém desconectados entre schema, repository, service e view.

A V8 apresenta padrão semelhante em outras áreas:

- regra de universo duplicada em múltiplas camadas;
- orquestração eConsignado separada;
- gates de saída diferentes;
- documentação/arquitetura à frente de alguns consumidores;
- `main` sem espelhar runtime.

Foi criado `CONTRATO_INTEGRACAO_CAMADAS_V8.md` exigindo regressões ponta a ponta.

## 4. Proveniência de build

Foi confirmado que o `pyproject.toml` do `main` ainda declara versão `0.1.0`, enquanto a linha operacional está em V5.6.14V8/V8F2.

Esse fato, combinado com a divergência entre `main` e ZIP canônico, impede rastreabilidade automática adequada do pacote.

Foi criado `CONTRATO_PROVENIENCIA_BUILD_V8.md` exigindo:

- versão canônica;
- commit SHA;
- schema version;
- manifesto de hashes;
- mesma árvore para teste e empacotamento;
- versão/commit visíveis em runtime/health/log;
- rollback associado à versão anterior.

## 5. Investigação do front operacional

Os logs preservados da instalação mostram no template do Processamento:

- eyebrow `PROCESSAMENTO DE ARQUIVOS`;
- `<h1>` começando com `Aud...` na saída truncada.

A saída não preservou o texto completo. Portanto, **não foi registrado como defeito de nomenclatura** nesta etapa.

Regra de auditoria: texto truncado não é prova suficiente para declarar regressão visual.

## 6. Classificação atual de prioridade

### Crítico

- reprocessamento destrutivo;
- Conference GET com mutação;
- saída sem gate canônico / `PROCESSADO` como validado;
- qualquer migração que destrua decisão/histórico/versão vigente.

### Alto

- universo operacional replicado;
- T L/chamadas;
- composição multi-Extrato/multi-GFD;
- eConsignado fora do universo mensal e falso `CONFERIDO`;
- decisão por fonte ausente;
- MEI/DAE e obrigação zero.

### Médio

- Pendências orientada por PROC em vez de competência;
- A4 retrato;
- nomenclaturas/UX remanescentes;
- performance sem benchmark.

## 7. Estado

Nenhuma das falhas críticas acima está homologada como corrigida.

A próxima etapa da auditoria deve buscar integridade referencial/orfandade no banco e fechar a matriz de invariantes do SQLite para a futura migração V8.
