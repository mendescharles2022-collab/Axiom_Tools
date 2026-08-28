# Auditoria canônica V8 — Etapa 15

Data: 28/08/2026
Status: **auditoria em andamento / sem pacote final**

## 1. Escopo

Esta etapa avançou da arquitetura abstrata para evidência da instalação real preservada em logs PowerShell.

## 2. Achado confirmado — regra de universo replicada

Foram identificadas consultas diretas a `fechamento_mensal_cliente` fora do domínio de Fechamento, inclusive em:

- `modules/processing/central.py`;
- `modules/processing/operations...`;
- `web/views/documents_views.py`.

Isso confirma duplicação da decisão de pertencimento ao ciclo/escopo entre camadas.

## 3. Consequência

Uma regra de chamada/status pode ser corrigida em uma tela e continuar antiga em outra.

O achado é consistente com problemas já observados:

- cliente de 2ª chamada cobrado na 1ª;
- fechados reaparecendo na Conferência;
- eConsignado consultando universo excessivo;
- gates distintos entre Impressão/Entregas;
- telas documentais mantendo filtros próprios.

## 4. Contrato criado

Foi criado `CONTRATO_UNIVERSO_OPERACIONAL_V8.md` definindo cinco universos semânticos:

1. composição da competência;
2. liberados da chamada atual;
3. em conferência;
4. em retificação;
5. autorizados de saída.

Os módulos consumidores devem usar fachada canônica do domínio Closing, sem reproduzir SQL de autorização/composição.

## 5. T L Empreendimentos Agrícolas

O log preservado mostra ao menos dois pontos de mutação de status/chamada em `closing/service.py`, incluindo um `UPDATE ... status='PRONTA', chamada=?` próximo da mudança global de `chamada_atual`.

A saída não preservou nome de função/condição integral, portanto a causa exata da regressão de T L ainda não é declarada.

Foi definida regressão sequencial para provar:

- adiamento 1 -> 2;
- persistência;
- ausência em todos os módulos da chamada 1;
- avanço global para chamada 2;
- liberação somente nesse evento;
- histórico completo.

## 6. Evidência histórica de segurança de atualização

Relatórios V6 e V7 confirmam que versões anteriores já possuíam:

- backup de banco e arquivos alterados;
- rollback integral;
- migração/validação em cópia do SQLite;
- nenhuma API externa ou reprocessamento documental durante instalação.

Logo, o contrato de instalação V8 preserva garantia já existente do produto.

## 7. Estado

A V8 continua NÃO HOMOLOGADA.

Próximos alvos: resiliência das integrações externas e contrato de competência/proveniência temporal.
