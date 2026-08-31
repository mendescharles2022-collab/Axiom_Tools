# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **DIAGNÓSTICO B01–B50 REVISTO / RUNTIME INTEGRAL AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico do tooling

GitHub Actions run `33196049264`  
Commit `eb695be6531c7711ac36b3f45e0d9d31eb809233`  
Python 3.12.14

```text
Ran 165 tests in 1.115s
OK
```

Preflight daquele marco:

- B homologados `0/50`;
- C PASS `0/28`;
- evidências externas `1/10`;
- release READY `False`;
- build OK `False`.

Artifact `v8-release-preflight`:

- ID `9695772154`;
- 2.288 bytes;
- SHA-256 `380162c6ed4b1d5b01b0f7c7c834f8f1d300699db54b4b050ed967b5e9181d85`.

Os 165 testes continuam válidos para o commit acima, mas não representam ainda a árvore operacional integral reconciliada nem os achados posteriores das Etapas 42–52.

## 2. Continuação de 31/08/2026 — Etapas 42 a 52

A auditoria foi retomada sem reiniciar o trabalho anterior.

Novos marcos registrados:

- Etapa 42 — cobertura incompleta do tooling de reconciliação para config/identidade;
- Etapa 43 — B01/B02 reconfirmados no V8F2 e validador de instalação com side effect;
- Etapa 44 — origem histórica B02 isolada no salto V6 → V7; investigação B08 refinada;
- Etapa 45 — causa arquitetural B03 isolada em autorização espalhada por UI/view;
- Etapa 46 — B07/B09/B10 isolados; mitigação válida B11/V8A preservada;
- Etapa 47 — B12–B17: colapso para último Extrato/GFD e ausência de identidade econômica;
- Etapa 48 — B18–B23: decisão global, aplicabilidade e correções parciais V8F2;
- Etapa 49 — B24–B28/eConsignado;
- Etapa 50 — B29–B33/parser, competência, IRRF e calendário;
- Etapa 51 — B34–B40/banco, segurança e concorrência;
- Etapa 52 — B41–B50/instalação, UX, escala, Sintegra, retenção e acervo.

Com isso, **B01–B50 possuem diagnóstico/restrição de evidência revisados até os deltas mais recentes disponíveis nesta sessão**.

Isso não significa correção nem homologação dos 50 bloqueadores.

## 3. Snapshot formal de estados

O arquivo canônico de status ainda não foi promovido apenas com base em inspeção de patches.

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 35 |
| `INSPECAO_PENDENTE` | 8 |
| `EM_CORRECAO` | 3 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: B35, B41, B42.  
Bloqueados pelo runtime: B05, B06, B45, B49.

Regra de governança mantida: **patch encontrado ≠ teste executado ≠ homologação**.

## 4. Runtime/pacote operacional preservado

Foi localizada no acervo a cópia:

`Axiom_Tools(20260827-175623).zip`

com 399.270.206 bytes, coincidente com a base canônica da auditoria de 27/08.

A plataforma não permitiu materializar seus bytes nesta sessão.

Foi materializada, porém, a cadeia de deltas V → V8F2, incluindo o pacote:

`AXIOM_TOOLS_V5_6_14V8F2_CONSOLIDADO_20260827.zip`

SHA-256 calculado na Etapa 43:

`E30B4189F883F1B8FB0B48574C36FF72DA7EE8679B7118E96FDEF17BF93AB2D2`

Esses deltas são evidência operacional válida sobre os arquivos que contêm, mas não substituem B06.

## 5. B06 — gate para implementação consolidada

Não implementar B01/B02/B03 sobre a fundação reduzida da `main` como se ela fosse o runtime final.

Infraestrutura do `main` já existente:

- exportador runtime com whitelist/bloqueio de conteúdo sensível;
- launcher PowerShell;
- auditor de reconciliação/manifesto;
- E2E;
- preflight automático/artifact.

Revisão aberta pela Etapa 42 antes do uso final:

1. incluir configuração-modelo e metadata/identidade de release no export seguro;
2. comparar configuração/identidade no auditor;
3. adicionar regressões dessa cobertura;
4. evitar caminhos absolutos desnecessários nos artefatos;
5. reexecutar a suíte canônica.

Após isso:

1. reconciliar instalação Windows/pacote canônico integral;
2. recuperar árvore e suíte operacional completas;
3. estabelecer baseline;
4. implementar os contratos sobre a árvore real.

## 6. Correções parciais válidas encontradas e que devem ser preservadas

A auditoria não deve apagar trabalho bom enquanto corrige regressões.

### V8A

- distinção visual entre `Aguardando processamento` e `Em conferência` baseada na existência real de dossiê, mitigando B11.

### V8F2 — FGTS zero (B19)

- quando o Extrato da competência informa FGTS zero, essa evidência prevalece sobre `fgts_esperado` cadastral;
- o código é coerente com a regra canônica;
- o validador, porém, pode passar com `zeros_validos=0`, portanto ainda falta regressão real representativa.

### V8F2 — eConsignado (B26)

- MTE/Dataprev positivo sem fonte local/recolhimento retorna `AGUARDANDO_FONTES`, não `CONFERIDO`;
- o validador contém checagem direta dessa função;
- falta regressão integrada/caso D A F Castro na árvore reconciliada.

### V8F2 — competência e-CAC (B31)

- reconhecimento ampliado de período de apuração;
- `competencia_metodo` preservado no resultado do especialista;
- falta modelo completo de proveniência/ranking de força.

### V8F2 — Pendências (B43)

- abre por padrão na competência ativa;
- backend pagina e filtra;
- PROC permanece disponível como detalhe/filtro técnico.

### V8F2 — relatório (B44)

- CSS define `A4 portrait`, tabela fixa, cabeçalho repetível e quebra controlada;
- teste atual é apenas estático, não prova impressão real.

### Segurança de rotas (B38)

Nos deltas materializados inspecionados:

- V8A: 13/13 POSTs com `login_required/admin_required`;
- V4: 36/36;
- V8F2: 30/30;
- formulários POST materializados possuem `csrf_token`.

Isso preserva a fundação de autenticação/CSRF. A pendência maior está em autorização de negócio, concorrência e prova da árvore completa.

## 7. Bloqueadores críticos com causa já suficientemente isolada

### B01 — reprocessamento destrutivo

V8F2 ainda:

1. snapshot;
2. DELETE vigente/pessoas;
3. `commit()`;
4. nova leitura.

Precisa virar candidato separado + promoção atômica.

### B02 — GET com mutação

Origem histórica isolada no salto V6 → V7: fechamento automático foi colocado dentro de `conferencia_competencia()`, função reutilizada por GETs.

A correção é retirar mutação do agregador de leitura e disparar fechamento por evento persistido.

### B03/B39 — saída e IDs

Entregas/Impressão aplicam filtros diferentes nas views, mas serviços aceitam `PROCESSADO`/IDs recebidos sem gate único por versão FECHADA.

### B07/B09/B10

`clientes_conferencia_ids()` recuperado inclui:

- PRONTA da chamada atual;
- FECHADA;
- RETIFICACAO.

FECHADA e RETIFICACAO precisam sair da mesa viva normal e o universo deve ser centralizado no domínio Closing.

### B12–B17/B50

Conference e retificação reduzem Extrato/GFD ao “último documento do tipo”. Hash físico ainda não representa identidade documental/econômica.

### B18/B23

Decisão manual segue global por `competencia + cliente`, podendo justificar/fechar cliente inteiro apesar de outra fonte pendente.

### B37/B46

Monitor ainda possui dupla verdade:

- persistência pode ficar `COM_PENDENCIAS`;
- UI calcula `PROCESSAMENTO_CONCLUIDO` quando percentual chega a 100%.

### B40

Transições críticas leem estado e depois executam UPDATE por `competencia + cliente_id` sem compare-and-set do estado/chamada/revisão lidos.

Risco concreto de lost update permanece.

## 8. B08/T L — investigação atualizada

Falha operacional permanece confirmada: T L deveria estar na 2ª chamada e apareceu `PRONTA` chamada 1.

A Etapa 44 recuperou o `closing/service.py` completo do V8B suficiente para eliminar hipóteses:

- `sincronizar_clientes_ativos()` não sobrescreve linha existente ADIADA;
- `aplicar_classificacao_cadastral()` só atua em PRONTA;
- `sincronizar_resultados_conferencia()` ignora ADIADA;
- migrações V7/V8/V8A recuperadas não reabrem ADIADA genericamente.

Continuam candidatos:

- persistência inicial que nunca consolidou corretamente ADIADA/chamada 2;
- `liberar_clientes()`/avanço explícito;
- operação concorrente/lost update — risco reforçado por B40;
- código externo não recuperado no delta.

B08 segue `INSPECAO_PENDENTE`; não aplicar correção especulativa.

## 9. B41 — rollback do V8F2 é insuficiente para V8 final

O instalador V8F2:

- copia apenas nove arquivos para backup;
- não copia SQLite/configuração local;
- valida contra banco real;
- o `try/catch` termina antes do restart/health-check;
- falha de backend/gateway depois disso não aciona restauração automática.

A Etapa 43 ainda mostrou que a validação funcional pode mutar fechamento por B02.

O tooling genérico de rollback do `main` continua patrimônio útil, mas precisa ser aplicado/testado ao conjunto real Windows.

## 10. B42 — proveniência

O V8F2 contém `SHA256SUMS.txt`, porém:

- instalador não verifica os hashes;
- pacote não carrega commit/schema canônicos ligados à release;
- runtime usa múltiplas strings internas de versão;
- não há prova de consumo de `config/release_identity.toml`.

A proveniência do `main` continua `EM_CORRECAO` até runtime, health, logs, instalador e pacote consumirem a mesma identidade.

## 11. B45 — desempenho

Avanços:

- paginação backend em Processamentos/Pendências/Monitor;
- `COUNT + LIMIT/OFFSET` nas listagens auditadas.

Pendências:

- `listar_sessoes()` possui N+1 por sessão;
- `status_sessao()` executa aproximadamente uma dúzia de consultas no caminho completo;
- a tela faz polling a cada 2 segundos;
- não existe benchmark final >600 clientes/query plans/locks sobre runtime reconciliado.

## 12. B47 — Sintegra

A regressão ficou historicamente isolada:

- V5.6.14V: template possuía `Sintegra Nacional` e `Sintegra Goiás`;
- V1 substituiu o template e removeu os botões;
- backend continuou entregando as duas URLs;
- V3A/V4 materializados continuam sem os atalhos.

Correção deve apenas restaurar os botões, preservando a modelagem atual de inscrições.

## 13. B48/B49

### Retenção B48

O `main` possui planner/simulação, mas os deltas não mostram ferramenta operacional integrada com `Simular → revisar → confirmar → executar → relatório` e gates de acervo.

### Banco ↔ filesystem B49

`audit_db_filesystem_links.py` oferece boa base read-only para banco -> filesystem, com root seguro, path traversal, symlink, tamanho e SHA-256.

Ainda falta:

- execução em banco/acervo real;
- direção filesystem -> banco para achar arquivo existente não indexado;
- ocorrência técnica automática para órfãos físicos relevantes.

## 14. B35 — invariantes

Estado `EM_CORRECAO`.

Continuam comprovadas no `main`:

1. `FECHADA` sem versão é inválida;
2. `versao_atual` precisa apontar para versão existente.

Pendente:

- `PRAGMA integrity_check` real;
- `PRAGMA foreign_key_check` real;
- invariantes adicionais comprovadas pelo schema reconciliado;
- antes/depois de migração e instalação.

## 15. Gate final

Ferramentas atuais:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`.

Modo final continua exigindo:

- 50/50 B homologados;
- 28/28 C PASS;
- release READY;
- build verificável;
- dez gates externos PASS.

## 16. Ordem de correção após B06

1. baseline + suíte operacional original;
2. B01 — candidato não destrutivo;
3. B02 — Conference/GET puro + evento de fechamento;
4. B03/B39 — gate único de saída e IDs;
5. B07/B09/B10/B11/B37 — universos/máquinas de estado;
6. B40/B08 — transições versionadas/CAS e regressão T L;
7. B18/B36 + schema B05 — decisão por fonte e migração do legado;
8. B12/B13/B14/B17/B50 — composição multi-documento e identidade econômica;
9. B15/B16/B49 — descoberta, vínculo PF/CAEPF e auditoria bidirecional;
10. B19–B23 — aplicabilidade, preservando correções válidas V8F2;
11. B24–B28 — eConsignado no orquestrador e contexto;
12. B29–B33 — parser Domínio/competência/proveniência/13º;
13. B34/B35/B38 — bordas de dados, invariantes e segurança final;
14. B43/B44/B46/B47 — UX/regressões finais;
15. B45/B48 — benchmark e manutenção segura;
16. C01–C28;
17. build/proveniência final;
18. instalação Windows + rollback comprovado.

## 17. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

A auditoria de diagnóstico B01–B50 avançou até a Etapa 52. O próximo salto de valor é reconciliar B06 e executar as correções sobre a árvore operacional real, preservando explicitamente os avanços válidos identificados nos patches.