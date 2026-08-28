# Achado — Origem histórica do bypass de saídas V3 → V8

Data: 28/08/2026
Status: **causa histórica provável fortemente sustentada por evolução documental + defeito atual confirmado no ZIP**

## 1. Achado atual já confirmado

A auditoria do ZIP V8 confirmou:

- Centro de Impressão não revalida canonicamente no backend todo cliente selecionado;
- seleção manual por IDs pode contornar o conjunto fechado/conferido;
- Central de Entregas protege melhor a listagem, mas ações POST individuais/selecionadas também não compartilham um gate único;
- saídas automáticas chegaram a usar `PROCESSADO` como equivalente a validado.

## 2. Contrato V3

Na V5.6.14V3, a UX de saída foi desenhada com exceções operacionais amplas:

### Entregas

- padrão: `Somente fechados` quando havia controle mensal;
- opção excepcional `Todos os eletrônicos` permanecia disponível.

### Impressão

- público padrão: retirada/office-boy;
- opção `Todos os clientes` disponível;
- nos modos por empresa/individual, seleção explícita podia incluir qualquer cliente independentemente do público padrão.

Naquele estágio, essas exceções eram parte do comportamento entregue.

## 3. Contrato V7 posterior

A V7 mudou a semântica do fechamento:

- fechamento tornou-se automático pelo batimento;
- entregas e impressão passam a ser liberadas a partir do estado `FECHADA`;
- retificações continuam versionadas.

A partir daí, `FECHADA` passa a ser condição de autorização, e não apenas filtro padrão de navegação.

## 4. Regressão de transição

A hipótese causal mais consistente com as evidências é:

1. V3 criou caminhos de exceção/seleção ampla;
2. V7 endureceu a regra de autorização para `FECHADA`;
3. telas/listagens foram parcialmente adaptadas;
4. serviços/POSTs de seleção explícita preservaram caminhos antigos;
5. na V8, esses caminhos aparecem como bypass do gate.

Isso explica por que o defeito atual não é simplesmente "faltou filtro": existe dívida de transição entre dois contratos legítimos de épocas diferentes.

## 5. Regra V8 definitiva

A V8 deve separar:

```text
PUBLICO PADRAO DA TELA
!=
UNIVERSO AUTORIZADO PELO BACKEND
```

Filtros como:

- retirada/office-boy;
- eletrônico;
- todos os canais;
- seleção manual;

podem alterar a **forma de escolher dentro do universo autorizado**, mas nunca ampliar autorização para cliente/versão não fechados.

## 6. Exceção operacional futura

Se o produto realmente precisar permitir saída excepcional antes do fechamento, isso não deve reutilizar `Todos os clientes` como bypass silencioso.

Deve existir uma ação administrativa explícita, com:

- permissão própria;
- justificativa obrigatória;
- usuário/data/hora;
- versão/evidências disponíveis;
- aviso claro de que é saída excepcional;
- auditoria;
- sem alterar o estado do fechamento.

Nenhuma exceção desse tipo está autorizada automaticamente por este documento.

## 7. Regressões mínimas

1. filtro `Todos` não inclui cliente não autorizado;
2. IDs manuais são intersectados com o universo autorizado;
3. impressão individual bloqueia não FECHADA;
4. entrega individual bloqueia não FECHADA;
5. lote bloqueia retificação pendente;
6. documento PROCESSADO de cliente aberto não sai;
7. FECHADA sem versão válida não sai;
8. Vn antiga não é usada silenciosamente depois de Vn+1;
9. filtros de canal não alteram autorização;
10. tentativa de bypass fica auditável/negada no backend.

## 8. Severidade

**Alta / regressão de autorização operacional.**

É uma regressão de transição entre contratos e deve ser corrigida no serviço compartilhado, não apenas em templates.

## 9. Relação com bloqueadores

Principalmente B03, B09, B10, B18, B39 e B40.
