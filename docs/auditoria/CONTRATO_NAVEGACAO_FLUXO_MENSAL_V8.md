# Contrato V8 — Navegação e fluxo mensal

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Objetivo

Garantir que a navegação represente a ordem operacional aprovada e que cada tela possua um único papel.

## 2. Evolução documentada

### AXT-003 estrutural

Em 17/08, `Processamento de Arquivos` era o núcleo futuro que absorveria conceitos antes separados de OCR, Competências e Conferência.

### V6

Fechamento Mensal foi introduzido no menu **logo após Processamento de Arquivos**.

### V8

A arquitetura foi posteriormente reformulada: Fechamento, Processamento e Conferência voltaram a possuir papéis próprios e não duplicados.

A competência passa a nascer no Fechamento Mensal. Consequentemente, o fluxo e a navegação devem refletir:

```text
Fechamento Mensal
    -> Processamento de Arquivos
    -> Central de Conferência
    -> Impressão / Entregas
```

Essa mudança é evolução legítima do contrato, não simples preferência visual.

## 3. Fechamento Mensal

Única origem normal da competência operacional.

Deve permitir:

- abrir competência;
- visualizar composição mensal;
- acompanhar chamada atual;
- visualizar evolução/status;
- consultar chamadas futuras e histórico;
- acessar retificações em área própria.

Não deve duplicar a mesa de resolução da Conferência.

Não deve exigir seleção manual de clientes para determinar quem será processado no fluxo normal.

Não deve possuir fluxo normal `Fechar selecionadas`.

## 4. Processamento de Arquivos

Tela técnica e operacional dos motores.

Deve:

- herdar competência/chamada abertas;
- mostrar fila/sessões/etapas técnicas;
- permitir upload/entrada controlada;
- reprocessar falhas técnicas;
- mostrar pendências técnicas;
- preservar histórico técnico em visão própria.

Não deve:

- abrir novamente competência;
- escolher manualmente carteira do fechamento;
- justificar ausência de DARF/FGTS/eConsignado;
- marcar fonte como conferida;
- fechar cliente;
- funcionar como mesa principal de auditoria/conferência.

## 5. Central de Conferência

Mesa operacional de resolução.

Deve receber apenas clientes que realmente alcançaram o estágio de conferência ou retificação no fluxo correspondente.

A ocorrência deve permitir, no mesmo contexto:

- anexar documento;
- reprocessar;
- ver documentos;
- justificar/resolver por fonte;
- registrar ocorrência/evidência;
- marcar sem movimento mensal quando aplicável;
- registrar próxima chamada/impedimento quando pertinente.

A tela é leitura + ações explícitas. Simples abertura/refresh não escreve no fechamento.

## 6. Competência herdada

Processamento, Conferência, Impressão e Entregas não devem pedir novamente ao usuário para "aplicar" a competência corrente no fluxo normal.

O contexto deve ser herdado do Fechamento Mensal.

Competência histórica pode ser consultada sem trocar silenciosamente a competência operacional ativa.

## 7. Navegação

Na navegação operacional do DP, `Fechamento Mensal` deve aparecer antes de `Processamento de Arquivos`.

A posição é funcional: ensina a ordem correta e reduz uso de tela técnica sem contexto mensal.

A ordem atual do `shell.html` do runtime ainda precisa ser verificada diretamente; a evidência recuperada não mostrou a sequência completa. Portanto este item é contrato/teste pendente, não defeito visual confirmado.

## 8. Resíduo terminológico no Processamento

Evidência preservada do runtime mostra o template de Processamento com:

- eyebrow `PROCESSAMENTO DE ARQUIVOS`;
- `<h1>` começando por `Aud...`.

O texto completo não foi recuperado.

Isso é classificado como **resíduo terminológico/funcional a inspecionar**, não como defeito confirmado por inferência.

Na revisão do runtime, deve-se verificar se:

- o título ainda usa `Auditoria`/`Conferência` por herança antiga;
- existem ações de decisão de negócio na tela técnica;
- nomenclatura e ações correspondem ao papel V8.

## 9. Uma ação primária por contexto

### Fechamento

Ação central: abrir/administrar competência e chamada.

### Processamento

Ação central: executar/reprocessar tecnicamente a competência herdada.

### Conferência

Ação central: resolver pendências/divergências por fonte.

Evitar grupos de botões que repetem a mesma decisão em módulos diferentes.

## 10. Regressões mínimas

1. Fechamento aparece antes de Processamento na navegação V8.
2. Processamento sem competência aberta informa contexto ausente e não inventa competência.
3. Processamento não oferece abertura/aplicação paralela da competência.
4. Conference não recebe cliente sem evidência suficiente apenas porque está PRONTA.
5. Fechamento não contém mesa duplicada de resolução documental.
6. Anexar/reprocessar na Conference não exige sair da tela.
7. abrir Conference não grava estado.
8. navegar para histórico não troca competência ativa silenciosamente.
9. Impressão/Entregas herdam competência e passam pelo gate.
10. título/ações do Processamento não apresentam papel de Auditoria/Conferência indevido.

## 11. Relação com bloqueadores

Principalmente B02, B07, B09, B10, B11, B37, B43, B45 e B46.
