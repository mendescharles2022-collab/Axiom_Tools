# Contrato V8 — Materialidade de retificação

Data: 28/08/2026
Status: contrato obrigatório de auditoria; implementação ainda não homologada.

## Princípio

Retificação nasce de mudança material na verdade operacional do fechamento, não apenas da existência de um arquivo novo.

A comparação entre a versão vigente e a nova evidência deve resultar em uma destas classes:

- SEM_MUDANCA;
- COMPLEMENTAR_NAO_MATERIAL;
- MUDANCA_MATERIAL;
- INDETERMINADA_REVISAO.

## Mudanças materiais

Devem ser consideradas materiais, conforme o caso:

- troca do cliente/identidade correta;
- alteração de CPF, CNPJ, CAEPF, matrícula ou unidade relevante;
- mudança de competência;
- mudança de aplicabilidade de DARF, FGTS, DAE ou eConsignado;
- alteração entre mensal, rescisório ou antecipado;
- alteração de valores além de tolerância técnica de arredondamento;
- alteração de empregado/contribuinte, admissão, desligamento ou afastamento que afete apuração;
- matrícula/unidade adicional com efeito econômico;
- evidência que invalide justificativa usada na versão vigente.

## Não material por padrão

Não deve criar retificação automaticamente:

- arquivo fisicamente idêntico;
- reemissão documental equivalente sem diferença econômica;
- evidência complementar que não altere valores, aplicabilidade ou conclusão das obrigações.

## Casos reais

### Jair Ferreira Camargo

Se a versão vigente considerar apenas uma matrícula e a recuperação do segundo Extrato válido elevar o FGTS consolidado para R$ 389,04, mantendo federal R$ 511,43 uma única vez, há mudança material na composição do FGTS.

### Leosmar Teodoro de Sousa

Segundo Extrato equivalente com mesmos valores centrais e FGTS zero não deve gerar retificação material apenas por ser outro arquivo.

### Alex Douglas de Andrade

Contexto rescisório que muda FGTS mensal de exigível para não aplicável é material para a obrigação FGTS, sem eliminar automaticamente a DARF previdenciária aplicável.

### MEI/DAE

Trocar expectativa genérica de GFD pela obrigação específica DAE é mudança material da natureza da obrigação.

## Deltas obrigatórios

Toda análise material deve registrar diferenças estruturadas, por exemplo:

- valor anterior e novo;
- fontes/documentos envolvidos;
- inscrições/matrículas adicionadas ou removidas;
- mudança de aplicabilidade;
- mudança de pessoas/vínculos;
- justificativa afetada.

## Promoção

- SEM_MUDANCA: mantém versão vigente.
- COMPLEMENTAR_NAO_MATERIAL: mantém versão vigente e registra evidência complementar.
- MUDANCA_MATERIAL: cria candidato Vn+1 e bloqueia novas saídas até conclusão.
- INDETERMINADA_REVISAO: não promove automaticamente.

A versão anterior nunca é alterada retroativamente.

## Regressões mínimas

1. arquivo idêntico não cria retificação;
2. reemissão equivalente não cria retificação financeira;
3. valor diferente cria delta material;
4. competência conflitante exige revisão/materialidade;
5. matrícula adicional com efeito econômico é material;
6. Leosmar não sofre retificação falsa por duplicidade equivalente;
7. nova fonte que invalida justificativa abre revisão;
8. mudança material bloqueia saídas;
9. conclusão Vn+1 preserva Vn;
10. todos os deltas permanecem auditáveis.

Relaciona-se principalmente aos bloqueadores B01, B04, B10, B12, B13, B14, B17, B18 e B40.
