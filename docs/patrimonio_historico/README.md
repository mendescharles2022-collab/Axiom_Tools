# Axiom Tools — Patrimônio Histórico Consolidado

Data de consolidação: 23/09/2026  
Escopo: histórico funcional, operacional, arquitetural e de UX recuperado das conversas do projeto e confrontado com o patrimônio já versionado no repositório.  
Finalidade: impedir perda de regras aprovadas, implementações observadas, aprendizados operacionais e decisões que ficaram dispersas entre chats, versões locais, ZIPs, auditorias e documentação.

## 1. Regra de leitura

Este conjunto NÃO declara que toda regra abaixo esteja implementada na árvore atual da main.

Cada item deve ser lido conforme uma das classificações:

- **CANÔNICO** — regra já registrada como permanente/vinculante no repositório.
- **HOMOLOGADO NO USO** — comportamento confirmado pelo usuário em operação real ou versão estável conhecida.
- **DECISÃO HISTÓRICA APROVADA** — decisão funcional/arquitetural explicitamente aceita em conversa e que deve ser preservada.
- **IMPLEMENTAÇÃO OBSERVADA** — comportamento/código/estrutura visto em runtime, backup, ZIP, log ou tela, sem equivaler automaticamente a homologação.
- **PROVISÓRIO V8** — material produzido na V8 e útil para investigação, mas sem autoridade para substituir comportamento homologado.
- **PENDENTE DE PROVA FÍSICA** — depende de runtime, banco, filesystem ou instalação Windows que não está integralmente no GitHub.
- **SUPERADO** — decisão antiga substituída por decisão posterior mais específica.

Regra central: **V8 não homologada não é baseline funcional.** Em conflito, prevalecem uso real confirmado, decisões expressamente aprovadas e canônicos permanentes.

## 2. Documentos deste patrimônio

1. **01_ORIGENS_ARQUITETURA_GOVERNANCA_E_EVOLUCAO.md**  
   Origem do produto, fronteiras, módulos, evolução, versões, autoridade documental e princípios permanentes.

2. **02_ARQUIVO_DIGITAL_STORAGE_PASTAS_E_GRAFIA.md**  
   Estruturas PF/PJ, funcionários, legado, estrutura.cfg, roots físicos, Storage, watcher/indexação, grafia, normalização e não destruição.

3. **03_CADASTRO_IDENTIDADE_CLIENTES_E_INTEGRACOES.md**  
   Cadastro PF/PJ, perfis, documentos, matriz/filiais, inscrições, RFB, Sintegra/SEFAZ, vínculos e atualização assistida.

4. **04_PROCESSAMENTO_DOCUMENTAL_MOTORES_E_REPROCESSAMENTO.md**  
   Pipeline documental, leitura nativa/OCR, fila/sessões, hash, motores Domínio/eSocial/e-CAC/FGTS, eConsignado, retificações e especialistas internos.

5. **05_FECHAMENTO_CONFERENCIA_REGRAS_DP_E_CASOS_REAIS.md**  
   Competência, chamadas, universo operacional, conferência, fechamento, regras rurais, rescisões, consignado, FGTS e casos reais de agosto/2026.

6. **06_UX_TELAS_IMPRESSAO_ENTREGAS_E_RELATORIOS.md**  
   UX recuperada, Processamento, Conferência, Fechamento, preview, busca, paginação, saídas, impressão, entrega eletrônica e relatórios.

7. **07_INFRAESTRUTURA_SEGURANCA_INSTALACAO_E_HOMOLOGACAO.md**  
   Windows, portas, serviços, SQLite, backup/rollback, segurança, testes, reconciliação runtime↔GitHub e gates de homologação.

8. **08_LACUNAS_CONTRADICOES_E_PLANO_DE_PRESERVACAO.md**  
   O que não está integralmente no Git, divergências entre branches/runtime, artefatos que ainda exigem coleta física e regras de preservação.

9. **09_LINHA_DO_TEMPO_RECUPERADA_DOS_CHATS.md**  
   Linha do tempo das conversas, mudanças de direção, homologações declaradas, reinícios documentais, evolução V5/V8 e reaproveitamento patrimonial.

## 3. Fontes cruzadas

O levantamento cruza, sem tratar uma fonte isolada como suficiente:

- conversas históricas do projeto Axiom Tools;
- reclamações e correções feitas durante uso real;
- decisões homologadas pelo usuário;
- README e STATUS_ATUAL;
- docs/decisions;
- docs/sprints;
- docs/architecture;
- docs/auditoria, inclusive B01–B50 e Etapas 1–84;
- config e scripts de auditoria/reconciliação;
- branch main;
- branch audit-v8-runtime-reconciliation;
- evidências conhecidas de instalação Windows, backups e ZIPs;
- handoff posterior para Enterprise, usado apenas como mapa de destino e não como substituto do patrimônio do Tools.

## 4. Princípios que atravessam todo o produto

- Não apagar automaticamente arquivos originais ou pastas reais.
- Não sobrescrever silenciosamente documento existente.
- Cadastro e filesystem são domínios relacionados, porém distintos.
- Preservar grafia legal/original; normalização serve para busca/matching.
- Leitura textual nativa antes de OCR; OCR somente como fallback.
- Processamento idempotente, incremental, rastreável e preparado para grandes lotes.
- Hash e proveniência devem permitir deduplicação sem destruição.
- Baixa confiança e conflito levam à revisão humana.
- Competência é contexto operacional, não simples atributo do nome do arquivo.
- Processado não significa conferido; 100% técnico não significa fechado.
- Fechamento, Processamento e Conferência possuem responsabilidades distintas.
- Retificação preserva versões anteriores.
- Impressão e entregas dependem de gate operacional válido.
- Portais externos são assistidos; autenticação forte, CAPTCHA e confirmação humana não são contornados.
- Alterações de estrutura física seguem Simular → Revisar → Confirmar → Revalidar → Aplicar.
- O sistema deve ser dimensionado para carteira grande e crescimento, evitando soluções cliente-a-cliente e remendos específicos.

## 5. Situação do repositório no momento desta consolidação

- main: fonte documental/auditável importante, mas não espelho integral do runtime histórico.
- audit-v8-runtime-reconciliation: contém patrimônio próprio e diverge da main.
- referência estável conhecida do legado: V5.6.14V7.
- V8: não homologada.
- runtime físico, banco operacional, documentos, certificados, credenciais, caches e parte dos logs não pertencem ao Git.
- portanto, nenhum futuro projeto deve declarar migração completa usando somente a árvore atual do repositório.

## 6. Regra para reutilização futura

Ao reutilizar patrimônio no Enterprise, Essence ou outro produto:

1. identificar a regra neste índice;
2. conferir o documento temático;
3. conferir a autoridade original no repositório quando existir;
4. distinguir regra de negócio de detalhe de implementação legado;
5. confirmar se existe conflito posterior;
6. implementar no domínio correto, sem copiar o monólito;
7. criar regressão para casos reais já conhecidos;
8. preservar os documentos e o histórico físico antes de qualquer migração.
