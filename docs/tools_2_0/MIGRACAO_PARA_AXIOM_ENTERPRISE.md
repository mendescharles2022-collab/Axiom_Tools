# Migração do Axiom Tools para o Axiom Enterprise

Data: 04/09/2026  
Status: **handoff arquitetural aprovado / migração física ainda não executada**

## 1. Decisão

O desenvolvimento futuro do Axiom Tools será incorporado ao Axiom Enterprise.

O Axiom Tools 2.0 não será uma nova aplicação independente e não será um módulo monolítico copiado para o Enterprise.

O programa será executado no repositório:

`mendescharles2022-collab/Axiom_Enterprise`

## 2. Autoridade no Enterprise

Decisão principal:

`docs/decisions/AXM-029_INCORPORACAO_AXIOM_TOOLS_2_0_AO_ENTERPRISE.md`

Sprint mestra planejada:

`docs/sprints/ENT-006_INCORPORACAO_AXIOM_TOOLS_2_0_OPERACAO_DP.md`

Roadmap:

`docs/roadmap/PROGRAMA_AXIOM_TOOLS_2_0_INCORPORACAO_ENTERPRISE.md`

Requisitos A–Z:

`docs/roadmap/AXIOM_TOOLS_2_0_REQUISITOS_A_Z.md`

Matriz de homologação:

`docs/homologacao/ENT-006_MATRIZ_RASTREABILIDADE_HOMOLOGACAO_TOOLS_2_0.md`

Retrospectiva:

`docs/auditoria/RETROSPECTIVA_AXIOM_TOOLS_V7_V8_PARA_ENTERPRISE_20260904.md`

## 3. Destinos funcionais

| Patrimônio do Tools | Destino no Enterprise |
|---|---|
| cadastro/contexto de cliente | Cadastro |
| inscrições e fontes | Cadastro + Integrações |
| competência/chamadas/sem movimento | Fechamento de Folha |
| upload/monitor/fila/processamento | Guias e Documentos |
| motores Domínio/eSocial/eCAC/FGTS | Guias e Documentos |
| Central de Conferência | Guias e Documentos + Fechamento |
| eConsignado | Consignados |
| procurações/portais | Certificados e Acessos + Integrações |
| Sintegra | Cadastro + Integrações |
| retificação documental | Guias e Documentos + Fechamento |
| impressão/entregas | Guias e Documentos |
| regras previdenciárias/rurais/IRRF | Referencial Técnico, consumido pelos motores |
| login/usuários/perfis | Core Enterprise |
| auditoria/configurações/backups | Core Enterprise |

## 4. O que não deve ser feito

- não copiar a pasta do runtime legado inteira para o Enterprise;
- não migrar banco diretamente;
- não apagar ou mover documentos reais durante desenvolvimento;
- não criar novo login/cadastro paralelo;
- não continuar criando arquitetura nova no repositório Tools;
- não arquivar este repositório antes da homologação do Enterprise;
- não considerar a V8 homologada;
- não usar tooling corrigido como prova de runtime corrigido.

## 5. Primeiro passo da execução real

A primeira execução da ENT-006 deverá ser somente leitura e inventário:

1. identificar o runtime real instalado;
2. reconciliar runtime ↔ GitHub;
3. inventariar schema SQLite;
4. inventariar configurações, parsers, workers, templates e scripts;
5. inventariar volumes e estrutura documental sem enviar dados sensíveis ao Git;
6. classificar cada artefato como incorporar, compartilhar, referenciar, reescrever, arquivar ou descartar;
7. gerar manifesto de handoff.

Somente depois começa implementação/migração.

## 6. Preservação do legado

Enquanto o destino não estiver homologado:

- V5.6.14V7 continua sendo a referência estável conhecida;
- V8 continua como linha não homologada/auditada;
- documentos físicos permanecem no lugar;
- banco legado permanece preservado;
- backups permanecem disponíveis;
- este repositório continua sendo fonte de evidência e regressão.

## 7. Condição para arquivamento

Este repositório só poderá ser arquivado após termo formal confirmando:

- ENT-006 concluída;
- regressões aprovadas;
- migração reconciliada;
- operação Windows homologada;
- rollback comprovado;
- Enterprise independente do runtime Tools;
- cópia histórica segura do último estado do legado.
