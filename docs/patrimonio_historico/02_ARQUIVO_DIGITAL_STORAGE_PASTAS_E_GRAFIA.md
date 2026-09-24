# Axiom Tools — Arquivo Digital, Storage, Pastas e Grafia

Data: 23/09/2026

## 1. Princípio máximo

**CANÔNICO**

Criar somente o que estiver faltando e preservar tudo o que já existir.

Consequências:

- não apagar pasta automaticamente;
- não excluir original;
- não mover legado para “organizar” sem decisão explícita;
- não renomear silenciosamente;
- não mesclar variantes conflitantes;
- não recriar árvore inteira sobre acervo real;
- atualização estrutural é incremental.

Fluxo obrigatório para alteração física:

    Inspecionar → Planejar/Simular → Revisar → Confirmar → Revalidar → Aplicar → Relatar

A simulação deve ser somente leitura.

## 2. Estrutura canônica histórica — PJ

**CANÔNICO (DEC-002 / AXT-001)**

    <Cliente PJ>/
    ├── Arquivos/
    │   ├── Atestados/
    │   ├── Recolhimentos/
    │   │   ├── DARF DCTFWeb/
    │   │   ├── FGTS Digital/
    │   │   ├── DAS - Simples Nacional/
    │   │   └── Outros/
    │   ├── Declarações/
    │   ├── Relatórios/
    │   ├── Notas Fiscais/
    │   └── Arquivos Diversos/
    ├── CNPJ e Inscrição Estadual/
    ├── Contrato Social e Alterações/
    ├── Documentos Diversos/
    ├── Documentos do Responsável/
    └── Funcionários/

## 3. Estrutura canônica histórica — PF

**CANÔNICO (DEC-002 / AXT-001)**

    <Cliente PF>/
    ├── Inscrições - CAEPF, CEI e Estadual/
    ├── Arquivos/
    │   ├── Atestados/
    │   ├── Recolhimentos/
    │   │   ├── DARF DCTFWeb/
    │   │   ├── FGTS Digital/
    │   │   └── Outros/
    │   ├── Declarações/
    │   ├── Relatórios/
    │   ├── Notas Fiscais/
    │   └── Arquivos Diversos/
    ├── Documentos do Responsável/
    ├── Documentos Diversos/
    └── Funcionários/

Diferenças históricas:

- PF não cria DAS - Simples Nacional;
- PF usa Inscrições - CAEPF, CEI e Estadual;
- PF não usa CNPJ e Inscrição Estadual;
- PF não usa Contrato Social e Alterações;
- Notas Fiscais pode existir em PF e PJ.

## 4. Funcionários/Empregados

**CANÔNICO**

Nomes equivalentes reconhecidos:

- Funcionários;
- Funcionarios;
- Empregados.

Se somente uma variante existir, utilizar a existente.  
Se nenhuma existir em estrutura nova, criar Funcionários.  
Se variantes equivalentes coexistirem com conteúdo, registrar conflito e não mesclar.

Estrutura de novo funcionário:

    <Nome Completo>/
    ├── Documentos Pessoais/
    ├── Documentos Gerados/
    ├── Documentos Escaneados/
    └── Rescisão/

Exames é legado:

- não criar em funcionário novo;
- preservar quando existir;
- nunca excluir durante correção estrutural.

## 5. Equivalências legadas

**CANÔNICO**

Exemplos explicitamente registrados:

- CNPJ e Inscrição Estadual ↔ CNPJ e Inscricao Estadual;
- Inscrições - CAEPF, CEI e Estadual ↔ Inscricoes - CAEPF, CEI e Estadual;
- Declarações ↔ Declaracoes;
- Relatórios ↔ Relatorios;
- Funcionários ↔ Funcionarios;
- Rescisão ↔ Rescisao.

No Windows, matching deve considerar comportamento case-insensitive.

Se equivalente legado existir:

- usar o existente;
- não criar variante “bonita” ao lado;
- não renomear;
- não mover conteúdo;
- registrar equivalência.

## 6. estrutura.cfg

**CANÔNICO HISTÓRICO**

Arquivo na raiz do cliente:

PF:
    Tipo=PF
    VersaoEstrutura=1.0

PJ:
    Tipo=PJ
    VersaoEstrutura=1.0

Regras:

- reconhecer arquivo existente;
- preservar chaves desconhecidas;
- não sobrescrever silenciosamente;
- divergência de Tipo é conflito;
- nunca converter PF↔PJ automaticamente.

## 7. Raízes físicas históricas

**IMPLEMENTAÇÃO OBSERVADA / NÃO CANÔNICO UNIVERSAL**

Foram observados caminhos reais como:

- E:\Programas\Axiom_Tools;
- E:\Rotinas Automáticas Dominio\Entrada Axiom\Domínio;
- E:\Rotinas Automáticas Dominio\Entrada Axiom\eCAC;
- E:\Rotinas Automáticas Dominio\Entrada Axiom\FGTS Digital;
- E:\Rotinas Automáticas Dominio\Entrada Axiom\eSocial;
- E:\Rotinas Automáticas Dominio\Repositório Axiom\Processados;
- E:\Rotinas Automáticas Dominio\Saída Axiom\...;
- E:\Contratos, Alterações e Matriculas CAEPF, em uma etapa do acervo/cadastro.

Esses caminhos documentam o runtime histórico. Não devem ser promovidos automaticamente a caminhos fixos de um novo sistema.

## 8. Configuração de caminhos

**DECISÃO HISTÓRICA APROVADA**

Configurações > Caminhos define raízes globais do escritório.

A ficha do cliente não deve obrigar configuração manual completa de caminho por cliente. Ela deve vincular/resolver a pasta correspondente, mantendo vínculo auditável.

Cadastro e filesystem são relacionados, mas independentes:

- excluir/inativar cadastro não exclui a pasta;
- pasta existente não cria automaticamente um cadastro válido sem revisão;
- conciliação precisa detectar órfãos dos dois lados.

## 9. Filiais

**DECISÃO HISTÓRICA APROVADA**

Filiais podem compartilhar a mesma pasta física da matriz.

Nesse caso:

- não criar pasta duplicada;
- manter vínculos cadastrais distintos;
- preservar identificação por CNPJ/unidade no banco;
- operações documentais devem continuar distinguindo as unidades quando a fonte exigir.

## 10. Motor de grafia e normalização

**DECISÃO HISTÓRICA APROVADA / IMPLEMENTAÇÃO OBSERVADA**

O Tools possuía/previa regras de grafia centralizadas, inclusive referência a excecoes_grafia.

Objetivo: impedir que cada módulo formate nome de forma diferente.

Regras recuperadas:

- preservar nome legal/original;
- normalização serve para matching, busca, pasta sugerida e apresentação controlada;
- não transformar tudo em caixa alta;
- siglas e iniciais reconhecidas permanecem em caixa alta;
- partículas internas podem permanecer minúsculas;
- não inventar acentuação que a fonte não fornece;
- nomes especiais devem admitir exceções cadastradas;
- sanitização de nome de arquivo/pasta não pode destruir a grafia armazenada no cadastro;
- comparação deve ser tolerante a variações necessárias sem sobrescrever o valor original.

Exemplos históricos usados na discussão:

- VJS deve permanecer como sigla;
- Wedersonia A de Oliveira deve preservar a inicial A, sem normalização ingênua.

Também existem exceções gerais conhecidas do ecossistema que devem continuar tratadas como exceção configurável, não regra espalhada.

## 11. Arquivo Digital / Storage como evolução

**DECISÃO HISTÓRICA APROVADA, POSTERIOR AO MODELO INICIAL**

O entendimento amadureceu de “criar árvore de pastas” para **Arquivo Digital do Escritório**:

- estrutura física organizada;
- banco indexa o que existe no disco;
- documentos continuam fisicamente no Storage;
- motor geral observa a árvore;
- arquivo novo deve ser detectado sem exigir cadastro manual em tela;
- indexação atualiza o sistema;
- migração de legado pode ser gradual;
- nenhum watcher deve apagar arquivo porque ele sumiu da visão lógica.

A evolução proposta para o Storage passou a classificar a árvore por perfil operacional.

PF:

- Produtor Rural;
- Empregador Doméstico;
- Profissional Liberal/CI;
- A Definir.

PJ:

- MEI;
- Simples Nacional;
- Lucro Presumido;
- Lucro Real;
- Produtor Rural PJ;
- A Definir.

Essa classificação é **posterior à DEC-002** e deve ser tratada como evolução do Arquivo Digital, não como prova de que a árvore antiga já possuía exatamente essas raízes.

## 12. Watcher, indexação e reconciliação

**DECISÃO HISTÓRICA APROVADA**

Motor geral do Storage:

- observa recursivamente pastas/subpastas;
- detecta inclusão/alteração;
- aguarda estabilidade do arquivo antes de ler;
- indexa metadados;
- calcula hash;
- classifica quando possível;
- associa a cliente/competência quando seguro;
- encaminha ambiguidade para revisão;
- executa reconciliação periódica completa além do watcher;
- registra arquivo ausente no filesystem sem apagar histórico;
- não usa “limpeza” para excluir original.

Conceitos úteis posteriormente registrados:

- WAITING_STABILITY;
- MISSING_ON_FILESYSTEM.

O watcher é observador/indexador, não faxineiro.

## 13. Órfãos e duplicidades

**DECISÃO HISTÓRICA APROVADA**

- arquivo sem cliente identificado não é descartado;
- pasta sem vínculo cadastral deve aparecer para conciliação;
- cadastro sem pasta deve aparecer como vínculo ausente;
- duplicidade por hash não autoriza exclusão;
- documento repetido pode ser marcado como duplicado/conhecido;
- retenção/limpeza deve se limitar a temporários, cache, logs e backups conforme política específica;
- originais, versões, saídas e evidências ficam fora de limpeza automática destrutiva.

## 14. Estado de autoridade

A estrutura DEC-002 continua sendo patrimônio canônico histórico do Tools.  
O modelo de Storage/Arquivo Digital posterior é uma evolução conceitual importante.  
Qualquer reconstrução deve confrontar ambos com o runtime físico antes de declarar uma árvore definitiva para migração.
