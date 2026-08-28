# Integração Assistida Sintegra → Cadastro de Clientes

Status: **proposta aprovada para avaliação na auditoria V8**  
Data: 28/08/2026

## Objetivo

Preservar os atalhos existentes de acesso rápido ao Sintegra Nacional e Sintegra Goiás na ficha do cliente e acrescentar um mecanismo assistido de captura dos dados exibidos na página consultada, sem depender de automação de CAPTCHA e sem remover o controle humano.

## Princípio

O Axiom Tools não deve tentar ler silenciosamente uma aba externa do navegador por meio da aplicação web comum, pois o navegador bloqueia esse acesso por política de mesma origem.

A solução recomendada é um pequeno componente local/browser extension do Axiom Tools, compatível prioritariamente com Firefox e posteriormente Chromium, acionado pelo usuário somente depois que a consulta Sintegra estiver aberta e concluída.

## Fluxo proposto

1. Usuário abre a ficha do cliente.
2. Mantêm-se os atalhos `Sintegra Nacional` e `Sintegra Goiás`.
3. Usuário realiza a consulta normalmente no portal, inclusive qualquer interação humana exigida.
4. Na página de resultado, aciona `Enviar ao Axiom Tools` pelo componente do navegador.
5. O componente lê apenas os campos visíveis/estruturados da página de resultado.
6. Os dados são enviados para um endpoint local autenticado do Axiom Tools, vinculados ao cliente que originou a consulta.
7. Antes de gravar, o Tools mostra comparação `Atual × Sintegra`.
8. Usuário confirma quais alterações deseja aplicar.
9. O sistema registra fonte, data/hora, usuário e diferenças aplicadas.

## Campos candidatos

Conforme disponibilidade real da página consultada:

- inscrição estadual;
- situação cadastral;
- razão social;
- nome fantasia;
- CNPJ/CPF;
- endereço;
- município/UF;
- CNAE/atividade;
- data de situação/baixa, quando exibida;
- outras inscrições estaduais exibidas.

Nenhum campo deve ser sobrescrito silenciosamente.

## Segurança e governança

- não automatizar ou contornar CAPTCHA;
- não coletar credenciais;
- não ler abas sem ação explícita do usuário;
- endpoint local deve usar token temporário/escopo do cliente;
- dados capturados devem ser apresentados em prévia diferencial antes de persistir;
- manter histórico/auditoria de alterações;
- falha de captura nunca deve apagar dados existentes.

## Simplificação de uso

A ficha do cliente deve manter o fluxo simples:

`Sintegra GO` / `Sintegra Nacional` → consulta manual → `Enviar ao Axiom Tools` → revisar diferenças → aplicar.

O objetivo é reduzir digitação sem retirar os atalhos atuais nem transformar o Sintegra em automação opaca.
