# Contrato V8 — Homologação, regressão e rastreabilidade da entrega

Data: 28/08/2026
Status: **contrato obrigatório para encerramento da auditoria V8**

## 1. Princípio

A V8 não pode ser homologada por uma única evidência isolada, como:

- backend iniciou;
- gateway respondeu;
- instalador terminou;
- tela abriu;
- um teste específico ficou verde;
- relatório foi gerado;
- commit documental foi criado.

Homologação exige coerência entre **fonte que será empacotada, banco/migração, regressão automatizada, casos reais, instalador e runtime Windows**.

## 2. Lição preservada da Auditoria Operacional V4

A Auditoria Operacional V4 registrou uma disciplina de validação que deve ser mantida ou ampliada na V8:

- suíte local de módulos/db/utils/validators/integrations/maintenance/audit/gateway;
- 252 testes aprovados naquela fotografia;
- `compileall` de código e scripts;
- validação sintática de templates Jinja;
- validação de JavaScript;
- schema em banco vazio;
- migração sobre cópia da base existente;
- smoke web usando o `venv` real do servidor;
- rollback quando o smoke falha.

A V8 possui muito mais regras de negócio que a V4, portanto não pode reduzir esse nível de controle.

## 3. Problema atual de rastreabilidade

O branch `main` atual não espelha integralmente a árvore operacional do ZIP canônico auditado.

Logo, antes da correção final é obrigatório reconciliar:

```text
fonte oficial
= árvore testada
= árvore empacotada
= árvore instalada
```

Documentação no GitHub não substitui código operacional sincronizado.

## 4. Matriz de tipos de teste

### A. Testes unitários

Cobrir regras isoladas:

- normalização/identidade;
- parser Domínio;
- IE;
- estados por fonte;
- política de promoção de candidato;
- consolidação federal/FGTS;
- gate de saída;
- normalização Enum/string;
- eConsignado.

### B. Testes de integração

Cobrir cadeia entre componentes:

- descoberta -> leitura -> identidade -> persistência;
- Processamento -> Conferência;
- Fechamento -> eConsignado;
- Conferência -> gate de saída;
- Cadastro -> inscrições -> Processamento;
- retificação -> bloqueio de saída.

### C. Regressão de casos reais

Executar a matriz de 28 casos de agosto, mais controles adicionais como Jair/Leosmar/P DA SILVA CARMO.

### D. Migração de banco

Executar sobre:

- banco vazio;
- cópia do banco canônico;
- cópia de banco com histórico/reprocessamentos;
- validar `PRAGMA integrity_check` e invariantes de contagem/relacionamentos.

### E. Smoke web

No ambiente Windows/venv que será usado para atualização:

- login;
- Dashboard;
- Clientes;
- Fechamento Mensal;
- Processamento;
- Conferência;
- Impressão;
- Entregas;
- eConsignado;
- atalhos/consulta Sintegra;
- inativação/reativação;
- rotas críticas sem 500.

### F. Teste de instalador

- backup antes de alteração;
- preservação de `data` e documentos;
- migração segura;
- inicialização dos serviços;
- smoke pós-instalação;
- rollback quando etapa crítica falhar.

## 5. Classificação das falhas da suíte

Cada falha deve ser classificada antes de alterar produção:

- `FALHA_FUNCIONAL_REAL`;
- `TESTE_LEGADO_SUPERADO_PELA_V8`;
- `FALHA_AMBIENTAL_WINDOWS/LIB_NATIVA`;
- `FLAKY/NAO_REPRODUZIDA`;
- `RISCO_NAO_CONFIRMADO`.

Nenhum teste deve ser alterado apenas para ficar verde.

Teste legado só muda quando existir contrato posterior documentado e regressão substituta.

## 6. Invariantes de dados

A homologação deve provar, no mínimo:

- nenhum documento físico apagado pela atualização;
- histórico de fechamento preservado;
- histórico de reprocessamento preservado;
- versões vigentes/candidatas coerentes;
- clientes/inscrições mantidos;
- pastas físicas não destruídas por inativação/exclusão cadastral;
- retificações preservadas;
- competência/chamada mantidas;
- contagens críticas explicadas antes/depois.

## 7. Regressão obrigatória de segurança operacional

1. abrir Conferência não escreve no fechamento;
2. seleção por ID não burla gate;
3. POST direto de Entregas não burla gate;
4. `PROCESSADO` não libera saída;
5. candidato pior não substitui versão vigente;
6. retificação bloqueia saída nova;
7. mudança para 2ª chamada persiste imediatamente;
8. decisão de uma fonte não resolve outra;
9. eConsignado da 1ª chamada não consulta universo histórico inteiro;
10. inativação preserva filesystem e histórico.

## 8. Regressão obrigatória dos motores

### Domínio

- P DA SILVA CARMO;
- 2A Peças;
- Jair 449/450;
- saldo zero por dedução;
- diretor/pró-labore sem FGTS;
- IRRF por competência de pagamento como teste específico.

### eConsignado

- D A F Castro;
- D&L Alimentos;
- GL Auto Center;
- casos com rescisão/garantias;
- SEM_CONSIGNADO e SEM_PROCURACAO.

### FGTS

- mensal;
- zero/não aplicável;
- rescisório;
- antecipado;
- múltiplas evidências;
- reemissão sem duplicação;
- rural PF/múltiplas matrículas.

### DARF/e-CAC

- documento adicionado depois;
- saldo zerado por deduções;
- impedimento por procuração;
- responsabilidade da equipe Fiscal;
- consolidação matriz/filial/rural sem duplicação.

### MEI/DAE

- Elenice;
- Luriel;
- DAE como fonte normal;
- ausência de GFD autônoma não gera pendência.

## 9. Critério de pacote final

Só gerar pacote quando:

- código operacional reconciliado com o repositório;
- testes aplicáveis verdes ou falhas remanescentes classificadas e realmente externas ao ambiente controlável;
- 28 casos reais regressados;
- migrations testadas;
- instalador e rollback testados;
- smoke Windows aprovado;
- documentação corresponde ao código que está no pacote;
- hash/versão do pacote registrados.

## 10. Resultado da homologação

O relatório final deve indicar explicitamente:

- commit/fonte utilizada;
- pacote gerado e hash;
- banco de teste utilizado/cópia;
- testes executados e totais;
- casos reais executados;
- falhas e classificação;
- migrações executadas;
- smoke Windows;
- rollback testado;
- pendências que realmente exigem servidor físico, se houver.

Sem essa rastreabilidade, o estado permanece `NÃO HOMOLOGADO`.
