# Integração Sintegra / SEFAZ GO → Cadastro de Clientes

Status: **proposta aprovada para avaliação na auditoria V8**  
Data inicial: 28/08/2026  
Atualização: 28/08/2026 — estratégia GO revisada após validação da consulta pública oficial

## 1. Objetivo

Preservar os atalhos existentes de acesso rápido ao Sintegra Nacional e Sintegra Goiás na ficha do cliente e reduzir redigitação cadastral mediante consulta/captura controlada, sempre com comparação antes de gravar alterações.

## 2. Decisão revisada para Goiás

A consulta pública oficial da Secretaria da Economia de Goiás disponibiliza pesquisa de contribuintes goianos por CCE, CNPJ ou CPF.

Na página pública validada em 28/08/2026 não é apresentado CAPTCHA no formulário de consulta.

Consequentemente, para Goiás a ordem preferencial passa a ser:

1. **consulta direta assistida pelo próprio Axiom Tools**, usando a consulta pública quando tecnicamente aceita;
2. leitura estruturada do resultado;
3. comparação `Cadastro atual × SEFAZ GO`;
4. confirmação humana do que será atualizado;
5. captura pelo navegador/WebExtension somente como fallback se a consulta direta for bloqueada, mudar de comportamento ou exigir contexto de navegador.

Não assumir que existe API oficial estável sem documentação específica. A integração direta deve ser isolada em adaptador próprio para que mudança do portal não contamine o Cadastro de Clientes.

## 3. Sintegra Nacional / outras UFs

O atalho `Sintegra Nacional` permanece.

Como cada UF pode possuir mecanismos diferentes, inclusive autenticação ou desafios de interação, a estratégia nacional continua assistida e adaptável por fonte.

Nenhuma regra específica de Goiás deve ser generalizada automaticamente para outras UFs.

## 4. Fluxo preferencial — Goiás

1. Usuário abre a ficha do cliente.
2. A ficha mantém `Sintegra Goiás` e `Sintegra Nacional`.
3. Ao acionar `Consultar SEFAZ GO`, o Tools utiliza CNPJ, CPF ou IE disponível.
4. O adaptador consulta a fonte pública oficial.
5. O resultado é normalizado sem gravar nada automaticamente.
6. O Tools apresenta comparação por campo:

   `Cadastro atual | SEFAZ GO | Ação`

7. Usuário escolhe quais diferenças aplicar.
8. O sistema grava fonte, data/hora, usuário, valor anterior e valor novo.
9. Falha de consulta nunca apaga ou substitui dado existente.

## 5. Fallback de navegador

Se a consulta direta não estiver tecnicamente disponível:

1. abrir o portal oficial;
2. usuário realiza a consulta;
3. componente/WebExtension lê somente a página de resultado após ação explícita;
4. envia os dados ao endpoint local autenticado do Tools;
5. segue a mesma comparação antes de persistir.

O fallback deve priorizar Firefox no ambiente atual e manter compatibilidade futura com Chromium quando necessário.

## 6. Campos candidatos

Conforme disponibilidade real da página consultada:

- inscrição estadual;
- situação cadastral;
- razão social/nome empresarial;
- nome fantasia;
- CNPJ/CPF;
- endereço;
- município/UF;
- CEP;
- CNAE/atividade principal e secundárias;
- regime de apuração, quando exibido;
- data da situação cadastral;
- data de cadastramento;
- outras inscrições exibidas;
- informações complementares relevantes disponibilizadas pela fonte.

## 7. Hierarquia e conflito de dados

A consulta não deve sobrescrever silenciosamente o cadastro.

Regras:

- documento principal incompatível com o cliente aberto = bloquear aplicação automática e exigir revisão;
- razão social/nome, endereço, CNAE e situação podem ser comparados diferencialmente;
- informação ausente na fonte não apaga valor existente;
- mudança de situação cadastral deve gerar ocorrência/histórico;
- dados vindos da RFB e da SEFAZ GO mantêm suas fontes distintas; uma fonte não deve fingir ser a outra.

## 8. Segurança e governança

- não contornar CAPTCHA quando alguma fonte o utilizar;
- não coletar credenciais desnecessárias;
- não automatizar autenticação protegida clandestinamente;
- não ler abas sem ação explícita no fallback;
- endpoint local do fallback deve usar token temporário/escopo do cliente;
- toda alteração precisa de prévia diferencial;
- manter histórico/auditoria;
- falha de captura/consulta nunca apaga dados existentes;
- adaptar a integração a mudanças do portal sem espalhar seletores/regras pelo módulo de Clientes.

## 9. Resiliência

O adaptador GO deve distinguir:

- consulta realizada com sucesso;
- contribuinte não localizado;
- indisponibilidade do portal;
- resposta alterada/incompatível;
- bloqueio de acesso automatizado;
- erro técnico local.

Bloqueio ou mudança do portal aciona fallback assistido; não deve ser interpretado como contribuinte inexistente.

## 10. Critérios de regressão

1. atalhos `Sintegra Goiás` e `Sintegra Nacional` aparecem na ficha;
2. `Consultar SEFAZ GO` não sobrescreve dados sem confirmação;
3. documento incompatível bloqueia atualização;
4. campo ausente na fonte não apaga cadastro;
5. histórico registra cada alteração aplicada;
6. indisponibilidade da fonte preserva cadastro;
7. consulta direta e fallback produzem o mesmo modelo normalizado de comparação;
8. mudança de HTML/portal fica confinada ao adaptador;
9. fluxo GO não depende de CAPTCHA inexistente na consulta pública atual;
10. regras de Goiás não são aplicadas automaticamente a outras UFs.

## 11. Fontes oficiais verificadas na auditoria

A Secretaria da Economia de Goiás mantém página oficial do Sintegra com link para `Contribuintes goianos` e página do CCE com consultas públicas. A página de consulta pública atualmente aceita CCE/CNPJ/CPF.

A implementação deve continuar tratando o portal como serviço externo sujeito a mudança, mesmo quando a consulta atual for pública e sem CAPTCHA visível.
