# Auditoria canônica V8 — Etapa 74

Data: 31/08/2026  
Status: **B07/B09/B10/B11/B37 com tooling executável e regressões / integração runtime ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 74 transformou os contratos de universo operacional e máquinas de estado em guardrails executáveis.

Blocos cobertos:

- B07 — universo operacional duplicado/espalhado;
- B09 — cliente FECHADA na mesa viva;
- B10 — RETIFICACAO misturada ao ciclo normal;
- B11 — `PRONTA` traduzida indevidamente para `Em conferência`;
- B37 — dupla verdade entre estado persistido e estado operacional derivado.

## 2. Universo operacional — B07/B09/B10

Novo tooling:

`scripts/audit_operational_scope_contract.py`

O auditor é orientado por política e verifica:

- referências diretas à tabela de fechamento fora do domínio permitido;
- SQL de composição mensal reproduzido fora da fachada Closing;
- funções de mesa/conferência contendo estados proibidos como `FECHADA` e `RETIFICACAO`;
- existência opcional de consumo da fachada canônica `closing_scope`;
- erros de parse, sem silenciosamente tratar arquivos inválidos como seguros.

Regressões:

`tests/test_audit_operational_scope_contract.py`

Cenários explícitos:

- SQL direto dentro de `modules/closing` permitido;
- SQL direto em Processamento bloqueado;
- `FECHADA` na função `clientes_conferencia` bloqueada;
- `RETIFICACAO` na mesa normal bloqueada;
- consulta histórica de fechados fora da mesa viva não é confundida com autorização operacional;
- fachada canônica pode ser exigida por política.

## 3. Semântica dos estados — B11/B37

Novo tooling:

`scripts/audit_state_semantics_contract.py`

O auditor permite configurar mapeamentos e coocorrências semanticamente proibidas.

Regra atual coberta por regressão:

```text
PRONTA -> "Em conferência" = proibido
PRONTA -> "Aguardando processamento" = aceitável como migração/visão operacional
```

Também existe regressão para a dupla verdade já observada no Monitor:

```text
COM_PENDENCIAS + PROCESSAMENTO_CONCLUIDO
```

quando os dois valores são usados pela mesma função para representar a mesma sessão.

O objetivo não é proibir rótulos amigáveis; é impedir que o rótulo visual contradiga a máquina de estado que deveria representar.

Regressões:

`tests/test_audit_state_semantics_contract.py`

## 4. Marco CI

Run `33447553697`  
Commit `74074198aa79cecfe23c169ac6ed2cec8caa3cf2`

Smoke B06:

```text
POWERSHELL_B06_SMOKE_OK
```

Suíte:

```text
Ran 388 tests in 2.918s
OK
```

Preflight:

```text
Final OK: False
Bloqueadores homologados: 0/50
Casos PASS: 0/28
Mapa causal: 28/28
Evidências PASS: 1/10
Release READY: False
Build OK: False
```

Artifact:

- ID `9778573414`;
- SHA-256 `d056e2c3339696e8748f891f0a7b2d68686958aa7cfa8b4bc515115aa74cdbf5`.

## 5. Impacto de estados

B07, B09, B10, B11 e B37 passam de:

`PRONTO_PARA_CORRIGIR`

para:

`EM_CORRECAO`

A promoção significa que os critérios técnicos já podem ser executados automaticamente contra a árvore reconciliada.

Não significa que a implementação operacional esteja corrigida ou homologada.

## 6. Snapshot após a Etapa 74

- `PRONTO_PARA_CORRIGIR`: 25;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 21;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

## 7. Próximo bloco

A próxima família estrutural é B12–B17/B50:

- múltiplos Extratos;
- federal consolidado x FGTS aditivo por matrícula;
- múltiplas GFD e natureza mensal/rescisória;
- descoberta→vínculo;
- identidade PF/CAEPF;
- deduplicação física, lógica e econômica.

O tooling deve impedir tanto `último arquivo vence` quanto `dois arquivos = somar`.

## 8. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
