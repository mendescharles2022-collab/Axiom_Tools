# B44 — Relatório A4 retrato — validação real

Data: 31/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Critério

O relatório impresso/PDF precisa caber em A4 retrato sem corte lateral, repetir cabeçalho nas páginas seguintes e evitar quebra interna de linhas.

## Estado do runtime recuperado

O stylesheet já contém:

- `@page { size: A4 portrait; margin: 8mm 7mm; }`;
- tabela limitada a 100% da área útil;
- `table-layout: fixed`;
- células com quebra controlada (`overflow-wrap:anywhere`, `white-space:normal`);
- `thead { display: table-header-group; }`;
- `break-inside: avoid` / `page-break-inside: avoid` por linha.

Portanto o bloqueador exigia principalmente prova real, e não uma reescrita preventiva do CSS.

## Prova com dados reais

Foi usado o relatório mais largo da competência 08/2026:

- tipo: `DARF DCTFWeb × Domínio — composição da folha`;
- 11 colunas;
- 310 linhas reais;
- geração em A4 retrato;
- resultado: 12 páginas.

Inspeção visual das páginas 1, 6 e 12 confirmou:

- nenhuma coluna cortada na margem direita;
- cabeçalho da tabela repetido na página intermediária e final;
- linhas mantidas dentro da página;
- última página encerrada sem overflow horizontal;
- layout permanece legível em retrato.

PDF de ensaio gerado com WeasyPrint 68.0 apresentou tamanho de página `595.276 × 841.89 pt (A4)`.

## Regressão automatizada

Teste versionado:

`runtime_overlay/app/tests/modules/test_report_a4_print_v8.py`

Resultado local:

- 4/4 testes PASS.

## Estado

B44 pode ser classificado como `CORRIGIDO_TESTADO` no snapshot canônico recuperado.

A homologação final continuará exigindo impressão/preview no Windows/browser utilizado no escritório, junto do build final reconciliado.
