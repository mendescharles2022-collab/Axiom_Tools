# Axiom Tools — Origens, Arquitetura, Governança e Evolução

Data: 23/09/2026

## 1. Identidade do produto

**DECISÃO HISTÓRICA APROVADA / CANÔNICO**

O Axiom Tools nasceu para substituir e organizar rotinas dispersas de arquivos, BATs e tarefas manuais do escritório por uma aplicação local, modular, auditável e segura, com forte foco no Departamento Pessoal.

O produto evoluiu para abranger:

- cadastro e indexação de clientes;
- estruturas físicas PF/PJ e funcionários;
- arquivo digital e repositório documental;
- upload e monitoramento de entradas;
- leitura PDF e OCR;
- classificação documental;
- competência;
- processamento por motores especialistas;
- conferência;
- fechamento mensal;
- retificação;
- impressão;
- entregas;
- integrações assistidas;
- parâmetros;
- auditoria e histórico.

O Tools não deveria substituir a folha oficial. O **Domínio permanece a folha oficial**; o Tools interpreta, organiza, cruza, confere, versiona e produz evidência operacional.

## 2. Princípios arquiteturais

**CANÔNICO**

- Regra de negócio separada de interface.
- Filesystem tratado como recurso externo sensível.
- Persistência não autoriza destruição do acervo.
- Módulos pequenos e substituíveis.
- Caminhos críticos centralizados em configuração.
- Testes em ambientes temporários/isolados.
- Operação crítica deve poder ser simulada antes da aplicação.
- Nenhuma exceção de cliente deve virar hardcode quando a regra puder ser genérica.
- Arquivos de código preferencialmente próximos de 300 linhas; evitar ultrapassar 500 sem justificativa.
- Interface consome serviços; UI não replica regra de negócio.
- Evolução funcional deve preservar o que já foi homologado.

## 3. Evolução por Sprints históricas

**CANÔNICO HISTÓRICO**

O roadmap documental inicial foi:

- AXT-000 — fundação documental/arquitetural;
- AXT-001 — estruturas PF/PJ e funcionários;
- AXT-002 — login, shell e dashboard;
- AXT-003 — clientes, importação e configurações;
- AXT-004 — OCR e classificação;
- AXT-005 — competências e roteamento;
- AXT-006 — conferência e visualização PDF;
- AXT-007 — impressão e consolidação;
- AXT-008 — integrações assistidas e operação Windows.

Esse roadmap explica a origem dos módulos, mas o produto operacional posterior evoluiu além dessa divisão.

## 4. Arquitetura operacional amadurecida

**DECISÃO HISTÓRICA APROVADA**

Com o uso real, tornou-se obrigatório separar:

### Fechamento Mensal
Abre a competência, define universo mensal/chamadas e acompanha o ciclo.

### Processamento de Arquivos
Recebe, identifica, classifica, extrai, arquiva e reprocessa evidências técnicas.

### Central de Conferência
Resolve divergências, ausências, justificativas, anexos, reprocessamento e decisão por fonte.

### Saídas
Somente recebem material autorizado pelo estado canônico do fechamento/conferência.

Abertura de uma tela de consulta não pode alterar estado. Leitura/GET deve ser pura.

## 5. Arquitetura dos motores

**DECISÃO HISTÓRICA APROVADA**

Ordem operacional de referência:

    Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento incremental final

Motores especialistas principais:

- Domínio;
- eSocial;
- e-CAC/DARF;
- FGTS Digital.

Especialistas internos reutilizáveis:

- Identidade;
- Competência;
- Valores;
- Pessoas;
- Dados Operacionais;
- eConsignado;
- Validação/Cruzamento.

O objetivo dessa arquitetura é impedir que cada parser reinvente regras de identificação, competência ou valores.

## 6. Escala e processamento

**DECISÃO HISTÓRICA APROVADA**

O desenho deve considerar volumes futuros maiores do que a carteira presente.

Requisitos permanentes:

- processamento em lotes;
- execução incremental;
- idempotência;
- SHA-256/hash;
- cache;
- checkpoints;
- retry controlado;
- paralelismo limitado;
- fila persistente;
- sessão de processamento auditável;
- memória controlada;
- paginação/filtros no backend quando o volume justificar.

O sistema não pode exigir seleção manual de centenas de clientes para o fluxo normal.

## 7. Governança e autoridade

**CANÔNICO / DECISÃO HISTÓRICA**

Documentação não é prova de runtime.

Regra de precedência prática para recuperação histórica:

1. decisão permanente específica;
2. comportamento homologado/confirmado em uso real;
3. correção explicitamente aprovada após falha real;
4. Sprint vigente compatível;
5. arquitetura consolidada;
6. documentação auxiliar;
7. material provisório V8 somente como evidência, nunca como autoridade isolada.

A auditoria V8 formalizou a frase:

**patch encontrado ≠ tooling verde ≠ correção integrada ≠ homologação.**

## 8. Linha de versões relevante

**HOMOLOGADO / IMPLEMENTAÇÃO OBSERVADA**

- V5 e sucessoras consolidaram cadastro, pastas e operação Windows preservando centenas de clientes.
- V5.6.13 introduziu/fortaleceu motores documentais.
- série V5.6.14 acumulou ajustes de Upload, Processamento, motores, fechamento e UX.
- V5.6.14V7 é a referência estável conhecida registrada no repositório.
- V8 introduziu/reformulou competência única, composição mensal, chamadas, conferência e vários contratos, mas ficou em auditoria.
- **V8 nunca foi homologada** e não deve apagar regras confirmadas das versões anteriores.

## 9. Auditoria V8

**PROVISÓRIO V8 / PATRIMÔNIO DE REGRESSÃO**

A V8 produziu patrimônio técnico valioso:

- B01–B50;
- 28 casos de regressão de agosto/2026;
- contratos de estados, composição, fonte, segurança, banco, UI e outputs;
- Etapas de auditoria chegando a 84;
- tooling de reconciliação runtime↔GitHub;
- gates de release;
- ferramentas de staging e verificação.

Esse patrimônio serve para detectar falhas e preservar aprendizados, mas não transforma a V8 em baseline homologada.

## 10. Incorporação posterior

**DECISÃO HISTÓRICA POSTERIOR**

Em 04/09/2026 foi decidido que o desenvolvimento futuro do Tools seria distribuído pelos domínios do Axiom Enterprise, sem copiar um módulo monolítico.

Esse handoff não revoga o valor histórico do repositório Axiom_Tools. Ao contrário: o repositório deve continuar preservado como fonte de regras, regressões e evidências enquanto existir qualquer migração incompleta.

A migração para outro produto deve ser por patrimônio funcional, não por cópia cega do runtime.
