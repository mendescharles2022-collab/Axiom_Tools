# Contrato V8 — Modularização e fonte única de regras

Data: 28/08/2026
Status: **risco estrutural confirmado / modularização deve preservar comportamento**

## 1. Evidência da auditoria canônica

A inspeção do ZIP canônico já registrou:

- `modules/processing/central.py` com aproximadamente 93 KB e mais de 2 mil linhas;
- `documents_views.py` com aproximadamente 73 KB e mais de 1,7 mil linhas;
- helpers/regras repetidos entre `conference.py` e `operations.py`, incluindo `_money`, `_cmp`, `_ultimo_tipo`;
- implementação antiga de `_check_darf_folha` ainda presente fora do fluxo canônico.

A própria AXT-003 já estabelece como padrão do projeto evitar monólitos, preferindo responsabilidades claras, arquivos em torno de 300 linhas quando viável e justificativa/divisão quando se aproximarem de 500 linhas.

## 2. Problema

O problema não é o número de linhas isoladamente.

O risco real é coexistirem, no mesmo arquivo ou em arquivos diferentes:

- descoberta documental;
- reprocessamento;
- identidade;
- competência;
- persistência;
- conferência;
- regras fiscais/previdenciárias;
- estados;
- saída;
- view/web;
- compatibilidade legada.

Isso facilita divergência entre caminhos que deveriam usar a mesma regra.

Exemplos já observados:

- `_ultimo_tipo()` inadequado para multi-Extrato;
- regra antiga `_check_darf_folha` sobrevivendo fora do fluxo atual;
- filtros de fechamento repetidos em Processamento/Conferência/Saídas;
- autorização de saída aplicada de forma diferente entre views e services.

## 3. Princípio

Regra de negócio canônica deve ter **uma fonte autoritativa reutilizável**.

Views traduzem entrada/saída.

Services orquestram casos de uso.

Repositories executam persistência/consultas.

Motores/especialistas extraem e interpretam documentos.

Políticas puras decidem:

- aplicabilidade;
- consolidação;
- estados;
- autorização;
- promoção de candidato.

Não repetir política em view, service e template.

## 4. Áreas candidatas a separação

A organização exata pode acompanhar o código existente, mas responsabilidades devem equivaler a:

### Reprocessamento

- criação de candidato;
- comparação candidato x vigente;
- política de promoção;
- histórico/versionamento.

### Identidade documental

- resolução cliente;
- resolução CPF/CNPJ/CAEPF/estabelecimento;
- inscrição de origem;
- grupo de consolidação.

### Conferência

- aplicabilidade de obrigações;
- composição de evidências;
- resultado por fonte;
- projeção agregada do cliente.

### Fechamento

- máquina de estado mensal;
- chamadas;
- fechamento derivado;
- retificação.

### Saídas

- gate único de autorização;
- impressão;
- entrega;
- geração automática.

### eConsignado

- universo do job;
- consulta/fotografia;
- interpretação contextual posterior.

## 5. Helpers puros

Formatadores como `_money` não devem se multiplicar em módulos de negócio.

Comparadores como `_cmp` precisam ter semântica explícita e teste próprio.

Seletores como `_ultimo_tipo` não podem esconder decisão de composição multi-documento.

Se existe necessidade de escolher “vigente”, “último”, “todos relacionados” ou “componentes econômicos”, isso deve ser nomeado no contrato da função.

## 6. Remoção de regra morta

Código legado só pode ser removido após:

1. confirmar que não é chamado por rota/job/teste válido;
2. identificar qual contrato atual o substitui;
3. migrar ou excluir teste que defendia regra superada;
4. executar regressão dos casos reais afetados.

Não deixar duas implementações “por segurança”. Isso é justamente fonte de deriva futura.

## 7. Views

Views não devem decidir:

- se cliente pode fechar;
- se obrigação é aplicável;
- se documento pode imprimir;
- se candidato é melhor;
- como somar FGTS;
- como deduplicar federal;
- qual chamada pertence ao ciclo.

Views devem:

- validar entrada superficial;
- chamar service/política;
- apresentar resultado;
- devolver erro operacional adequado.

## 8. Repositories

Repositories não devem inferir negócio a partir de detalhes de tipo de entrada sem normalização.

O caso `classificacao_inativacao` string/Enum é exemplo de acoplamento indevido entre camada de entrada e persistência.

Normalizar antes de persistir.

## 9. Migração incremental

A modularização V8 não deve virar reescrita total.

Ordem segura:

1. criar política pura com testes;
2. cobrir comportamento atual válido;
3. redirecionar um caminho por vez;
4. executar regressão;
5. remover implementação duplicada somente após provar ausência de uso.

Rotas/URLs e contratos visuais aprovados devem permanecer, salvo mudança explicitamente aprovada.

## 10. Testes de arquitetura

Adicionar verificações simples, sem transformar o projeto em burocracia:

- views não importam módulos internos proibidos quando houver service público;
- gate de saída é chamado por todas as entradas de saída;
- cálculo da Conferência usa política única;
- não existem duas funções canônicas de decisão DARF/FGTS com semântica concorrente;
- arquivos críticos excessivamente grandes geram alerta de revisão, não falha automática cega.

## 11. Regressões obrigatórias durante decomposição

- Jair 449/450;
- Leosmar duplicidade equivalente;
- MEI/DAE;
- FGTS rescisório;
- DARF por procuração;
- Predileta/Fiscal;
- eConsignado D A F Castro;
- T L 2ª chamada;
- gate Impressão/Entregas;
- inativação/reativação;
- Conference read-only.

## 12. Critério de aceite

A modularização só é melhora se reduzir duplicidade sem alterar resultado funcional aprovado.

Nenhuma refatoração estrutural pode ser usada como justificativa para adiar regressão dos casos reais.
