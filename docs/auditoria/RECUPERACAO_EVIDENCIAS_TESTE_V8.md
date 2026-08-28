# Recuperação de evidências de teste — Auditoria Canônica V8

Data: 28/08/2026

## Motivo

O snapshot `config/blocker_status_v8_current.json` perdeu campos `test_evidence` durante a sequência de sincronização/formatação da auditoria, embora diversos bloqueadores já tivessem sido promovidos a `CORRIGIDO_TESTADO` com testes registrados em commits, notas de auditoria e regressões anteriores.

O validador canônico (`scripts/validate_blocker_statuses.py`) está correto ao exigir `code_evidence` + `test_evidence`. Esta recuperação não afrouxa o gate: ela restaura a trilha exigida pelo próprio contrato V8.

## Fontes recuperadas

- Snapshot detalhado anterior no commit `200a6bba5d231581e875b33ba8355b8d3a495381`, que preserva evidências explícitas para B02 e B07–B11.
- Commits de implementação já referenciados em `config/blocker_status_v8_current.json`.
- Resultados de testes/regressões registrados nas notas atuais de cada bloqueador.
- Execuções GitHub Actions anteriores da branch, incluindo o run `33203553566` concluído com sucesso no marco anterior.
- O run `33217576061` falhou exclusivamente porque `CORRIGIDO_TESTADO` estava sem `test_evidence`; não houve falha funcional reportada, apenas seis erros de validação derivados da mesma ausência documental.

## Evidência recuperada por bloqueador

| Bloqueador | Evidência de teste recuperada / registrada |
|---|---|
| B02 | Snapshot antigo: `test_conference_readonly_v8=2/2 PASS`; regressão não-web `296/296 PASS`. |
| B04 | Nota canônica atual: `4/4` testes específicos PASS. |
| B07 | Snapshot antigo: `test_closing_universe_v8=6/6 PASS`; base real 08/2026; regressão não-web `281/281 PASS`. |
| B08 | Snapshot antigo: `test_closing_calls_v8=5/5 PASS`; caso real T L reparado para ADIADA/chamada 2; regressão `296/296 PASS`. |
| B09 | Snapshot antigo: `test_closing_universe_v8=6/6 PASS`; base real com interseção fechados × ciclo vivo igual a zero. |
| B10 | Snapshot antigo: bloco B10–B11 `9/9 PASS`; base real 08/2026 com retificações separadas do ciclo vivo. |
| B11 | Snapshot antigo: bloco B10–B11 `9/9 PASS`; regressão não-web `281/281 PASS`. |
| B12 | Nota atual: Multi-Extrato testado com Jair e Leosmar; deduplicação lógica e composição econômica validadas. |
| B13 | Nota atual: caso Jair validado com federal R$ 511,43 uma única vez e FGTS R$ 389,04 por componentes distintos. |
| B14 | Nota atual: Multi-GFD validado para reemissão, sucessora e componente distinto, com bloqueio de soma cega em conflito. |
| B15 | Nota atual: pipeline de identidade validado na ordem documento principal → inscrição oficial → vínculo manual. |
| B16 | Nota atual: dois CAEPFs de Jair resolvem para cliente 826 e ambiguidade é bloqueada. |
| B17 | Nota atual: núcleo transversal validado com SHA físico separado do fingerprint econômico. |
| B18 | Nota atual: decisão manual por fonte validada e legado global impedido de autorizar fechamento/propagar estado. |
| B19 | Nota atual: FGTS zero validado como `NAO_APLICAVEL`, sem falsa ausência de GFD. |
| B20 | Nota atual: MEI/DAE validado; Elenice R$ 299,88 conferida. |
| B21 | Nota atual: deduções previdenciárias validadas para derivação do saldo esperado quando os campos existem. |
| B22 | Nota atual: bases zeradas/afastamentos não geram DARF falso e FGTS permanece independente. |
| B23 | Nota atual: `IMPEDIDA_EXTERNAMENTE` validado por fonte com justificativa obrigatória. |
| B24 | Nota atual: job eConsignado validado herdando competência/chamada e disparando recálculo por evento. |
| B25 | Nota atual: universo eConsignado validado para chamada atual com movimento; 30 clientes em 08/2026. |
| B26 | Nota atual: avaliador contextual único validado; casos DAF/Lourenconi divergentes, GL justificado e D&L residual. |
| B27 | Nota atual: falhas/sem procuração não apagam snapshot bom; promoção oficial atômica. |
| B28 | Nota atual: retry cria novo job auditável e preserva job anterior. |
| B29 | Nota atual: extrato separa situação/tipo/vínculo; Diretor/Trabalhando não vira empregado. |
| B30 | Nota atual: saldo da Apuração Federal validado como fonte autoritativa; P da Silva Carmo = R$ 220,00. |
| B31 | Nota atual: proveniência temporal validada; regressão acumulada `393/393 PASS` no marco B31–B33. |
| B32 | Nota atual: IRRF preserva competência de cálculo/pagamento e critério PAGAMENTO sem substituir saldo federal autoritativo. |
| B33 | Nota atual: dezembro e 13º validados com exceções anuais configuráveis/versionadas e bloqueio de sobreposição. |
| B34 | Nota atual: `5/5` testes específicos; regressão não-web `398/398 PASS`. |
| B35 | Nota atual: `integrity_check=ok`, `foreign_key_check=0`, invariantes lógicas pós-migração=0 e regressão `400/400 PASS`; 200 referências históricas de impressão preservadas. |
| B36 | Nota atual: migração semântica do legado global validada sem propagação para fontes. |
| B37 | Nota atual: sessão técnica separada da revisão documental; `297/297` acumulados no marco. |
| B38 | Nota atual: 182 rotas/125 mutações auditadas; 0 mutações internas sem sessão; CSRF global sem exemptions; 111/111 forms POST com token. Ensaio HTTP real fica para homologação Windows. |
| B39 | Nota atual: bloco B38+B39 `19/19` específicos; regressão não-web `406/406 PASS`. |
| B40 | Nota atual: concorrência otimista validada com `revisao_estado`; escrita obsoleta rejeitada. |
| B43 | Nota atual: `7/7` específicos e `259/259` não-web executáveis no ambiente atual. |
| B44 | Nota atual: smoke A4 DARF 9 páginas/120 linhas e Pendências 5 páginas/90 linhas; regressão não-web `419/419 PASS`. |
| B46 | Nota atual: `7/7` específicos PASS no bloco de Pendências/Monitor. |
| B47 | Nota atual: `6/6` específicos e regressão não-web `425/425 PASS`. |
| B50 | Nota atual: coberto pelo mesmo núcleo transversal validado em B17. |

## Regra de uso

Cada bloqueador `CORRIGIDO_TESTADO` aponta este documento em `test_evidence` com âncora própria. A evidência documental não substitui homologação física. Nenhum item é promovido a `CORRIGIDO_HOMOLOGADO` sem `runtime_evidence` e `homologation_evidence`.

Após esta restauração, o CI da branch deve voltar a ficar verde antes da continuidade dos bloqueadores ainda abertos.
