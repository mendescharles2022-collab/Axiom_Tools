# Auditoria canônica V8 — Etapa 38

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## Escopo

Revisão do bloqueador B37 — mistura entre estados técnicos e estados de negócio.

## Achados já confirmados

A V8 auditada apresenta situações em que conceitos diferentes usam estados incompatíveis ou são traduzidos como se fossem equivalentes, incluindo:

- sessão técnica com duas interpretações de conclusão;
- documento `PROCESSADO` tratado como autorização de saída;
- estado mensal apresentado como Conferência antes do estágio real;
- resultado de consulta externa tratado como conclusão de obrigação;
- decisão antiga global com alcance maior que a fonte realmente resolvida.

## Regra V8

Devem existir fontes de verdade separadas para:

1. sessão técnica;
2. documento/processamento;
3. obrigação/fonte;
4. ciclo mensal do cliente;
5. consulta externa;
6. retificação;
7. autorização de saída, que é derivada do fechamento vigente.

Rótulos de interface não podem criar uma segunda verdade persistida.

## Transições

Mudanças críticas precisam passar por regra de domínio que valide estado anterior, novo estado, causa, revisão esperada e histórico.

Isso também protege contra escrita baseada em estado antigo.

## Regressões obrigatórias

- sessão concluída pode coexistir com divergência na Conferência;
- documento processado não libera saída se o cliente não estiver fechado;
- retorno positivo do eConsignado não conclui obrigação sem cruzamento;
- decisão de DARF não fecha FGTS pendente;
- cliente em chamada futura permanece fora do ciclo corrente;
- nova evidência em cliente fechado cria retificação quando material;
- abrir Conferência não muda estado.

## Estado

B37 permanece `CONFIRMADO_RUNTIME` e não foi corrigido/homologado nesta etapa.

Próxima frente: B48/B49/B50 — limpeza/retenção, banco ↔ filesystem e hash físico versus identidade econômica.
