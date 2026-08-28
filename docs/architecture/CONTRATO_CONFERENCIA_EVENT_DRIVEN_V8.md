# Contrato V8 — Central de Conferência somente leitura e recálculo por evento

Data: 28/08/2026
Status: **contrato obrigatório de correção / V8 não homologada**

## 1. Evidência do defeito atual

A auditoria do ZIP canônico confirmou que a montagem da Central de Conferência chama sincronização de resultados do fechamento durante a própria consulta.

Consequência: abrir ou atualizar uma tela pode alterar `fechamento_mensal_cliente`, criar versão/histórico e encerrar cliente sem existir um evento operacional novo.

Isso viola a separação V8 entre leitura e mutação.

## 2. Regra canônica

Toda operação de leitura da Conferência deve ser pura.

Abrir, atualizar, paginar, filtrar, buscar, trocar aba ou consultar detalhes não pode:

- alterar status mensal;
- criar fechamento;
- criar snapshot;
- criar retificação;
- promover candidato;
- alterar decisão por fonte;
- gerar saída;
- gravar histórico de negócio como se uma decisão tivesse ocorrido.

## 3. Eventos autorizados a provocar recálculo

O agregador da Conferência pode ser executado após evento persistido, como:

- documento novo processado e promovido;
- candidato de reprocessamento promovido;
- documento anexado por ocorrência e processado;
- decisão/justificativa por fonte;
- alteração explícita de movimento mensal;
- mudança persistida de chamada;
- conclusão de retificação;
- correção cadastral que altere comprovadamente a aplicabilidade da competência.

O recálculo deve receber explicitamente `competencia + cliente_id + causa + correlation_id`.

## 4. Idempotência

Reexecutar o mesmo evento não pode:

- criar fechamento duplicado;
- criar múltiplas versões iguais;
- duplicar histórico;
- repetir saída;
- alterar `updated_at` de negócio sem mudança material.

O resultado do agregador precisa ser determinístico para o mesmo conjunto de evidências e decisões.

## 5. Fechamento automático

`FECHADA` só pode resultar do agregador canônico quando todas as obrigações aplicáveis estiverem em estado terminal aceitável e não houver retificação material pendente.

Consulta de tela jamais é causa de fechamento.

## 6. Regressão mínima

Antes de homologar:

1. copiar banco real de teste;
2. registrar hash/contagens relevantes de fechamento, versões, retificações, decisões e histórico;
3. abrir a Conferência 10 vezes, paginar, filtrar, buscar e abrir detalhes;
4. comparar o banco antes/depois;
5. nenhuma tabela de negócio pode ter sido alterada;
6. em seguida executar um evento real de decisão/documento;
7. provar que apenas o cliente/competência afetado foi recalculado;
8. repetir o mesmo evento e provar idempotência.

## 7. Concorrência

Recálculo deve utilizar revisão/versão esperada do estado mensal. Job ou request iniciado sobre estado antigo não pode sobrescrever uma decisão posterior.

## 8. Resultado esperado

A Central de Conferência passa a ser uma projeção confiável do estado já persistido e uma mesa para executar ações explícitas. Ela deixa de possuir efeito colateral invisível por simples navegação.
