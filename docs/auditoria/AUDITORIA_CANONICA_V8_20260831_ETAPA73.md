# Auditoria canônica V8 — Etapa 73

Data: 31/08/2026  
Status: **B01/B02/B03/B39 com tooling executável e regressões / integração runtime ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Objetivo

Após estabilizar o handoff B06 até a Etapa 72, a auditoria voltou às correções que podem ser preparadas sem escrever sobre o runtime físico.

A Etapa 73 transformou quatro contratos críticos em auditores automatizados:

- B01 — reprocessamento por candidato, sem destruir a vigente;
- B02 — GET da Conferência como leitura pura;
- B03 — gate único de autorização de saídas;
- B39 — seleção manual de IDs não equivale a autorização.

## 2. B01 — reprocessamento candidato

Novo tooling:

`scripts/audit_reprocessing_candidate_contract.py`

Cobertura principal:

- identifica funções de reprocessamento por política;
- bloqueia `DELETE` sobre tabelas vigentes configuradas;
- detecta `commit` anterior à criação do candidato;
- exige evidência de candidato;
- exige etapa de promoção;
- exige recálculo posterior à promoção;
- não realiza autofix.

Regressões:

`tests/test_audit_reprocessing_candidate_contract.py`

Incluem o padrão já observado no V8F2: remoção de pessoas/arquivo vigente antes da nova leitura.

## 3. B02 — pureza de leitura GET

Novo tooling:

`scripts/audit_get_read_purity.py`

O auditor constrói grafo de chamadas entre funções Python recuperáveis e percorre cada rota GET.

Bloqueia:

- chamada direta a mutador configurado;
- mutação escondida em helper indireto;
- SQL de escrita alcançável a partir de GET;
- mistura GET/POST quando o mesmo handler contém mutação;
- erro de parse silencioso.

Regressões:

`tests/test_audit_get_read_purity.py`

O caso `GET -> montar_conferencia -> conferir_cliente -> fechar_cliente` é explicitamente coberto.

## 4. B03 — gate único de saída

Novo tooling:

`scripts/audit_output_gate_contract.py`

O auditor inventaria entrypoints de geração/impressão/entrega e percorre chamadas até os geradores.

Bloqueia:

- caminho até gerador sem gate canônico;
- bypass em rota POST que chama gerador diretamente;
- helper indireto que alcança gerador sem autorização;
- uso de `PROCESSADO` como sinal de autorização sem estado fechado esperado.

Permite o desenho preferencial em que o gate fica centralizado no próprio serviço gerador, protegendo todos os chamadores.

Regressões:

`tests/test_audit_output_gate_contract.py`

## 5. B39 — seleção manual não é autorização

Novo tooling:

`scripts/audit_manual_selection_gate.py`

O auditor identifica fluxos de seleção por nome/parâmetro e prova se um caminho de IDs selecionados até geração/impressão/entrega atravessa guard de backend.

Guardas configuráveis incluem, por exemplo:

- interseção com universo autorizado;
- filtro de autorizados;
- validação de seleção;
- gate de saída em lote.

Regressões:

`tests/test_audit_manual_selection_gate.py`

Assim, `IDs enviados pelo front -> gerar` sem nova autorização no backend passa a ser defeito detectável.

## 6. Marco CI

Run `33447254039`  
Commit `e51bc61f13bbb21922b295eb57f8794a481962ed`

Smoke B06:

```text
POWERSHELL_B06_SMOKE_OK
```

Suíte:

```text
Ran 371 tests in 1.531s
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

- ID `9778467287`;
- SHA-256 `4ce32783f1cd0d4fd2df6300d39d7a7cb3c87e2b4054fdbe3b06c1bfad2e6919`.

## 7. Impacto de estados

B01, B02, B03 e B39 passam de:

`PRONTO_PARA_CORRIGIR`

para:

`EM_CORRECAO`

Isso significa apenas que já existe tooling/regressão executável para orientar a correção.

Não significa:

- código operacional corrigido;
- execução na árvore Windows real;
- caso C homologado;
- pacote liberado.

## 8. Snapshot após a Etapa 73

- `PRONTO_PARA_CORRIGIR`: 30;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 16;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

## 9. Próximo bloco

Sem depender do runtime físico, a próxima frente natural é consolidar universo/máquinas de estado:

B07, B09, B10, B11 e B37.

A correção integrada deles continuará condicionada à reconciliação B06, mas os contratos podem ser convertidos em tooling/regressões agora.

## 10. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
