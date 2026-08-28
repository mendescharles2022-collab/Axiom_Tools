# Auditoria canônica V8 — Etapa 21

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa consolidou quatro regras transversais que ainda estavam fragmentadas:

- agregação do fechamento por fonte;
- aplicabilidade das obrigações;
- máquina de estados do cliente mensal;
- elegibilidade/composição mensal e ciclo de vida do cliente.

## 2. Agregador único do fechamento

Foi criado `CONTRATO_AGREGADOR_FECHAMENTO_POR_FONTE_V8.md`.

O estado agregado do cliente deve derivar das obrigações aplicáveis.

Uma fonte resolvida não encerra outra.

`PROCESSADO` e `100%` técnico não significam `FECHADA`.

## 3. Matriz de aplicabilidade

Foi criado `CONTRATO_MATRIZ_APLICABILIDADE_OBRIGACOES_V8.md`.

Regra central:

```text
primeiro determinar se a obrigação é aplicável e seu resultado esperado;
depois verificar se o documento necessário existe.
```

Isso cobre as falsas pendências observadas em:

- MEI/DAE;
- diretor/pró-labore sem empregados;
- afastamentos integrais;
- faltas integrais;
- saldo federal zero por deduções;
- rescisões e múltiplas evidências FGTS;
- DARF sob responsabilidade Fiscal;
- impedimento por procuração;
- eConsignado contextual.

## 4. Máquina de estados mensal

Foi criado `CONTRATO_TRANSICOES_ESTADO_CLIENTE_MENSAL_V8.md`.

Regras centrais:

- competência nova não antecipa `EM_CONFERENCIA`;
- GET é somente leitura;
- FECHADA só nasce do agregador + snapshot;
- nova mudança material em FECHADA leva a RETIFICACAO, nunca volta silenciosamente para PRONTA;
- próxima chamada sai do universo atual imediatamente;
- workers antigos não podem desfazer mudança mais nova;
- `Sem movimento` é mensal, reversível e auditável.

Foi acrescentado controle de revisão/optimistic locking como requisito de escrita.

## 5. Ciclo de vida de Clientes x histórico do Fechamento

Foi criado `CONTRATO_CICLO_VIDA_CLIENTE_HISTORICO_V8.md`.

Novo achado arquitetural:

A AXT-003 permitiu exclusão administrativa real do cadastro mestre. Depois, Fechamento/retificação/saídas passaram a depender de `cliente_id` histórico.

Portanto:

- exclusão do cadastro continua possível administrativamente;
- filesystem continua preservado;
- porém fechamento, versões, retificações, decisões, auditoria e saídas históricas não podem ser apagados por cascade;
- identidade histórica precisa sobreviver por snapshot/tombstone ou estratégia equivalente.

## 6. Evolução da elegibilidade mensal

Foi criado `CONTRATO_ELEGIBILIDADE_COMPOSICAO_MENSAL_V8.md`.

### Evidência V6

V6 dizia: todos os clientes ativos entram automaticamente na 1ª chamada.

### Evidência do runtime posterior

`closing/service.py` possui indicação de que `NAO_SE_APLICA` fica fora do fechamento mensal.

### Arquitetura V8

Estar cadastrado no Tools não significa participar automaticamente do fechamento.

Conclusão: houve evolução da regra e ela precisa ser centralizada em um único serviço de elegibilidade.

## 7. Quatro conceitos que não podem mais ser confundidos

```text
cliente não elegível para o fechamento
!=
cliente participante sem movimento
!=
cliente participante em próxima chamada
!=
obrigação específica não aplicável
```

Misturar esses conceitos produz contagens erradas, consultas excessivas e falsas pendências.

## 8. Contagem da competência

A auditoria de 08/2026 registrou 339 participantes, número muito inferior à carteira total.

Isso confirma que existe seleção operacional além da simples existência cadastral.

A regra SQL completa que gera essa composição ainda não foi recuperada do ZIP/runtime e permanece para inspeção; não foi inferida por aproximação.

## 9. Casos reais protegidos nesta etapa

- T L Empreendimentos Agrícolas — 2ª chamada;
- Elenice/Luriel — MEI/DAE;
- Jair — múltiplos CAEPF/matrículas;
- P DA SILVA CARMO — diretor não é empregado;
- Gold Pallace/Marcos/Wilmar — zero legítimo;
- Alex Douglas — rescisão e aplicabilidade por fonte;
- Predileta — responsabilidade Fiscal;
- Casa das Carnes/Maria Virginia — impedimento externo por fonte;
- D A F Castro e correlatos — eConsignado contextual.

## 10. Impacto em homologação

Os contratos desta etapa devem virar testes integrados, não apenas unitários.

É obrigatório provar no runtime reconciliado:

1. mesmo universo em todos os módulos;
2. motivo de inclusão/exclusão explicável;
3. máquina de estados sem transição por GET;
4. decisão por fonte;
5. fechamento agregado + snapshot;
6. inativação/exclusão sem destruir história;
7. optimistic locking contra escrita obsoleta;
8. regressão dos casos reais.

## 11. Estado final

Nenhum ponto desta etapa está `CORRIGIDO_HOMOLOGADO` apenas por ter sido documentado.

A V8 permanece não homologada e nenhum pacote final está autorizado.
