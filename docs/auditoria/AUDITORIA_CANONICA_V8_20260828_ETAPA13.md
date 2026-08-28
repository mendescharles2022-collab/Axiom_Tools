# Auditoria canônica V8 — Etapa 13

Data: 28/08/2026
Status: **auditoria em andamento / pacote final não liberado**

## 1. Escopo

Esta etapa consolidou requisitos de instalação/rollback e proteção das mutações críticas da V8.

## 2. Instalação e rollback

A V7 foi considerada estável após instalação no servidor preservando banco, serviços, histórico e retificações. A documentação também determinou que a V8 não deve ser tratada como concluída sem pacote instalável com rollback.

Isso passa a ser requisito vinculante da homologação V8.

Foi criado `CONTRATO_INSTALACAO_ROLLBACK_V8.md` com:

- inventário pré-instalação;
- backup obrigatório;
- teste de migração em cópia do SQLite;
- `integrity_check`;
- ordem segura de atualização;
- smoke funcional;
- rollback coerente de código + banco + configurações;
- regressões críticas pós-instalação.

## 3. Autenticação e mutações

A AXT-002 já definiu login, sessão, logout e proteção das telas internas como fundação do sistema.

As rotas V8 adicionadas depois devem herdar esse piso.

Foi criado `CONTRATO_AUTENTICACAO_MUTACOES_V8.md` cobrindo:

- autenticação obrigatória;
- proteção CSRF/mecanismo equivalente;
- autorização no backend;
- seleção por IDs sempre intersectada com o universo permitido;
- GET somente leitura;
- jobs com escopo persistido;
- auditoria de usuário/ação/resultado;
- rejeição atômica em falhas de sessão/autorização.

## 4. Relação com achados anteriores

Esses contratos reforçam falhas já confirmadas:

- Conferência não pode escrever durante GET;
- Impressão/Entregas não podem confiar em filtro visual ou IDs recebidos;
- job eConsignado não pode ampliar silenciosamente o universo;
- mudança de chamada precisa de transição válida e auditável;
- aplicação de dados externos não pode gravar automaticamente sem revisão.

## 5. Estado de evidência

A árvore `main` ainda é incompleta em relação ao runtime V8. Portanto, não foi marcado como defeito específico algo que dependa de inspeção direta de decorators/dependências do código operacional.

A classificação correta permanece:

- contratos antigos comprovados;
- defeitos V8 já comprovados pelo ZIP;
- segurança de rotas V8 novas ainda requer verificação na árvore reconciliada.

## 6. Critérios acrescentados à homologação

1. pacote V8 deve ter backup automático e rollback executável;
2. migração SQLite deve ser testada em cópia realista antes do banco operacional;
3. atualização não pode substituir banco/dados permanentes por payload do pacote;
4. todas as mutações V8 devem exigir autenticação e autorização de backend;
5. GET da Conferência precisa permanecer puro;
6. jobs precisam carregar escopo autorizado persistido;
7. smoke de porta/serviço não substitui regressão funcional;
8. a árvore testada deve ser a mesma usada para gerar o instalador.

## 7. Estado final

A V8 continua NÃO HOMOLOGADA.

Próxima etapa: capacidade, desempenho, paginação, memória e execução em lotes para a carteira operacional real.
