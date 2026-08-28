# B21/B22/B23 — Previdência, afastamentos e impedimentos por fonte

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B21 — Deduções previdenciárias

Quando `darf_folha_esperado` não está preenchido, mas o Extrato Mensal contém `total_inss`, salário-família e salário-maternidade, a Conference passa a derivar conservadoramente:

`INSS esperado = total INSS − salário-família − salário-maternidade`.

Esse fallback é usado somente quando os três campos estão presentes.

Fixtures reais:

- Ponto Kent: R$ 893,45 − R$ 135,08 = R$ 758,37; DARF previdenciário R$ 758,37; resultado CONFERIDO.
- Denes Mariano: R$ 124,81 − R$ 124,81 = R$ 0,00; DARF previdenciário não aplicável/ausência justificada; FGTS permanece obrigação independente.

## B22 — Afastamentos/faltas e bases zeradas

Saldo previdenciário efetivamente zerado na folha não é convertido em falsa pendência de DARF.

Fixtures reais:

- Gold Pallace: previdenciário zero → `NAO_APLICAVEL_ZERO`;
- Marcos Augusto Pimentel: previdenciário zero → `NAO_APLICAVEL_ZERO`;
- Wilmar Ferreira: previdenciário zero → `NAO_APLICAVEL_ZERO`;
- GL Auto Center: previdenciário zero, mas FGTS R$ 194,24 continua aplicável e confere com a GFD R$ 194,24.

Afastamento de uma pessoa específica não zera a empresa inteira por cadastro. A evidência da própria competência permanece soberana.

## B23 — DARF Fiscal / impedimento RFB

Foi incluído o estado manual por fonte `IMPEDIDA_EXTERNAMENTE`.

Regras:

- exige observação/justificativa;
- é registrado somente na fonte selecionada;
- pode resolver a fonte DARF como situação justificada;
- nunca libera FGTS ou eConsignado irmãos;
- se outra fonte continuar divergente, o agregado continua DIVERGENTE.

Fixture real:

- Casa das Carnes e Panificadora Lago Azul: DARF marcado `IMPEDIDA_EXTERNAMENTE` por procuração expirada/revogada; FGTS não aplicável; agregado fica JUSTIFICADO apenas para esse contexto.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_previdencia_afastamentos_impedimentos_v8.py`

Resultados:

- 8/8 testes específicos PASS;
- regressão não-web acumulada: 366/366 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

## Estado

B21, B22 e B23 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica recuperada. A homologação Windows/runtime final permanece pendente.
