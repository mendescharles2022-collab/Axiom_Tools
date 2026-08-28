# Auditoria canônica V8 — Etapa 7

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo desta etapa

A Etapa 7 aprofundou quatro áreas:

- enriquecimento cadastral RFB/SEFAZ GO/Sintegra;
- rastreabilidade e homologação da V8;
- classificação de regressões reintroduzidas;
- transições de status/chamada no Fechamento Mensal.

Também foram recuperadas referências da árvore operacional real do servidor em textos de diagnóstico de 26/08/2026.

## 2. Cadastro — fonte externa não controla situação interna

A AXT-003 v1.1 já estabelecia separação entre:

- situação interna do cliente;
- situação cadastral RFB.

A mesma regra passa a valer explicitamente para situação estadual/IE.

Assim, RFB `Baixada` ou SEFAZ `Suspensa/Baixada` gera informação/divergência para revisão, mas não inativa automaticamente o cliente do Axiom Tools.

## 3. IE — validação local não é confirmação cadastral

A carga inicial e o adendo da AXT-003 distinguem:

- DV/formato local;
- conferência externa no Sintegra.

A carga inicial oficial preparada possui:

- 981 linhas;
- 887 CNPJs válidos detectados;
- 25 CPFs válidos;
- 69 candidatos a CAEPF;
- 274 registros com IE informada;
- 241 IEs com DV local conferindo;
- 29 IEs com DV local divergente;
- 4 placeholders `10.000.000-0`;
- 6 raízes CNPJ com matriz/filial distintas;
- 27 possíveis perfis de teste Domínio.

Regra preservada: IE divergente é mantida na staging, marcada para conferência e somente depois pode ser mantida/corrigida/removida. Não recalcular DV e sobrescrever silenciosamente.

## 4. Sintegra/SEFAZ GO — arquitetura revisada

A consulta pública oficial de Goiás foi validada em 28/08/2026 com entrada por CCE/CNPJ/CPF e sem CAPTCHA visível no formulário atual.

A arquitetura foi atualizada:

- consulta direta pelo adaptador GO = primeira tentativa;
- comparação diferencial antes de aplicar;
- navegador/WebExtension = fallback;
- nenhuma regra GO generalizada automaticamente a outras UFs;
- falha de portal não significa contribuinte inexistente.

## 5. Garantias V4/V7 perdidas na V8

Foram identificadas regressões reintroduzidas, e não apenas recursos novos faltantes.

### Retificação/versionamento

V4 já possuía candidata `Vn -> Vn+1`, versão anterior preservada e bloqueio de saída durante retificação.

O reprocessamento documental V8, porém, ainda pode apagar a versão vigente antes de validar a nova leitura.

Classificação: `REGRESSAO REINTRODUZIDA — CRITICA`.

### Próxima chamada

V7 já validava empresas adiadas fora do ciclo corrente.

T L Empreendimentos Agrícolas aparece no snapshot 08/2026 como `PRONTA`, chamada 1, apesar da decisão de 2ª chamada.

Classificação: `REGRESSAO REINTRODUZIDA — ALTA`.

### Movimento mensal

V6/V7 já separavam sem movimento mensal do cadastro permanente.

A Conferência V8 ainda permite que o cadastro histórico interfira sobre uma composição mensal explicitamente `COM_MOVIMENTO`.

Classificação: `REGRESSAO REINTRODUZIDA — ALTA`.

### Saídas

V4/V7 e contratos AXT anteriores já protegiam saídas por fechamento/conferência.

A V8 possui caminhos de backend que não aplicam o mesmo gate.

Classificação: `REGRESSAO DE ENFORCEMENT — CRITICA`.

## 6. Árvore operacional real confirma fundação de fechamento/retificação

Trechos recuperados da instalação em `E:\Programas\Axiom_Tools\app\src\axiom_tools` confirmam existência de:

- `modules/closing/service.py`;
- `modules/closing/retification.py`;
- `modules/processing/central.py`;
- tabelas/históricos de fechamento;
- versões e retificações;
- updates de status/chamada;
- leitura do fechamento pelo Processamento.

`closing/service.py` possui mutações de status/chamada em mais de um ponto e atualização da `chamada_atual`.

`closing/retification.py` registra `RETIFICACAO_DETECTADA`, atualiza cliente para `RETIFICACAO` e mantém tabelas de versão.

Isso reforça que a correção V8 deve reutilizar a fundação existente em vez de criar mecanismo paralelo.

## 7. T L Empreendimentos — causa ainda não isolada

A evidência atual prova o estado final incorreto, mas não permite atribuir com segurança a reversão a uma função específica.

Possibilidades ainda abertas:

- comando de adiamento não persistiu;
- rotina posterior sobrescreveu;
- avanço de chamada/recomposição usou predicado amplo;
- migração/backfill alterou o estado;
- escrita concorrente usou snapshot obsoleto.

A auditoria, portanto, não registra causa inventada.

Foi criado contrato de transições com:

- invariantes;
- compare-and-set;
- verificação de linhas afetadas;
- histórico obrigatório;
- teste de colisão concorrente;
- regressão completa da T L antes/depois de refresh, processamento, eConsignado e reinício.

## 8. Processamento consulta o Fechamento

A árvore real mostra `processing/central.py` consultando `fechamento_mensal_cliente` por competência/cliente e conjunto de status, além de outras consultas semelhantes na camada `operations`.

O texto recuperado não expõe por completo o conjunto `status IN (...)`, portanto ainda não é possível cravar quais estados são aceitos nesse ponto.

Classificação: `PONTO DE AUDITORIA DE CODIGO A CONFRONTAR`.

Teste obrigatório:

- chamada futura não entra no processamento corrente;
- `FECHADA` não entra em processamento normal, salvo evidência nova tratada como candidata/retificação;
- `RETIFICACAO` usa fluxo próprio;
- cliente fora da composição mensal não entra apenas por estar ativo no cadastro.

## 9. Homologação da V8

Foi criado contrato específico de homologação.

A V8 deve manter no mínimo a disciplina já comprovada na Auditoria V4:

- suíte automatizada;
- compileall;
- templates/JS;
- banco vazio;
- migração em cópia da base real;
- integrity_check;
- smoke no `venv` real do Windows;
- instalador/backup/rollback.

E acrescentar:

- matriz dos 28 casos reais;
- reprocessamento candidato/versionado;
- gates de saída;
- eConsignado Etapa 0;
- transições de chamada;
- retificação;
- identidade multi-inscrição;
- Sintegra/IE;
- inativação/reativação.

## 10. Documentos produzidos nesta etapa

- `CONTRATO_ENRIQUECIMENTO_CADASTRAL_FONTES_V8.md`;
- `CONTRATO_HOMOLOGACAO_REGRESSAO_V8.md`;
- `MAPA_REGRESSOES_REINTRODUZIDAS_V8.md`;
- `CONTRATO_TRANSICOES_FECHAMENTO_CHAMADAS_V8.md`;
- atualização de `INTEGRACAO_ASSISTIDA_SINTEGRA_CLIENTES.md`;
- este documento.

## 11. Estado ao final da Etapa 7

Continuam críticos e não homologados:

1. reprocessamento destrutivo;
2. recuperação segura Jair 449/450;
3. classificação duplicidade/reemissão vs unidade aditiva;
4. composição multi-GFD;
5. decisão por fonte;
6. Conference read-only;
7. gate único de saídas;
8. eConsignado Etapa 0 e universo mensal;
9. correção da inativação string/Enum;
10. transição de chamada da T L;
11. regressão dos 28 casos;
12. Sintegra visual + consulta GO homologada;
13. reconciliação do `main` com a árvore operacional do ZIP;
14. regressão final no Windows/instalador.

Nenhum pacote V8 deve ser liberado antes dessas verificações.
