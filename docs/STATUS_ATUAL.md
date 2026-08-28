# Axiom Tools — Status Atual

Data: 28/08/2026  
Status: **V5.6.14V7 estável / V8 em auditoria e correção / V8 NÃO HOMOLOGADA**

## 1. Marco atual

A auditoria V8 possui 50 bloqueadores canônicos, 28 casos reais de 08/2026, registries machine-readable e tooling automatizado de reconciliação/homologação.

A execução canônica do tooling é:

- GitHub Actions run `33195532631`;
- commit `b18c487f125c300964a5558b5f8cbe271c0418dc`;
- Python 3.12.14;
- **161 testes executados / 161 aprovados**.

A run também publicou o artifact `v8-release-preflight` (ID `9695566182`) com SHA-256 `a379a32b433722f87b179d200dde5d454eefdaff68a2e2318f8bb93b295bf4c6`.

## 2. Preflight atual

Resultado automático:

- `Final OK = False`;
- bloqueadores homologados: `0/50`;
- casos PASS: `0/28`;
- evidências externas PASS: `1/10`;
- release `READY = False`;
- build final `OK = False`.

Esse bloqueio é esperado e correto.

## 3. Estado B01–B50

- 35 `PRONTO_PARA_CORRIGIR`;
- 8 `INSPECAO_PENDENTE`;
- 3 `EM_CORRECAO` — B35, B41, B42;
- 4 `BLOQUEADO_POR_RUNTIME` — B05, B06, B45, B49;
- 0 `CORRIGIDO_HOMOLOGADO`.

## 4. Gate Zero — B06

O `main` ainda não contém integralmente a árvore operacional V8 auditada no servidor/ZIP canônico.

Já estão prontos/testados:

- exportador controlado do runtime;
- launcher PowerShell;
- auditor runtime ↔ GitHub;
- 3 E2E de reconciliação;
- manifesto/hash e bloqueio de dados sensíveis.

Pendente: executar a exportação na instalação Windows real ou recuperar pacote canônico equivalente e reconciliar a árvore operacional.

## 5. Gate final de homologação

Implementado:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`;
- `config/release_gate_evidence_v8_current.json`;
- artifact automático de preflight no CI.

O modo final exige simultaneamente:

1. B01–B50 homologados com evidência;
2. C01–C28 PASS com evidência;
3. release `READY`;
4. build/proveniência verificados;
5. CI, baseline runtime, banco, invariantes, benchmark, segurança, A4, instalação e rollback em PASS.

## 6. Tooling já preparado

Além da reconciliação e gate:

- proveniência de build;
- baseline/clone/comparação/invariantes SQLite;
- bundle/verificação/ensaio de rollback;
- inventário estático de segurança;
- consistência banco ↔ filesystem;
- retenção dry-run;
- benchmark SQLite;
- regressão C01–C28;
- governança B01–B50;
- índice SHA-256 de evidências.

## 7. Ordem da correção operacional após B06

1. baseline/suíte original;
2. B01 — reprocessamento candidato;
3. B02 — Conference somente leitura;
4. B03/B39 — gate de saídas;
5. B07/B08 — universo/chamadas;
6. estados/retificação/concorrência;
7. documentos/identidade/composição/aplicabilidade;
8. eConsignado;
9. cadastro/legado/segurança;
10. UX/restantes;
11. migração/invariantes reais;
12. C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 8. Estado de entrega

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback físico **não comprovado**;
- runtime **ainda não reconciliado integralmente com o GitHub**.

A referência viva é o `main`, `docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md` e os registries de `config/`.
