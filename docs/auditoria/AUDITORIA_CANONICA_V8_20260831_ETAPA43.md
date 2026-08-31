# Auditoria canônica V8 — Etapa 43

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Objetivo

Prosseguir após a Etapa 42 usando evidência operacional preservada fora da árvore reduzida do `main`, sem promover automaticamente nenhum artefato parcial a runtime canônico.

## 2. Pacote canônico localizado no acervo

Foi localizada uma cópia preservada de:

`Axiom_Tools(20260827-175623).zip`

Tamanho registrado no acervo: `399.270.206 bytes`.

Esse nome coincide com o ZIP já tratado pela auditoria anterior como pacote canônico de 27/08/2026.

Nesta sessão, a plataforma de arquivos recusou a materialização desse ZIP grande com erro de acesso interno. Portanto:

- sua existência ficou novamente comprovada;
- seus bytes não foram reabertos nesta etapa;
- nenhum novo hash foi atribuído;
- B06 continua sem reconciliação byte a byte da árvore completa.

## 3. Artefato complementar V8F2 materializado

Também foi localizada e materializada com sucesso a atualização:

`AXIOM_TOOLS_V5_6_14V8F2_CONSOLIDADO_20260827.zip`

Tamanho: `76.124 bytes`.

SHA-256 calculado nesta etapa:

`E30B4189F883F1B8FB0B48574C36FF72DA7EE8679B7118E96FDEF17BF93AB2D2`

O ZIP contém 12 entradas e o instalador declara substituir nove arquivos operacionais. Trata-se de **delta de atualização**, não de árvore completa; por isso não resolve B06, mas é evidência operacional válida sobre os arquivos que contém.

Arquivos centrais auditados:

- `modules/processing/conference.py` — SHA-256 `0A5CF202FFA13B68CCE791D62F5D29663DAFBFA4E01E86478B6A6E8B377EC8E5`;
- `modules/processing/central.py` — SHA-256 `39D0DC013D99931696CACC77F7FE3C1CAA89BCC232B5E115573910EE3733FA1A`;
- `web/views/documents_views.py` — SHA-256 `61F60701F205E94383E92F1F2DA6A26378165CE511390D87F8B7CDAD54DEA085`.

## 4. B02 confirmado novamente no V8F2

O registro canônico define B02 como `Conference GET com mutação`.

No `documents_views.py` do V8F2, a rota GET:

`/processamento/guias`

monta a página chamando `conferencia_competencia(...)` quando existe competência selecionada.

No `conference.py` do mesmo pacote, `conferencia_competencia(...)`:

1. monta as linhas de conferência;
2. verifica se existe controle de fechamento ativo;
3. ao final chama `sincronizar_resultados_conferencia(con, competencia, linhas)`;
4. se houver sincronizações, recalcula o resumo de fechamento.

Portanto a consulta GET continua alcançando rotina de sincronização de fechamento.

Isso coincide exatamente com o defeito descrito em `CONTRATO_CONFERENCIA_EVENT_DRIVEN_V8.md`: abrir/atualizar a Central não pode alterar estado mensal, criar histórico ou produzir fechamento.

Conclusão: **B02 permanece confirmado no V8F2** e não pode ser considerado regressão já corrigida pelo consolidado de 27/08.

## 5. B01 confirmado novamente no V8F2

O registro canônico define B01 como `Reprocessamento destrutivo`.

No `central.py` do V8F2, `reprocessar_arquivo(...)` executa a seguinte ordem:

1. recupera o registro vigente;
2. grava `_snapshot_reprocessamento(...)`;
3. identifica os registros afetados;
4. executa `DELETE FROM processamento_item_pessoa ...`;
5. executa `DELETE FROM processamento_arquivo ...`;
6. executa `commit()`;
7. somente então chama `processar_conteudo_misto(...)` para criar a nova leitura.

Se a nova leitura falhar, o fluxo retorna erro depois de a interpretação vigente já ter sido removida do conjunto ativo.

Isso viola a regra de `CONTRATO_REPROCESSAMENTO_CANDIDATO_V8.md`, que exige:

- preservar a versão vigente;
- processar candidato separado;
- rejeitar candidato pior sem tocar na vigente;
- promover apenas em operação atômica.

Conclusão: **B01 permanece confirmado no V8F2**.

## 6. Novo reforço B02/B41 — validador de instalação não é somente leitura

O instalador `INSTALAR_14V8F2.ps1`:

- valida existência do banco operacional;
- copia nove arquivos de código/UI para backup;
- não inclui o SQLite nesse backup de atualização;
- substitui os arquivos;
- executa `VALIDAR_14V8F2.py` contra o banco indicado pelo runtime;
- em falha de validação, restaura apenas os arquivos do backup.

O validador `VALIDAR_14V8F2.py`, por sua vez, chama:

`conferencia_competencia(con, competencia_ativa, escopo_fechamento="CICLO")`

contra a conexão do banco utilizada na validação.

Como a função de conferência contida no próprio V8F2 ainda chama `sincronizar_resultados_conferencia(...)`, a validação de instalação percorre exatamente o caminho conhecido de B02.

Consequências de auditoria:

- o smoke/validador não é comprovadamente side-effect-free;
- a validação pode alcançar mutações de fechamento enquanto testa o pacote;
- o rollback local do instalador restaura arquivos, mas não possui cópia do banco nesse fluxo;
- `porta respondeu` e `V8F2_FUNCIONAL_OK` não são evidência suficiente de preservação do estado de negócio.

Esse achado reforça B02 e B41. Não cria novo bloqueador B51.

## 7. Cobertura do validador V8F2

`VALIDAR_14V8F2.py` verifica pontos específicos, entre eles:

- competência operacional definida;
- reconhecimento de competência em DARF;
- identificação de dois documentos/clientes conhecidos;
- reforço contextual e-CAC;
- eConsignado aguardando fontes/conferido;
- listagem de pendências;
- regra de FGTS zero;
- CSS A4 retrato.

Ele **não** prova:

- B01 candidato não destrutivo;
- B02 leitura pura;
- integridade antes/depois da Conferência;
- rollback de banco;
- idempotência de fechamento;
- preservação de histórico após falha de reprocessamento.

## 8. Estados dos bloqueadores

Nenhum estado é promovido nesta etapa.

- B01 permanece `PRONTO_PARA_CORRIGIR`;
- B02 permanece `PRONTO_PARA_CORRIGIR`;
- B06 permanece `BLOQUEADO_POR_RUNTIME` até reconciliação integral;
- B41 permanece `EM_CORRECAO`;
- B42 permanece `EM_CORRECAO`.

## 9. Próximo passo

Continuar a exploração segura dos artefatos operacionais preservados que puderem ser materializados, priorizando evidências capazes de:

1. completar o mapa B01/B02/B03;
2. recuperar dependências necessárias à futura correção;
3. aproximar B06 sem confundir delta V8F2 com runtime completo;
4. manter banco, documentos e credenciais fora do repositório.

A V8 permanece **NÃO HOMOLOGADA**.
