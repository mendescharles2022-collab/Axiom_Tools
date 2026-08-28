# Contrato V8 — Relatórios operacionais e impressão A4

Data: 28/08/2026
Status: **contrato de auditoria / homologação visual pendente**

## 1. Falha confirmada

O status operacional V8F2 registra relatório de pendências ultrapassando a largura imprimível do papel A4 em modo retrato.

A correção existente ainda não foi homologada em preview/impressão real.

Isso é falha funcional de saída, não apenas refinamento estético: informação cortada ou deslocada compromete o uso do relatório como evidência operacional.

## 2. Formato padrão

Relatórios operacionais tabulares da rotina mensal devem ter versão imprimível em:

- papel A4;
- orientação retrato por padrão quando o relatório for definido como retrato;
- margens controladas;
- largura limitada à área imprimível;
- sem scroll horizontal na versão de impressão.

Paisagem só deve ser usada quando o relatório específico for deliberadamente projetado para isso, não como remendo automático para tabela mal dimensionada.

## 3. Conteúdo prioritário

No relatório de pendências/conferência, a informação precisa permanecer inteligível em papel:

- cliente;
- competência;
- fonte/obrigação;
- situação;
- divergência/pendência;
- valor esperado/encontrado quando aplicável;
- justificativa/observação essencial;
- data/hora ou contexto necessário;
- paginação.

Identificadores técnicos internos devem ser omitidos da versão operacional quando não agregarem decisão ao usuário.

## 4. Tabelas

Regras:

- `table-layout`/dimensionamento deve impedir extrapolação da página;
- células textuais longas devem quebrar linha;
- não usar `white-space: nowrap` indiscriminadamente;
- colunas monetárias/números podem permanecer compactas;
- textos de ocorrência/justificativa recebem largura flexível;
- nomes extensos quebram de modo legível;
- cabeçalho da tabela deve repetir em páginas seguintes quando suportado;
- não separar visualmente uma linha de forma que torne impossível associar cliente e ocorrência.

## 5. Conteúdo de tela que não vai para o papel

Na folha impressa não devem consumir espaço:

- sidebar;
- topbar;
- botões;
- filtros interativos;
- campos de pesquisa;
- paginação web;
- ações de reprocessar/anexar/resolver;
- elementos puramente navegacionais.

O cabeçalho impresso deve ser próprio do relatório.

## 6. Cabeçalho e rodapé

Cabeçalho mínimo:

- Axiom Tools;
- nome do relatório;
- competência;
- filtros relevantes aplicados;
- data/hora da geração.

Rodapé/paginação quando tecnicamente viável:

- página atual/total ou numeração de página;
- identificação discreta do relatório.

Não repetir blocos grandes em todas as páginas.

## 7. Valores e máscaras

Preservar regras já homologadas de apresentação:

- competência `MM/AAAA`;
- datas `DD/MM/AAAA`;
- moeda brasileira;
- CPF/CNPJ/CAEPF/IE conforme formatador central;
- siglas técnicas corretas: DARF, FGTS, eSocial, eConsignado, e-CAC etc.

Não introduzir formatadores específicos no template de impressão.

## 8. Pendências por fonte

Com a V8, o relatório deve refletir fonte/obrigação individual.

Exemplo: uma DARF justificada e um FGTS pendente do mesmo cliente não podem aparecer como uma única situação global ambígua.

A versão impressa deve permitir entender por que o cliente está aberto sem consultar a tela.

## 9. Estado fechado e retificação

Relatórios históricos devem distinguir:

- fechamento vigente;
- versão do fechamento;
- retificação pendente/concluída quando aplicável.

Não misturar snapshot antigo com estado corrente sem rotulagem explícita.

## 10. Teste visual obrigatório

A homologação não pode ser apenas CSS estático ou render HTML.

Executar no ambiente Windows/navegador real:

1. abrir preview de impressão;
2. selecionar A4 retrato;
3. validar primeira página;
4. validar página intermediária;
5. validar última página;
6. testar nome de cliente longo;
7. testar justificativa longa;
8. testar valores monetários;
9. testar múltiplas fontes no mesmo cliente;
10. confirmar ausência de corte horizontal.

## 11. Casos extremos de regressão

- cliente com nome muito longo;
- ocorrência longa;
- vários documentos/fontes;
- CAEPF/matrículas no detalhamento;
- mais de uma página;
- dezenas/centenas de pendências;
- filtro por competência;
- `Competência não identificada` em relatório técnico separado quando necessário.

## 12. Critério de homologação

O relatório só é aprovado quando todas as informações essenciais ficam dentro da área imprimível do A4 e continuam legíveis sem redução extrema de fonte.

Gerar PDF ou abrir preview sem corte é parte da regressão final da V8.
