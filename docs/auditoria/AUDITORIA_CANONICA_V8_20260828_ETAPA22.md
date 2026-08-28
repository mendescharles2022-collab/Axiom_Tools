# Auditoria canônica V8 — Etapa 22

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa auditou:

- navegação e ordem do fluxo mensal;
- evolução histórica Processamento/Conferência;
- pendências técnicas x pendências de negócio;
- resíduos de terminologia/UX;
- origem histórica do bypass de saídas.

## 2. Navegação V6 → V8

V6 documentou `Fechamento Mensal` no menu logo após `Processamento de Arquivos`.

V8 mudou o contrato: a competência é aberta uma única vez no Fechamento e herdada pelos demais módulos.

Portanto a ordem funcional V8 é:

```text
Fechamento Mensal
-> Processamento de Arquivos
-> Central de Conferência
-> Impressão / Entregas
```

Foi criado `CONTRATO_NAVEGACAO_FLUXO_MENSAL_V8.md`.

A ordem efetiva atual do `shell.html` ainda não foi recuperada integralmente; não foi marcada como defeito sem prova.

## 3. Transição AXT-003 → V8

Em 17/08, a AXT-003 estrutural determinou que OCR, Competências e Conferência não fossem mantidos como módulos autônomos antigos; esses conceitos seriam absorvidos pelo futuro Processamento.

Posteriormente V6/V7 criaram Fechamento e a V8 voltou a separar definitivamente:

- Fechamento = competência/composição/status;
- Processamento = execução técnica;
- Conferência = resolução operacional.

Foi criado `MAPA_TRANSICAO_PROCESSAMENTO_CONFERENCIA_AXT003_V8.md` para evitar tratar toda herança antiga como bug e para orientar migração dos testes.

## 4. Resíduo no template do Processamento

Evidência preservada do runtime contém:

```text
PROCESSAMENTO DE ARQUIVOS
<h1>Aud...
```

Mesmo com buscas literais adicionais, o conteúdo completo do título não foi recuperado.

Classificação mantida:

**resíduo terminológico/funcional a inspecionar**.

Não foi promovido artificialmente a defeito funcional confirmado.

## 5. Pendências técnicas x Conferência

Foi criado `CONTRATO_PENDENCIAS_TECNICAS_VS_CONFERENCIA_V8.md`.

Problema confirmado anteriormente no ZIP:

- persistência podia manter sessão como `COM_PENDENCIAS` por itens em revisão;
- camada visual podia apresentar `PROCESSAMENTO_CONCLUIDO` ao atingir 100%;
- duas verdades para a mesma sessão.

Contrato final:

```text
estado técnico da sessão
!=
pendência técnica do arquivo/job
!=
pendência de negócio da Conferência
```

Divergência DARF/FGTS/eConsignado não transforma uma sessão tecnicamente concluída em sessão técnica pendente.

## 6. Pendências do Processamento

A aba técnica deve:

- herdar competência ativa;
- priorizar falhas técnicas;
- deixar PROC/chaves como detalhe avançado;
- separar competência não identificada;
- não funcionar como segunda Central de Conferência.

## 7. Origem histórica do bypass de saídas

Foi registrado `ACHADO_ORIGEM_BYPASS_SAIDAS_V3_V8.md`.

V3 permitia exceções amplas de seleção em Impressão/Entregas, como `Todos os clientes` e seleção explícita fora do público padrão.

V7 posteriormente tornou `FECHADA` a condição de liberação operacional.

O defeito atual confirmado da V8 é compatível com uma transição incompleta: filtros/listagens foram endurecidos, mas serviços/POSTs preservaram caminhos antigos de seleção ampla.

A correção deve ocorrer no gate compartilhado de backend.

## 8. Evidência x contrato

Nesta etapa foram mantidas as classificações:

### Confirmado

- mudança histórica de arquitetura;
- V6 com Fechamento depois de Processamento;
- regra V8 de competência originada no Fechamento;
- status técnico duplicado na auditoria canônica;
- bypass atual de saídas confirmado anteriormente;
- caminhos excepcionais de seleção existiam na V3.

### Inspeção pendente

- ordem atual completa da sidebar;
- texto integral `Aud...`;
- ações atuais completas presentes no template de Processamento.

## 9. Próximo alvo

Auditar a suficiência do snapshot/versionamento para o contrato V8.

A V4 já possuía snapshot, mas a V8 passou a exigir mais dimensões:

- decisão por fonte;
- aplicabilidade;
- identidade/matrícula;
- composição multi-documento;
- proveniência;
- versão que autorizou saída.

É necessário verificar se o modelo de versão consegue congelar essa verdade sem depender do cadastro atual.

## 10. Estado final

V8 permanece NÃO HOMOLOGADA.

Nenhum pacote final autorizado.
