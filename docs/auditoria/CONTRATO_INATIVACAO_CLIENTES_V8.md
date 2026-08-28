# Contrato de regressão V8 — Inativação e reativação de clientes

Data: 28/08/2026
Status: **falha funcional confirmada na suíte do ZIP canônico / correção ainda não homologada**

## 1. Falha confirmada

A auditoria da suíte do ZIP canônico confirmou falha funcional na inativação:

`classificacao_inativacao` pode chegar como string, enquanto o repositório assume sempre um Enum e acessa `.value`.

Esse cenário produz erro em fluxo funcional de cadastro e deve ser corrigido antes do pacote final.

## 2. Contrato anterior válido

A AXT-003 já definiu como escopo obrigatório:

- inativação;
- reativação;
- histórico mínimo de alterações;
- exclusão somente cadastral quando necessária;
- preservação do filesystem.

Portanto a correção não pode simplificar o problema removendo classificação, histórico ou reativação.

## 3. Normalização de entrada

A camada de aplicação/repositório deve aceitar entradas semanticamente válidas independentemente de chegarem como:

- instância do Enum interno;
- string com o valor canônico permitido.

A normalização deve ocorrer em um único ponto antes da persistência.

Entrada inválida deve produzir erro de validação claro, e não `AttributeError`/falha por `.value`.

## 4. Dados mínimos da inativação

Quando aplicáveis ao modelo vigente, preservar:

- cliente;
- situação anterior;
- nova situação;
- classificação/motivo da inativação;
- data efetiva;
- observação;
- usuário;
- data/hora da alteração.

Reativação deve gerar novo evento de histórico; não apagar o evento anterior.

## 5. Relação com Fechamento Mensal

Inativar cadastro mestre não pode reescrever competências históricas já abertas/fechadas.

Regras:

- histórico mensal anterior permanece intacto;
- inativação futura impede participação automática em novos ciclos conforme data efetiva;
- se a saída ocorrer no fim de uma competência, aquela competência pode permanecer no ciclo conforme situação operacional real;
- competências posteriores respeitam a inativação;
- reativação futura volta a permitir participação sem alterar retrospectivamente competências anteriores.

Esse contrato é necessário para casos de saída do escritório, como Maria Virginia S Souto.

## 6. Filesystem e documentos

Inativação/reativação é estado cadastral.

Não deve:

- apagar pasta física;
- apagar documentos;
- apagar históricos;
- apagar vínculos de competências anteriores;
- renomear/destruir acervo como efeito colateral não solicitado.

## 7. Regressões obrigatórias

1. inativar recebendo Enum funciona;
2. inativar recebendo string canônica funciona;
3. string inválida gera validação controlada;
4. histórico registra inativação;
5. reativação registra novo evento;
6. pasta física permanece;
7. documentos permanecem;
8. competência histórica permanece inalterada;
9. novo ciclo após data efetiva não inclui cliente inativo automaticamente;
10. reativação não altera retrospectivamente ciclos anteriores.

## 8. Critério de homologação

A falha só pode ser marcada como corrigida após teste funcional do fluxo de inativação e reativação, e não apenas após evitar o `.value` na linha que hoje quebra.
