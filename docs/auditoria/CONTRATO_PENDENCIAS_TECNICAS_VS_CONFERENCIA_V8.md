# Contrato V8 — Pendências técnicas x pendências de Conferência

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Problema confirmado

A auditoria canônica do ZIP registrou que a sessão técnica pode ser persistida como `COM_PENDENCIAS` quando existem documentos em `REVISAO`, enquanto outra camada visual converte a mesma sessão para `PROCESSAMENTO_CONCLUIDO` ao atingir 100%.

Isso produz duas verdades para a mesma execução.

Além disso, a aba `Pendências` ainda expõe contexto técnico de PROC/chaves para o usuário separar a competência corrente, misturando problemas de execução com problemas de negócio.

## 2. Princípio

Separar três dimensões:

```text
ESTADO DA EXECUCAO TECNICA
!=
PENDENCIA TECNICA DO DOCUMENTO/JOB
!=
PENDENCIA DE NEGOCIO DA CONFERENCIA
```

## 3. Estado da sessão técnica

Estados mínimos:

- `NAO_INICIADO`;
- `PROCESSANDO`;
- `PAUSADO`;
- `CONCLUIDO`;
- `CONCLUIDO_COM_FALHA_TECNICA`;
- `INTERROMPIDO`;
- `CANCELADO`.

Percentual representa apenas percurso técnico da sessão.

`100%` significa que todos os itens previstos foram percorridos; não significa que todas as obrigações foram conferidas.

## 4. Pendência técnica

Pertence a Processamento quando existe falha que impede produzir evidência técnica confiável, como:

- arquivo ilegível;
- erro de leitura nativa;
- OCR fallback falhou;
- cliente impossível de identificar com as evidências disponíveis;
- competência tecnicamente indeterminada;
- parser/motor especialista falhou;
- arquivo corrompido;
- falha de persistência;
- falha de conexão/API necessária à execução técnica;
- worker/job interrompido sem conclusão segura.

## 5. Pendência de Conferência

Pertence à Central de Conferência quando a evidência foi tecnicamente processada, mas a realidade operacional ainda exige decisão/cruzamento, como:

- DARF aplicável ausente;
- FGTS divergente;
- múltiplas evidências a compor;
- eConsignado incompatível;
- justificativa por procuração;
- responsabilidade Fiscal;
- afastamento/rescisão a contextualizar;
- documento tecnicamente válido com valor diferente;
- obrigação aplicável sem evidência suficiente de negócio.

## 6. `REVISAO` precisa de qualificação

Um status genérico `REVISAO` não pode decidir sozinho se a sessão técnica tem falha.

A revisão precisa indicar sua natureza, por exemplo:

- `REVISAO_TECNICA`;
- `REVISAO_IDENTIDADE`;
- `REVISAO_COMPETENCIA`;
- `REVISAO_CONFERENCIA`;
- `REVISAO_MATERIALIDADE`.

Somente revisões que representem falha técnica incompleta devem afetar o estado técnico da sessão.

## 7. Monitor de Execução

Tela normal deve priorizar:

1. competência/chamada;
2. etapa/motor atual;
3. progresso técnico durante execução;
4. resultado técnico ao concluir;
5. contador de falhas técnicas;
6. link para detalhes técnicos.

Divergências de DARF/FGTS/eConsignado não devem transformar o Monitor em Central de Conferência.

## 8. Aba Pendências do Processamento

Deve abrir no contexto da competência operacional herdada.

Não exigir do operador PROC/chave técnica para enxergar o ciclo mensal normal.

PROC, IDs e chaves internas ficam em detalhe avançado/diagnóstico.

Separar visualmente:

- pendências técnicas da competência ativa;
- competência não identificada;
- histórico técnico de competências anteriores.

## 9. Encaminhamento à Conferência

Ao terminar processamento técnico de um cliente:

- persistir evidências;
- recalcular aplicabilidade/agregador;
- encaminhar ao estágio correto;
- não copiar pendências de negócio para o status da sessão.

A sessão pode estar `CONCLUIDO` e haver 20 clientes `PENDENTE_DIVERGENTE` na Conferência; isso é coerente.

## 10. Falha técnica x impedimento externo

`SEM_PROCURACAO` no eConsignado/e-CAC, quando a consulta oficial respondeu com esse resultado, é situação operacional auditável, não erro de infraestrutura.

Timeout, erro de rede, resposta inválida ou falha de autenticação técnica configurada são falhas técnicas.

## 11. Regressões mínimas

1. sessão 100% sem erro técnico -> `CONCLUIDO`, mesmo com divergência de Conference;
2. parser falho em item obrigatório -> `CONCLUIDO_COM_FALHA_TECNICA` ou estado equivalente;
3. DARF ausente aplicável não muda sessão para `COM_PENDENCIAS`;
4. FGTS divergente fica na Conference;
5. cliente não identificado fica como pendência técnica até resolução;
6. `SEM_PROCURACAO` não vira erro técnico automaticamente;
7. aba Pendências abre filtrada pela competência ativa;
8. PROC/chave não são filtros primários do fluxo normal;
9. competência não identificada fica em exceção própria;
10. Monitor não exibe duas verdades de status para a mesma sessão.

## 12. Relação com bloqueadores

Principalmente B15, B24, B31, B37, B43 e B46.
