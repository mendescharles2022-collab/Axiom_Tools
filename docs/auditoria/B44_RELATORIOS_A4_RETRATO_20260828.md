# B44 — Relatórios A4 retrato sem corte

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Problema

O relatório de Pendências/Conferência podia estourar A4 retrato, especialmente nos formatos com muitas colunas. O relatório DARF possui 11 colunas e é o pior caso horizontal do conjunto atual.

## Correção

A view de relatório passou a expor classes específicas por tipo:

- `ax-report-view--<tipo>`;
- `ax-report-table--<tipo>`;
- `ax-report-sheet`.

No perfil de impressão:

- `@page` permanece A4 portrait com margens 8mm/7mm;
- tabela usa `table-layout: fixed`;
- largura física possui pequena folga (`99.2%`) e células usam `box-sizing: border-box`;
- `thead` é repetido como `table-header-group`;
- `tbody` permanece `table-row-group`;
- linhas evitam quebra interna quando possível;
- texto longo usa `overflow-wrap:anywhere` e `hyphens:auto`;
- relatórios largos usam tipografia condensada própria;
- Pendências, DARF, Conferência e Auditoria possuem perfis proporcionais de colunas;
- não há `min-width` horizontal no bloco de impressão.

## Teste estrutural

Arquivo:

`runtime_overlay/app/tests/modules/test_report_a4_v8.py`

Resultado: 6/6 PASS.

A bateria não-web executável no ambiente Linux da auditoria passou em 419/419 testes após a correção.

## Smoke PDF real

Foi usado WeasyPrint 68.0 somente como renderer independente de ensaio e o PDF resultante foi renderizado novamente para PNG com a ferramenta de preflight/render de PDF.

### DARF — pior caso horizontal

- 11 colunas;
- 120 linhas com textos longos;
- 9 páginas;
- MediaBox: 210 × 297 mm em todas as páginas verificadas;
- cabeçalho repetido em todas as páginas;
- 120/120 linhas extraídas do PDF;
- inspeção visual da primeira e última página: sem corte à direita;
- SHA-256 do PDF de ensaio: `e5c05a2ad208e932f1daaa271daef0b3bdca0bafbab10e81f492947b5b2704f8`.

A primeira tentativa de smoke detectou corte real na coluna Situação. B44 não foi promovido naquele ponto. A correção de `box-sizing`, folga física e densidade foi aplicada e o smoke foi repetido até eliminar o corte.

### Pendências — caso que motivou o bloqueador

- 6 colunas;
- 90 linhas com nomes de arquivo e campos Faltantes propositalmente longos;
- 5 páginas;
- MediaBox: 210 × 297 mm;
- cabeçalho repetido em todas as páginas;
- 90/90 linhas presentes;
- preflight: PDF aberto, não criptografado, não escaneado;
- inspeção visual: sem corte horizontal;
- SHA-256 do PDF de ensaio: `21711597edea458ef298e34582b68c02de6d696a867ede47a6529f22508ef3ea`.

## Limite de homologação

A correção está testada estruturalmente e por renderer PDF independente. A homologação final ainda deverá confirmar o `window.print()` no navegador Windows usado no escritório, porque o motor de impressão do navegador é parte do runtime físico final.

## Estado

B44 pode ser classificado como `CORRIGIDO_TESTADO`.

Ainda não é `CORRIGIDO_HOMOLOGADO`.
