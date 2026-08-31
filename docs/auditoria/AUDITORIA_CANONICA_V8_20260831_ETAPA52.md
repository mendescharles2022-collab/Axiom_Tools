# Auditoria canônica V8 — Etapa 52

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Fechamento do bloco B41–B50 a partir dos deltas operacionais preservados e da infraestrutura já existente no `main`:

- B41 — backup/rollback;
- B42 — proveniência de build;
- B43 — Pendências orientada por PROC;
- B44 — relatório A4 retrato;
- B45 — escala >600 clientes;
- B46 — Monitor duplicado/confuso;
- B47 — Sintegra;
- B48 — limpeza/retention;
- B49 — banco ↔ filesystem;
- B50 — hash ≠ obrigação.

Nenhum achado desta etapa autoriza pacote final.

## 2. B41 — instalador V8F2 não atende ao contrato de rollback da V8

O `INSTALAR_14V8F2.ps1` executa pré-validação e cria backup dos nove arquivos substituídos, porém não inclui no backup:

- `data/axiom_tools.db`;
- configurações locais operacionais;
- estado completo necessário para rollback coerente;
- inventário de versão/schema do banco.

O fluxo faz:

1. valida existência do banco;
2. compila Python do payload;
3. copia os nove arquivos atuais para `backups/processamento-v5-6-14v8f2-*`;
4. substitui os arquivos;
5. executa `VALIDAR_14V8F2.py` contra o banco operacional;
6. em falha **dentro desse bloco**, restaura apenas os arquivos.

### 2.1 Limite do `try/catch`

O bloco `try/catch` termina antes de:

- parar processos nas portas 5200/5201;
- iniciar backend;
- aguardar `/health` 5201;
- iniciar gateway;
- aguardar health 5200;
- confirmar caminho real do módulo importado.

Logo, se backend/gateway/import-check falhar depois da substituição, o instalador lança erro sem executar o rollback de arquivos já aplicado.

### 2.2 Banco real durante validação

Como registrado na Etapa 43, o validador chama `conferencia_competencia(...)` contra o banco real e essa função ainda possui efeito de sincronização de fechamento no V8F2.

Assim, mesmo o rollback parcial de código não consegue reverter eventual efeito de banco produzido durante a validação.

### 2.3 Ordem operacional

O contrato V8 exige bloquear operação/parar writers antes de backup/migração e validar rollback como conjunto coerente. O V8F2 substitui/valida código antes de encerrar os serviços nas portas 5200/5201.

### Conclusão

B41 permanece **EM_CORRECAO**. O V8F2 possui backup útil de arquivos, mas não constitui rollback homologável da V8.

Correção futura precisa incluir banco/configuração, escopo transacional de instalação, falhas pós-startup e smoke side-effect-free.

## 3. B42 — há hashes de payload, mas eles não formam proveniência de build

O V8F2 contém `SHA256SUMS.txt` com hashes de:

- instalador;
- validador;
- nove arquivos do payload.

Isso é patrimônio útil e deve ser preservado.

Entretanto:

- `INSTALAR_14V8F2.ps1` não lê `SHA256SUMS.txt`;
- não executa `Get-FileHash`/verificação equivalente;
- não existe, no pacote, commit Git da origem;
- não existe schema version associado ao pacote;
- a versão `V5.6.14V8F2` está hardcoded no nome/textos do instalador;
- módulos internos possuem identidades independentes como `PROCESSAMENTO-2.7-14T5`, `ECAC-2.5-V8F2` e `MOTORES-3.6-V8F2`;
- nenhuma evidência liga esses identificadores ao `config/release_identity.toml` do repositório.

O instalador comprova apenas que o import Python aponta para a raiz esperada, não que o runtime carregado corresponda a um commit/build canônico.

A Etapa 42 já registrou também que o tooling de reconciliação precisa incorporar config/identidade.

### Estado

B42 permanece **EM_CORRECAO**.

Hashes existem, mas precisam ser verificados e incorporados a uma identidade única `release + commit + schema + manifesto` consumida pelo runtime e instalador.

## 4. B43 — Pendências recebeu correção funcional real no V8F2, mas PROC ainda é dimensão visível da tela

### 4.1 Competência ativa como default

A rota GET `/processamento/pendencias` V8F2 faz:

```python
if "competencia" not in request.args:
    cfg = obter_config_processamento(conexao)
    competencia = cfg.get("competencia_ativa")
```

Portanto a tela abre, por padrão, dentro da competência operacional ativa. Isso corrige o comportamento anterior de uma fila global orientada principalmente por PROC.

### 4.2 Filtro técnico de PROC continua disponível

O template mantém:

```text
Todas as PROC
```

como filtro ao lado de busca/origem/competência, e cada documento exibe sua `chave_processamento` como detalhe técnico.

Esse uso é aceitável como dimensão avançada, desde que não volte a ser a chave principal da operação.

### 4.3 Backend da listagem

`listar_pendencias(...)` V8F2:

- filtra no SQL por competência/chave/origem/causa;
- usa `COUNT(*)` separado;
- pagina com `LIMIT/OFFSET`;
- aceita 10/25/50/100 por página;
- exclui ZIP agregador da fila documental;
- limita lista de chaves a 300 e, quando há competência, busca somente chaves daquela competência.

Esse é avanço funcional concreto.

### Classificação

B43 deve ser tratado como **correção substancial implementada no V8F2 / homologação integrada pendente**.

Não promover ainda a `CORRIGIDO_TESTADO` porque o delta não foi executado sobre a árvore reconciliada e a tela completa não passou regressão Windows desta auditoria.

## 5. B44 — A4 retrato foi implementado no CSS, mas o validador só verifica texto estático

`processing-hub.css` V8F2 contém:

```css
@media print {
  @page { size:A4 portrait; margin:8mm 7mm }
  ...
  .ax-report-table table { table-layout:fixed; font-size:7.2pt; }
  .ax-report-table thead { display:table-header-group; }
  .ax-report-table tr { break-inside:avoid; page-break-inside:avoid; }
  ...
}
```

Também remove navegação/topbar/sidebar na impressão e força quebra de texto dentro das células.

Isso atende estruturalmente vários requisitos do contrato de relatório.

### Validador V8F2

O teste do pacote apenas faz:

```python
assert "@page{size:A4 portrait" in css
assert "table-layout:fixed!important" in css
```

Ele não:

- renderiza relatório real;
- abre print preview;
- mede overflow/corte;
- prova cabeçalho repetido em múltiplas páginas;
- prova conteúdo longo de Pendências/Auditoria;
- valida Chrome/Firefox/Edge no Windows alvo.

### Estado

B44 possui **implementação CSS coerente + teste estático**, mas permanece sem homologação visual/física de impressão.

Não promover a `CORRIGIDO_HOMOLOGADO`.

## 6. B45 — há melhorias de paginação, mas N+1 e polling pesado permanecem visíveis

### 6.1 Avanços reais

O V8F2 implementa backend pagination em:

- Processamentos;
- Pendências;
- Monitor operacional/auditoria.

`listar_pendencias(...)` usa `COUNT + LIMIT/OFFSET` e métricas agregadas, sem carregar todos os documentos da fila na memória para paginar.

`operations.monitor(...)` V4 também usa `COUNT + LIMIT/OFFSET`.

Esses pontos devem ser preservados.

### 6.2 N+1 em `listar_sessoes(...)`

No `queue.py` preservado até V8F:

1. uma query carrega até 50 sessões;
2. para **cada sessão**, executa query de contagem por estado;
3. para **cada sessão**, `_resumo_documentos_chave(...)` executa outra consulta agregada e uma consulta de recentes.

Logo a listagem de sessões possui padrão N+1 evidente, crescendo linearmente em queries adicionais por sessão.

### 6.3 `status_sessao(...)` em polling

A tela `processing_queue.html` consulta `/processamento/fila/status` a cada **2 segundos**.

A função `status_sessao(...)` preservada possui aproximadamente uma dúzia de consultas SQL no caminho completo, incluindo:

- sessão;
- estados da fila;
- resumo documental;
- arquivo atual;
- blocos;
- etapas;
- fontes;
- competências;
- configuração;
- repositório;
- saídas;
- worker.

Isso significa carga frequente sobre SQLite enquanto o usuário permanece com o Monitor aberto.

### 6.4 Sem benchmark final

Nenhum benchmark representativo de >600 clientes, query plan ou lock contention foi executado nesta sessão sobre o runtime reconciliado.

### Estado

B45 permanece **CONFIRMADO_RUNTIME / TESTE_PENDENTE_RUNTIME**.

A V8 trouxe paginação útil, mas ainda não atende ao critério de ausência de N+1 evidente e escala comprovada.

## 7. B46 — a dupla verdade do Monitor continua exatamente presente no V8F preservado

`_atualizar_sessao(...)` persiste, ao terminar:

```text
CONCLUIDO
COM_ERROS
COM_PENDENCIAS
CANCELADO
```

Porém `listar_sessoes(...)` e `status_sessao(...)` fazem:

```python
if percentual >= 100:
    status_operacional = "PROCESSAMENTO_CONCLUIDO"
elif erros:
    ...
elif revisao:
    ...
```

Assim uma sessão persistida como `COM_PENDENCIAS` pode ser exibida como `PROCESSAMENTO_CONCLUIDO` só porque chegou a 100%.

Esse é o defeito canônico do B46 e permanece no `queue.py` do V8F materializado.

### Interface ainda redundante

O template `processing_queue.html` mostra simultaneamente:

- chip da sessão com percentual/status;
- percentual grande;
- barra de progresso;
- contador concluídos/total;
- bloco atual;
- etapa atual;
- origem;
- KPI `Atenção`;
- fluxo dos pacotes;
- blocos;
- fontes;
- destino/repositório/saídas;
- lista de documentos recentes.

Detalhes técnicos foram parcialmente colocados em `<details>`, o que é positivo, mas o destaque de percentual continua mesmo quando o processamento já terminou.

### Estado

B46 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

A correção deve primeiro criar uma única verdade técnica de sessão e só depois simplificar a UI.

## 8. B47 — regressão Sintegra pode ser rastreada na própria sequência de patches

A sequência materializada mostra:

### V5.6.14V

`clients/detail.html` contém explicitamente:

- botão `Sintegra Nacional`;
- botão `Sintegra Goiás`;
- ambos com `target="_blank"` e `rel="noopener"`.

### V5.6.14V1

O template `clients/detail.html` substituído pelo patch não contém mais os links Sintegra.

O backend, entretanto, continua entregando:

```python
sintegra_nacional = "https://www.sintegra.gov.br/"
sintegra_go = "https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.html"
```

### V3A e V4

Os templates de cliente materializados também continuam sem renderizar os atalhos.

Isso confirma o documento canônico `REGRESSAO_CLIENTES_SINTEGRA_20260828.md`: o backend preservou as URLs e a regressão ocorreu na camada visual do template.

### Estado

B47 permanece **CONFIRMADO_RUNTIME / correção simples e bem isolada**.

Não reverter a modelagem nova de inscrições; apenas restaurar os dois atalhos assistidos na ficha.

## 9. B48 — não existe rotina operacional de limpeza homologável nos deltas; o `main` possui apenas infraestrutura de planejamento

A busca nos deltas operacionais materializados não encontrou ferramenta de manutenção mensal com fluxo:

```text
Simular -> revisar -> confirmar -> executar -> relatório
```

Foram encontrados apenas usos pontuais de `unlink()` para arquivos temporários de geração/validação e ações de arquivamento no repositório híbrido.

Isso não equivale à ferramenta administrativa de retenção.

O `main` possui `scripts/plan_retention_cleanup.py` e testes associados, que são infraestrutura útil para **planejar/simular** política de retenção, mas não há evidência de integração runtime homologada capaz de executar a limpeza com todos os gates de segurança do contrato.

### Estado

B48 permanece **CONTRATO_OBRIGATORIO / implementação operacional pendente**.

Não usar rotinas temporárias existentes como justificativa para apagar acervo mensal.

## 10. B49 — auditor bidirecional possui boa fundação no `main`, mas falta execução contra banco/acervo real

`scripts/audit_db_filesystem_links.py` já oferece uma base segura para o lado **banco -> filesystem**:

- abre SQLite em modo `ro`;
- usa `PRAGMA query_only=ON`;
- authorizer bloqueia escrita/DDL/PRAGMA;
- resolve caminhos contra roots permitidas;
- rejeita path traversal;
- rejeita symlink/reparse;
- verifica existência/tipo;
- pode validar tamanho;
- pode validar SHA-256;
- produz findings estruturados.

Isso é patrimônio importante.

### Limite

A ferramenta é dirigida por specs SQL e verifica os registros fornecidos pelo banco contra filesystem.

O problema operacional B49 exige também o sentido:

**filesystem -> banco**

para encontrar arquivos que existem nas conexões/repositório, deveriam estar indexados e permaneceram invisíveis — exatamente o padrão dos casos Eloim, J Bernardes/Odonto Art e outras guias existentes não incorporadas.

Nos deltas, o botão `Arquivar pendentes` atua sobre registros já conhecidos; não é auditoria de órfãos físicos.

Além disso, a ferramenta do `main` ainda não foi executada sobre:

- `axiom_tools.db` canônico;
- raízes reais das conexões;
- repositório processado;
- amostra dos casos reais.

### Estado

B49 permanece **BLOQUEADO_POR_RUNTIME / infraestrutura parcial pronta**.

A auditoria final deve prover os dois sentidos e gerar ocorrência técnica para itens físicos não indexados.

## 11. B50 — a Etapa 47 já confirmou a causa arquitetural; esta etapa não cria diagnóstico concorrente

B50 declara que:

- SHA-256 identifica bytes;
- fingerprint lógico identifica documento/fato;
- identidade econômica decide se componentes devem somar, substituir ou serem equivalentes.

A Etapa 47 comprovou que o V8F2 deduplica fisicamente por combinação estreita de:

```text
origem_id + caminho_origem + sha256
```

sem camada recuperada de fingerprint documental/econômico.

Também confirmou que Conferência e retificação escolhem o “último documento do tipo”, agravando a confusão entre:

- reemissão;
- sucessor;
- matrícula distinta;
- componente aditivo.

### Estado

B50 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**, alinhado a B12/B13/B14/B17.

## 12. Visão consolidada B41–B50

| ID | Resultado desta etapa |
|---|---|
| B41 | backup parcial de código confirmado; rollback de banco/config e falha pós-startup ausentes |
| B42 | SHA256SUMS existe, mas não é verificado nem ligado a commit/schema/release |
| B43 | correção substancial no V8F2: competência ativa virou default; homologação pendente |
| B44 | A4 portrait implementado e testado estaticamente; impressão real pendente |
| B45 | paginação melhorou; N+1/polling pesado e benchmark continuam pendentes |
| B46 | dupla verdade `COM_PENDENCIAS` x `PROCESSAMENTO_CONCLUIDO` permanece confirmada |
| B47 | regressão visual Sintegra isolada no salto V -> V1 e persistente nos deltas seguintes |
| B48 | contrato/planner existem; ferramenta operacional segura de limpeza não foi recuperada |
| B49 | auditor banco->filesystem existe; filesystem->banco e execução real continuam pendentes |
| B50 | causa já confirmada: hash físico não representa obrigação lógica/econômica |

Nenhum item foi promovido para `CORRIGIDO_HOMOLOGADO`.

## 13. Marco após B01–B50

Com a Etapa 52, os **50 bloqueadores canônicos** possuem agora contrato e diagnóstico/restrição de evidência revisados até os deltas mais recentes disponíveis nesta sessão.

Isso não significa que os 50 estejam corrigidos. Significa que a auditoria já separou, de forma suficientemente detalhada:

- defeito confirmado;
- correção parcial válida a preservar;
- implementação ausente;
- teste pendente;
- dependência do runtime integral;
- dívida de homologação Windows.

Os achados positivos que não devem ser perdidos incluem, entre outros:

- V8A: distinção visual `Aguardando processamento` x `Em conferência`;
- V8F2: FGTS zero com precedência da evidência Domínio;
- V8F2: eConsignado não `CONFERIDO` sem fonte de recolhimento;
- V8F2: competência e-CAC ampliada + `competencia_metodo`;
- V8F2: Pendências por competência ativa e paginação backend;
- V8F2: CSS A4 portrait;
- autenticação e tokens CSRF preservados nos deltas auditados;
- tooling do `main` para invariantes, rollback, proveniência e auditoria de vínculos.

## 14. Próxima etapa canônica

Após completar o diagnóstico B01–B50, o próximo trabalho deve ser:

1. atualizar o rastreador canônico com as Etapas 42–52;
2. reconciliar B06 com a árvore operacional integral quando os bytes do ZIP/runtime puderem ser acessados;
3. preservar os patches válidos identificados;
4. implementar correções na ordem de dependência já definida;
5. executar regressões B01–B50 e C01–C28;
6. somente então tratar build/instalação final.

A V8 permanece **NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO**.
