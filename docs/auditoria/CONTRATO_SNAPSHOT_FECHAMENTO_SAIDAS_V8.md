# Contrato V8 — Snapshot de fechamento e autorização de saídas

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Problema

Na V8 auditada existem conceitos corretos, porém ainda desconectados:

- cliente mensal `FECHADA`;
- histórico/versionamento do fechamento;
- processamento documental;
- retificação;
- Centro de Impressão;
- Central de Entregas;
- saídas automáticas.

A autorização de saída não pode depender apenas do status textual atual do cliente ou do status `PROCESSADO` do documento.

## 2. Princípio

Todo fechamento concluído deve possuir um **snapshot imutável e identificável** daquilo que foi considerado válido naquele momento.

A autorização de saída deve referenciar esse snapshot/versão.

Modelo conceitual:

```text
competencia + cliente
    -> versao_fechamento Vn
        -> obrigacoes consideradas
        -> documentos/evidencias considerados
        -> decisoes/justificativas por fonte
        -> valores consolidados
        -> data/hora/usuario/evento de conclusao
        -> hash/fingerprint logico do snapshot
```

## 3. Fechamento inicial

Um cliente pode tornar-se `FECHADA` somente quando todas as obrigações aplicáveis da competência estiverem em estado terminal aceitável, como:

- `CONFERIDA`;
- `NAO_APLICAVEL`;
- `JUSTIFICADA`;
- `IMPEDIDA_EXTERNAMENTE`, quando a regra operacional permitir conclusão daquela obrigação.

A conclusão agrega os estados por fonte, mas não apaga o detalhe de cada fonte.

## 4. Versão de fechamento

Ao concluir o cliente:

1. gerar `versao_fechamento` nova;
2. congelar referências das evidências consideradas;
3. congelar valores e estados por fonte;
4. registrar proveniência e usuário/evento;
5. somente então tornar o estado agregado `FECHADA`;
6. liberar o snapshot correspondente ao gate de saída.

## 5. Saídas vinculadas à versão

Toda saída final deve registrar, no mínimo:

- `cliente_id`;
- competência;
- `versao_fechamento_id`;
- tipo de saída;
- documentos incluídos;
- data/hora;
- usuário/processo;
- resultado.

Isso se aplica a:

- impressão individual;
- impressão selecionada;
- lote de impressão;
- entrega individual;
- entrega selecionada;
- entrega em lote;
- saída automática;
- PDF consolidado.

## 6. Nova evidência em cliente fechado

Quando chega nova evidência para cliente/competência `FECHADA`, o sistema deve primeiro comparar a evidência contra a versão vigente.

Possibilidades:

### 6.1 Evidência já conhecida/idêntica

- não cria nova versão;
- fechamento permanece vigente;
- saídas permanecem autorizadas.

### 6.2 Evidência complementar sem impacto material

- preservar Vn;
- registrar a evidência como complementar;
- não criar retificação apenas por existir arquivo novo;
- saídas podem permanecer autorizadas se o gate confirmar ausência de impacto material.

### 6.3 Mudança material

- criar candidato de retificação Vn+1;
- preservar Vn intacta;
- alterar estado agregado para fluxo de `RETIFICACAO`;
- bloquear novas saídas finais até concluir a retificação;
- não apagar saídas históricas já realizadas com Vn;
- permitir rastrear que uma saída antiga foi produzida com versão hoje superada.

## 7. Saída antiga após retificação

Uma saída realizada antes da retificação é fato histórico e não deve ser apagada.

Após Vn+1 ser homologada:

- Vn continua auditável;
- Vn+1 torna-se vigente;
- novas saídas devem referenciar Vn+1;
- sistema deve conseguir indicar quais saídas foram produzidas sob Vn.

## 8. Reprocessamento

Reprocessamento documental comum não tem autorização para alterar diretamente um snapshot fechado.

Fluxo correto:

```text
reprocessamento -> candidato documental -> comparação -> promoção documental
    -> avaliação de impacto no fechamento
        -> sem impacto: Vn permanece
        -> impacto material: candidato de retificação Vn+1
```

## 9. Gate único

O gate de saída deve validar simultaneamente:

- competência correta;
- cliente no universo aplicável;
- estado agregado `FECHADA`;
- versão vigente existente;
- ausência de retificação material pendente;
- documentos solicitados pertencem ou são derivados da versão autorizada;
- seleção manual por IDs pertence ao mesmo universo;
- ação autorizada para o usuário/contexto.

## 10. Proibições

- `PROCESSADO` não autoriza saída;
- `FECHADA` sem `versao_fechamento` não autoriza saída;
- filtro visual não autoriza saída;
- ID manual recebido por POST não autoriza saída;
- snapshot antigo não pode ser usado silenciosamente depois de retificação material;
- nova evidência não pode sobrescrever a versão fechada anterior.

## 11. Regressões mínimas

1. Cliente PRONTA com documento PROCESSADO -> saída bloqueada.
2. Cliente FECHADA V1 -> saída liberada e vinculada a V1.
3. Nova evidência idêntica -> continua V1, sem retificação.
4. Evidência complementar sem impacto -> V1 preservada e justificativa auditável.
5. Mudança material -> RETIFICACAO e novas saídas bloqueadas.
6. Conclusão V2 -> novas saídas usam V2.
7. Saída histórica de V1 continua registrada após V2.
8. POST manual de IDs não consegue incluir cliente sem versão vigente autorizada.
9. Abrir Conference não cria versão nem libera saída.
10. Reprocessamento pior não altera V1 nem dispara retificação falsa.

## 12. Relação com bloqueadores

Este contrato é necessário para liberar principalmente:

- B01;
- B02;
- B03;
- B04;
- B09;
- B10;
- B18;
- B39;
- B40.

## 13. Homologação

Somente será considerado implementado quando o runtime reconciliado provar que:

- fechamento gera snapshot/versão coerente;
- saída referencia essa versão;
- retificação bloqueia saída;
- histórico anterior permanece íntegro;
- nenhuma rota paralela contorna o gate.
