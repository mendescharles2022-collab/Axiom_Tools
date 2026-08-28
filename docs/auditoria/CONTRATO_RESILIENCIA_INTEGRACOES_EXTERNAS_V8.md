# Contrato V8 — Resiliência das integrações externas

Data: 28/08/2026
Status: **contrato de auditoria / implementação integral pendente**

## 1. Escopo

Aplica-se a fontes e integrações externas utilizadas pelo Axiom Tools, incluindo:

- eConsignado MTE/Dataprev;
- e-CAC/RFB;
- eSocial;
- FGTS Digital;
- RFB cadastral;
- SEFAZ GO/Sintegra;
- futuros provedores oficiais.

## 2. Princípio central

Falha externa não pode apagar dado interno válido nem ser confundida com resultado de negócio.

É obrigatório distinguir:

```text
resultado válido da fonte
resultado vazio válido
impedimento/autorização ausente
indisponibilidade temporária
falha técnica de integração
resposta incompatível/inconsistente
```

## 3. Estados de consulta não são estados de Conferência

Exemplo eConsignado:

- `COM_CONSIGNADO`;
- `SEM_CONSIGNADO`;
- `SEM_PROCURACAO`;
- `ERRO_TECNICO`.

Esses estados descrevem a consulta externa.

Somente após cruzamento com vínculo, folha, afastamento, rescisão, pagamento direto, garantias e documentos nasce o estado da obrigação na Conferência:

- `CONFERIDA`;
- `DIVERGENTE`;
- `JUSTIFICADA`;
- `IMPEDIDA_EXTERNAMENTE`;
- etc.

## 4. Preservação da última fotografia válida

Quando uma consulta nova falhar:

- não apagar resultado anterior válido;
- registrar tentativa nova separadamente;
- manter data/hora/fonte da fotografia anterior;
- exibir que a informação pode estar desatualizada;
- impedir que o erro técnico transforme automaticamente a obrigação em conferida ou ausente.

## 5. Timeout, retry e backoff

Integrações de rede devem possuir:

- timeout explícito;
- número limitado de tentativas;
- backoff quando apropriado;
- tratamento de erro por classe;
- log da tentativa sem segredo;
- cancelamento seguro.

Retry não deve duplicar efeitos de escrita externa ou interna.

## 6. Idempotência

Reexecutar a mesma consulta para a mesma competência/entidade deve produzir resultado reprodutível quando a fonte não mudou.

Evitar:

- duplicar contratos eConsignado;
- criar várias ocorrências idênticas;
- multiplicar inscrições externas;
- gerar retificação por fotografia idêntica;
- duplicar documento baixado/reprocessado.

## 7. Cache

Cache externo precisa registrar:

- chave de consulta;
- fonte;
- data/hora;
- validade/TTL quando aplicável;
- hash/fingerprint da resposta normalizada;
- origem `CACHE` ou `REDE`.

Cache nunca pode ser apresentado como informação recém-consultada sem indicar sua idade.

## 8. Universo da consulta

Toda integração mensal deve receber seu universo do Fechamento Mensal.

Exemplo já comprovado de defeito: job eConsignado 08/2026 consultou 840 empregadores enquanto a composição mensal auditada tinha 339 participantes do ciclo.

A regra correta é consultar somente o universo elegível daquela competência/chamada.

## 9. Impedimentos externos

Casos como:

- procuração expirada;
- procuração revogada;
- ausência de autorização;
- portal indisponível;
- certificado indisponível;

precisam ser classificados corretamente.

Procuração expirada/revogada pode justificar especificamente a fonte DARF/e-CAC, mas não deve resolver automaticamente FGTS, eConsignado ou outras obrigações.

## 10. Fontes cadastrais RFB/SEFAZ

Dados externos de cadastro entram em modo diferencial:

`Atual interno x Fonte externa x Ação`

Nunca sobrescrever silenciosamente:

- situação interna;
- nome operacional;
- endereço validado manualmente;
- inscrição existente;
- vínculo matriz/filial;
- dados que a fonte não retornou.

## 11. Segurança

Não registrar em logs:

- senha;
- token completo;
- cookie de sessão;
- certificado privado;
- chave privada;
- credencial gov.br.

Logs devem registrar apenas identificadores seguros suficientes para diagnóstico.

## 12. Observabilidade mínima

Cada integração deve expor:

- última execução;
- duração;
- quantidade consultada;
- sucesso/vazio/impedimento/erro;
- taxa de erro;
- fonte/provedor;
- última fotografia válida;
- mensagens de indisponibilidade resumidas.

## 13. Regressões obrigatórias

1. falha de rede não apaga resultado válido anterior;
2. `SEM_CONSIGNADO` é resultado válido, não erro;
3. `SEM_PROCURACAO` é impedimento informativo, não sucesso de Conferência;
4. retry não duplica contratos;
5. cache antigo é identificado como cache;
6. eConsignado não consulta cliente fora da chamada;
7. RFB/SEFAZ não sobrescrevem situação interna;
8. resposta parcial externa não zera campo interno ausente na resposta;
9. portal indisponível gera pendência técnica, não divergência contábil;
10. nova fotografia idêntica não cria retificação.

## 14. Critério de aceite

Nenhuma integração externa pode ser homologada apenas porque 'respondeu' uma vez. Deve provar comportamento seguro também em timeout, resposta vazia, erro parcial, indisponibilidade e repetição idêntica.
