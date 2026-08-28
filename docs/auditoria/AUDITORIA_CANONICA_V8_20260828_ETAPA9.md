# Auditoria canônica V8 — Etapa 9

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo desta etapa

A Etapa 9 aprofundou quatro frentes estruturais necessárias antes da correção final:

- segurança transacional das mutações V8;
- modularização/fonte única de regras;
- schema e migração aditiva para decisão por fonte e reprocessamento versionado;
- transição da suíte de testes V7 para os contratos V8.

## 2. Segurança transacional — baseline existe, V8 precisa revalidação

A AXT-003 já exigia:

- transações;
- rollback;
- SQL parametrizado;
- autenticação/autorização de backend;
- CSRF para POSTs persistentes/destrutivos.

A Auditoria V4 chegou a registrar todas as rotas de negócio protegidas naquela fotografia.

Porém o `main` atual não contém a árvore V8 integral e seu `pyproject.toml` possui `dependencies = []`, apesar do runtime operacional conhecido usar Flask/Flask-WTF/Waitress.

Conclusão correta: não declarar CSRF ausente/presente com base no `main` incompleto. A segurança V8 deve ser revalidada na árvore operacional reconciliada.

Foi criado contrato para garantir atomicidade e idempotência em:

- reprocessamento;
- mudança de chamada;
- decisão por fonte;
- fechamento;
- retificação;
- inativação/reativação;
- impressão/entrega;
- enriquecimento cadastral.

## 3. Reprocessamento — transação precisa proteger a versão boa

O defeito destrutivo já comprovado exige que a promoção de candidato seja a unidade transacional.

A versão vigente permanece intocada até o candidato ser validado.

A promoção deve manter coerentes:

- documento lógico;
- versão vigente/candidata;
- itens/pessoas relacionados;
- identidade;
- competência;
- inscrição de origem;
- histórico;
- disparo de recálculo da Conferência.

Falha antes da promoção não toca a versão vigente.

## 4. Modularização — risco estrutural confirmado

A auditoria do ZIP já registrou:

- `central.py` ~93 KB / >2 mil linhas;
- `documents_views.py` ~73 KB / >1,7 mil linhas;
- helpers duplicados entre `conference.py` e `operations.py`;
- regra antiga `_check_darf_folha` sobrevivendo fora do fluxo canônico.

A correção não deve virar reescrita geral.

Estratégia aprovada:

1. extrair política pura;
2. cobrir com testes;
3. redirecionar um caminho por vez;
4. executar regressão real;
5. remover duplicidade apenas após provar ausência de uso.

Views não decidem regra de fechamento/consolidação/gate.

## 5. Schema V8 — evolução aditiva

A árvore real já possui:

- `fechamento_mensal`;
- `fechamento_mensal_cliente`;
- `fechamento_mensal_historico`;
- `fechamento_mensal_versao`;
- `fechamento_mensal_retificacao`.

A V8 deve reutilizar essa fundação, não criar um segundo mecanismo de versões.

Novas necessidades persistentes:

- estado/decisão por `competencia + cliente + fonte`;
- vínculo entre obrigação e múltiplas evidências/documentos;
- natureza da evidência (reemitida, sucessora, matrícula distinta, rescisória etc.);
- candidato/versionamento do reprocessamento documental;
- identificação inequívoca de vigente x candidato.

## 6. Migração da decisão global antiga — risco crítico evitado

A decisão manual legada é global por cliente/competência.

É proibido fazer backfill assim:

```text
cliente legado JUSTIFICADO
=> DARF JUSTIFICADA + FGTS JUSTIFICADO + eConsignado JUSTIFICADO
```

Isso reproduziria exatamente a falha antiga.

Política:

- histórico fechado legado permanece agregado;
- converter automaticamente por fonte somente se a origem estiver inequivocamente identificada;
- ambiguidade permanece como legado histórico, sem autorizar silenciosamente fontes da V8;
- competências abertas devem recalcular pelas evidências atuais.

## 7. Evidência multi-documento no schema

A Conferência deve relacionar obrigação a documentos existentes, sem duplicar PDFs.

A relação precisa permitir distinguir:

- principal;
- complementar;
- reemissão equivalente;
- sucessora;
- unidade/matrícula distinta;
- rescisória;
- antecipada;
- justificativa/anexo externo.

Isso é necessário para Jair, Leosmar e múltiplas GFD.

## 8. Migração precisa preservar história, não fabricar detalhe retroativo

Competências fechadas antes da V8 podem não possuir detalhe por fonte.

A UI pode identificar essas competências como fechamento legado agregado.

Não fabricar retrospectivamente estados DARF/FGTS/eConsignado que nunca foram registrados.

Também é proibido:

- marcar todas as fontes como conferidas só porque o cliente está FECHADA;
- tratar PROCESSADO como evidência conferida;
- apagar reprocessamentos ruins do histórico;
- usar migração de schema como motor de correção dos 28 casos.

## 9. Testes V7 que precisam transição legítima

A documentação V7 confirma regras que foram superadas pela V8:

- `PRONTA` apresentada diretamente como `Em conferência`;
- Central padrão incluía liberadas + fechadas;
- decisão manual global podia concluir o ciclo;
- retificação podia aparecer no escopo amplo da Conferência.

A V8 altera esses comportamentos.

Logo, testes que ainda os protejam devem ser substituídos por novos testes, e não mantidos artificialmente.

## 10. Testes antigos que continuam válidos

Preservar/reforçar:

- próxima chamada fora do ciclo atual;
- sem movimento mensal separado do cadastro permanente;
- impressão/entrega exigindo FECHADA;
- retificação preservando versão anterior;
- saída bloqueada durante retificação;
- histórico de mudanças;
- rollback/migração segura.

## 11. Documentos produzidos nesta etapa

- `CONTRATO_TRANSACOES_SEGURANCA_MUTACOES_V8.md`;
- `CONTRATO_MODULARIZACAO_REGRAS_V8.md`;
- `CONTRATO_SCHEMA_MIGRACAO_V8.md`;
- `MAPA_TESTES_LEGADOS_V7_PARA_V8.md`;
- este documento.

## 12. Estado ao final da Etapa 9

A auditoria funcional/arquitetural está suficientemente detalhada para impedir correções pontuais e migrações perigosas, mas ainda não existe homologação de implementação.

Continuam sem prova de correção no runtime canônico:

1. reprocessamento candidato/versionado;
2. recuperação Jair 449/450;
3. composição multi-documento;
4. decisão por fonte;
5. Conference read-only;
6. gate único de saída;
7. eConsignado Etapa 0 e universo mensal;
8. inativação string/Enum;
9. transição T L para 2ª chamada;
10. aba Pendências filtrada por competência;
11. relatório A4;
12. Sintegra GO integrado e atalhos restaurados;
13. migração aditiva testada sobre cópia da base real;
14. suíte V8 atualizada e executada;
15. reconciliação `main` x árvore operacional;
16. regressão Windows/instalador.

Nenhum pacote V8 deve ser liberado antes dessas verificações.
