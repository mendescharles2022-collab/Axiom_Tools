# Auditoria canônica V8 — Etapa 3

Data: 28/08/2026
Base de evidência: `Axiom_Tools(20260827-175623).zip` + registros da auditoria canônica e análise dos 28 casos reais de 08/2026.
Status: **auditoria em andamento / nenhuma correção estrutural considerada homologada nesta etapa**.

## 1. Objetivo desta etapa

Esta etapa cruza os achados estruturais já confirmados com os 28 casos reais de agosto para transformar exceções pontuais em regras canônicas de sistema.

Não é uma reinterpretação dos casos já discutidos. O objetivo é identificar quais mecanismos centrais precisam existir para que os mesmos defeitos não reapareçam em outros clientes e competências.

## 2. Achado novo — o estado da Conferência precisa existir por fonte/obrigação

A modelagem atual baseada em uma única decisão manual por `competencia + cliente_id` é insuficiente.

Os casos reais provam que um mesmo cliente pode ter, simultaneamente:

- DARF conferida;
- FGTS pendente;
- eConsignado justificado;
- FGTS rescisório aplicável;
- uma fonte impedida externamente;
- outra fonte normalmente exigível.

Exemplos já validados:

- Casa das Carnes e Panificadora Lago Azul: DARF impedida por procuração expirada, sem liberar automaticamente outras fontes;
- Maria Virginia S Souto: DARF impedida por procuração revogada;
- Predileta: DARF sob responsabilidade da equipe Fiscal, sem liberar automaticamente FGTS/eConsignado;
- Alex Douglas de Andrade: FGTS mensal não aplicável porque o vínculo foi tratado no contexto rescisório, mantendo DARF previdenciária;
- GL Auto Center: ausência de desconto de consignado explicada por afastamento/pagamento direto, enquanto FGTS continua aplicável.

### Regra canônica

A Conferência deve possuir estado por `cliente + competencia + fonte/obrigacao`.

Estados mínimos sugeridos para a obrigação:

- `PENDENTE`;
- `CONFERIDA`;
- `NAO_APLICAVEL`;
- `JUSTIFICADA`;
- `IMPEDIDA_EXTERNAMENTE`;
- `DIVERGENTE`;
- `RETIFICACAO`.

A situação agregada do cliente deve ser derivada desses estados, nunca o contrário.

Uma decisão em DARF não pode modificar implicitamente FGTS, DAE, eConsignado ou qualquer outra fonte.

## 3. Reprocessamento candidato/versionado — política de promoção obrigatória

A regra `não destruir a versão vigente antes da nova leitura` precisa ser complementada por uma política explícita de promoção de candidato.

### Fluxo obrigatório

1. preservar integralmente a versão vigente;
2. criar candidato de reprocessamento separado;
3. executar identificação, competência, classificação e extração no candidato;
4. comparar candidato x vigente;
5. somente promover o candidato se ele não degradar campos essenciais ou se a mudança estiver justificada por nova evidência material;
6. candidato rejeitado permanece auditável, mas não vira versão vigente;
7. após promoção, recalcular somente os cruzamentos afetados.

### Campos que não podem regredir silenciosamente

- cliente/identidade;
- competência;
- tipo documental;
- inscrição/matrícula/origem;
- status técnico;
- campos obrigatórios por tipo;
- valores já extraídos com evidência válida.

Confiança/completude percentual isolada não é suficiente para decidir promoção.

### Regressão obrigatória — Jair Ferreira Camargo

Os Extratos 449 e 450 devem ser recuperados a partir das versões históricas válidas sem apagar o histórico dos reprocessamentos posteriores.

Resultado esperado:

- ambos vinculados ao cliente 826;
- competência 08/2026;
- identidade por matrícula preservada;
- Extrato 449: FGTS R$ 129,68;
- Extrato 450: FGTS R$ 259,36;
- saldo federal consolidado R$ 511,43 sem duplicação.

## 4. Composição multi-documento precisa distinguir repetição de componente aditivo

A auditoria confirma dois cenários distintos.

### Jair Ferreira Camargo

Dois Extratos de matrículas distintas:

- federal repetido/consolidado: não somar;
- FGTS por matrícula: somar.

Resultado FGTS esperado: R$ 389,04.

### Leosmar Teodoro de Sousa

Dois Extratos vigentes com os mesmos valores centrais e FGTS zero.

Neste caso, a simples existência de dois documentos não autoriza soma ou duplicação de obrigação.

### Regra canônica

Antes de compor valores, o motor deve classificar documentos relacionados como:

- reemissão/duplicidade equivalente;
- versão sucessora;
- unidade/matrícula distinta;
- evidência complementar;
- documento de natureza distinta no mesmo fato gerador.

A composição financeira só ocorre depois dessa classificação.

## 5. Chave de composição e fingerprint documental

Para impedir soma cega, a composição deve utilizar uma identidade lógica além do `cliente_id`.

Elementos necessários conforme a fonte:

- competência;
- cliente/grupo empregador;
- CPF/CNPJ/CAEPF;
- inscrição/matrícula/filial;
- tipo documental;
- natureza do recolhimento;
- período de apuração;
- identificadores disponíveis no documento;
- hash do arquivo;
- fingerprint dos valores centrais.

Hash idêntico indica arquivo idêntico, mas hash diferente não prova obrigação distinta. Reemissões podem ter bytes diferentes e representar o mesmo fato.

## 6. FGTS mensal, rescisório e antecipado devem ser componentes, não guias concorrentes

Os casos Alex Douglas, Comercial Faria, Empório Frios Itapaci, Predileta e Ribeiro e Nascimento Art Vidros demonstram que o batimento não pode pressupor uma única GFD por competência.

A estrutura de conferência precisa distinguir pelo menos:

- FGTS mensal;
- FGTS rescisório;
- FGTS antecipado/recolhido em razão da rescisão;
- garantias relacionadas a consignado/rescisão, quando aplicável;
- guia substituída/reemitida.

A soma deve considerar apenas componentes economicamente distintos. Reemissão da mesma obrigação não pode dobrar valor.

## 7. Obrigações zeradas precisam virar não aplicáveis quando a causa está explicada

Vários dos 28 casos são falsas pendências causadas por ausência legítima de guia.

Casos confirmados incluem:

- Denes Mariano de Castro: salário-família zera saldo previdenciário;
- Gold Pallace Hotel: afastamento integral, sem remuneração e bases zeradas;
- Marcos Augusto Pimentel Daibert: afastamento integral pelo INSS, sem valores;
- Larissa B Maia: sem empregados, FGTS zero e DARF corretamente localizada;
- Wilmar Ferreira Pires: faltas integrais, sem remuneração e sem guias;
- MEIs Elenice Batista Santos Silva e Luriel Ferreira Malheiros: DAE como obrigação normal, sem GFD autônoma.

### Regra canônica

`documento ausente` só pode ser pendência quando a obrigação estiver efetivamente `APLICAVEL`.

Primeiro o motor determina aplicabilidade e valor esperado; só depois verifica presença documental.

## 8. Descoberta/leitura/vínculo é uma cadeia única de diagnóstico

Construtora & Empreendimentos Messias, Delfino Pereira Ribeiro, Eloim Transportes, Empresa Funerária Itapax e J Bernardes/Odonto Art demonstram o mesmo padrão operacional: arquivo existia, mas não chegou corretamente à Conferência.

A auditoria não deve registrar genericamente `guia ausente` nesses casos.

O diagnóstico deve localizar o ponto exato da falha:

1. descoberta do arquivo;
2. ingestão;
3. classificação;
4. leitura;
5. identidade;
6. competência;
7. vínculo ao cliente;
8. persistência;
9. inclusão na composição da Conferência.

A tela de ocorrência deve expor em qual estágio o documento ficou retido.

## 9. eConsignado precisa de conclusão contextual, não resposta isolada da API

Os casos D A F Castro, D&L Alimentos, Empório Frios Itapaci, GL Auto Center, Lourenconi & Modesto, Predileta e Ribeiro e Nascimento Art Vidros confirmam que retorno da API não pode ser tratado sozinho como verdade operacional final.

A conclusão deve considerar:

- vínculo ativo;
- data de desligamento;
- remuneração na competência;
- afastamento;
- pagamento direto comunicado;
- rescisão;
- garantias;
- identificador do contrato;
- duplicidades/repetições do retorno.

Retorno positivo residual sem vínculo/remuneração compatível deve virar observação ou inconsistência a confirmar, não bloqueio automático.

## 10. Gate único de autorização de saída

Os achados de Impressão, Entregas e Saídas automáticas são o mesmo defeito arquitetural em três lugares: autorização distribuída e incompleta.

Deve existir um único gate canônico de backend reutilizado por todas as saídas.

### Requisitos mínimos

Para competência sob Fechamento Mensal, liberar saída final somente quando:

- cliente está `FECHADA`;
- não existe retificação material pendente;
- a ação pertence ao cliente/competência autorizados;
- seleção manual por IDs é intersectada com o mesmo universo permitido.

`PROCESSADO` nunca autoriza saída final por si só.

Filtros visuais não são mecanismo de segurança.

## 11. Conferência deve ser cálculo puro e recalculada por evento

Abrir a Central de Conferência não pode criar histórico, fechar cliente ou alterar estado.

Eventos que podem disparar recálculo:

- processamento concluído de documento novo;
- promoção de candidato de reprocessamento;
- anexo processado pela ocorrência;
- decisão/justificativa por fonte;
- alteração válida de movimento mensal;
- conclusão de retificação;
- alteração persistida de chamada.

Consulta de tela permanece somente leitura.

## 12. Matriz dos 28 casos por mecanismo central

### Reprocessamento/versionamento

Casos: 1, 2, 5, 11, 16 e 26.

### Descoberta/leitura/vínculo

Casos: 5, 8, 11, 13 e 16.

### FGTS rescisório/múltiplas evidências

Casos: 2, 4, 12, 17, 24 e 25.

### Aplicabilidade/obrigação zerada ou substituída

Casos: 7, 9, 10, 14, 15, 18, 20, 21, 23 e 28.

### eConsignado contextual

Casos: 6, 7, 12, 14, 19, 24 e 25.

### Decisão/justificativa específica por fonte

Casos: 3, 22 e 24, além de cenários correlatos dos casos 2 e 14.

### Chamada/estado mensal

Caso 27.

Um mesmo caso pode pertencer a mais de um mecanismo; isso é esperado e demonstra por que correções pontuais por cliente não são aceitáveis.

## 13. Falha funcional paralela ainda pendente

A suíte do ZIP canônico já confirmou uma falha funcional fora do núcleo de fechamento:

- `classificacao_inativacao` pode chegar como string e o repositório assume sempre Enum (`.value`).

Ela continua pendente de correção antes de qualquer pacote final, mas não deve ser misturada conceitualmente com as regras de Conferência.

## 14. Critérios de regressão acrescentados nesta etapa

Antes de considerar V8 homologável, além dos critérios anteriores:

1. decisão de DARF não pode resolver FGTS/eConsignado implicitamente;
2. obrigação não aplicável não pode aparecer como documento ausente;
3. candidato de reprocessamento pior deve ser rejeitado sem tocar na versão vigente;
4. candidato rejeitado deve permanecer auditável;
5. Jair deve consolidar federal uma vez e FGTS em R$ 389,04;
6. Leosmar não pode sofrer soma indevida de documentos equivalentes;
7. múltiplas GFD devem distinguir obrigação econômica de reemissão;
8. documentos existentes não vinculados devem indicar o estágio exato da falha;
9. eConsignado residual sem contexto compatível não pode bloquear sozinho;
10. Impressão, Entregas e Saídas automáticas devem usar o mesmo gate de backend;
11. abrir/atualizar a tela de Conferência não pode escrever no fechamento;
12. mudança de chamada deve ser persistida e auditada imediatamente;
13. regressão completa dos 28 casos precisa ser executada antes do pacote final.

## 15. Estado ao final da Etapa 3

A arquitetura funcional necessária está mais bem delimitada, mas a auditoria permanece aberta.

Não há evidência nesta etapa de que o ZIP canônico já implemente os mecanismos acima. Portanto:

- nenhum achado é considerado corrigido apenas por estar documentado;
- nenhum pacote final deve ser gerado;
- a próxima etapa deve confrontar estes contratos com a implementação do pacote canônico e montar a matriz de regressão executável dos 28 casos.
