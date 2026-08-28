# Protocolo executável — Reconciliação runtime ↔ repositório V8

Data: 28/08/2026
Status: **protocolo obrigatório antes da implementação final/homologação**

## 1. Objetivo

Tornar o repositório oficial um espelho rastreável do código operacional que será corrigido, testado, empacotado e instalado, sem importar dados reais do escritório para o controle de versão.

## 2. Situação atual confirmada

A auditoria canônica foi executada sobre `Axiom_Tools(20260827-175623).zip`, cuja árvore operacional contém módulos V8 não presentes integralmente no `main` atual.

O `main` também mantém metadado de versão incompatível com a linha operacional real.

Portanto nenhuma correção somente documental ou feita na árvore reduzida pode ser considerada correção do runtime canônico.

## 3. Princípio de reconciliação

A fonte operacional deve ser capturada de modo controlado e comparada com o repositório.

Não fazer cópia cega da raiz instalada.

Separar:

### Deve ser elegível para versionamento

- código-fonte Python;
- templates;
- CSS/JS próprios;
- testes;
- scripts de instalação/migração controlados;
- arquivos de configuração-modelo sem segredos;
- metadata de versão/build;
- documentação técnica aplicável.

### Nunca deve entrar no repositório

- banco SQLite operacional;
- documentos de clientes;
- PDFs reais;
- certificados digitais;
- tokens/segredos/senhas;
- cookies/sessões;
- logs com dados sensíveis;
- backups operacionais;
- caches/temp;
- downloads reais de portais;
- arquivos de configuração local contendo credenciais/caminhos sensíveis quando não sanitizados.

## 4. Inventário da árvore runtime

Na cópia segura do runtime, gerar inventário contendo:

- caminho relativo;
- tamanho;
- SHA-256;
- categoria (`codigo`, `teste`, `template`, `static`, `script`, `dados`, `segredo`, `temp`, etc.);
- decisão `VERSIONAR`, `IGNORAR`, `REVISAR`.

Regras de exclusão devem ser aplicadas antes de qualquer commit.

## 5. Comparação com `main`

Para os arquivos versionáveis:

- existente igual → nenhuma ação;
- existente diferente → diff/revisão;
- runtime novo → candidato a inclusão;
- somente GitHub → revisar se é fundação histórica, arquivo obsoleto ou componente ainda necessário.

Não apagar arquivo do repositório apenas porque não apareceu em uma cópia parcial do runtime sem entender sua função.

## 6. Base de trabalho para correção

Depois da reconciliação:

1. estabelecer uma árvore oficial de código;
2. registrar commit-base equivalente ao runtime auditado, ou documentar diferenças inevitáveis;
3. executar a suíte baseline antes das correções V8;
4. corrigir os bloqueadores sobre essa árvore;
5. executar regressão e benchmark na mesma árvore.

## 7. Dados necessários para testes

Não versionar banco/documentos reais.

Criar:

- fixtures sintéticas;
- cópias locais de homologação fora do Git;
- arquivos sanitizados quando realmente necessários;
- geradores de cenário para os 28 casos quando possível.

A proveniência das fixtures deve permitir reproduzir a regra sem expor dado operacional desnecessário.

## 8. Versão canônica

Após a reconciliação deve existir uma única fonte de versão consumida por:

- metadata do pacote;
- runtime;
- health;
- logs;
- instalador;
- manifesto do pacote;
- relatório de homologação.

O build deve incluir commit SHA e schema version.

## 9. Manifesto do pacote

Gerar manifesto com hashes SHA-256 dos arquivos controlados que serão instalados.

O instalador deve validar o manifesto antes de aplicar e registrar o conjunto efetivamente instalado.

## 10. Regressão da reconciliação

Antes de iniciar correções de negócio:

- importar/estabelecer árvore reconciliada;
- executar testes baseline;
- iniciar aplicação em ambiente de homologação;
- comparar rotas/módulos esperados com o runtime auditado;
- verificar que nenhuma funcionalidade operacional desapareceu apenas por erro de reconciliação;
- verificar que nenhum dado sensível entrou no Git.

## 11. Proibições

- não fazer commit do ZIP bruto com banco/documentos;
- não copiar `data`, `logs`, `backups`, `documentos`, `temp` como código;
- não declarar o `main` reconciliado sem comparação de hashes/inventário;
- não gerar pacote a partir de working tree diferente da testada;
- não corrigir produção e depois tentar reconstruir o código “de memória”.

## 12. Critério de conclusão

B06 só pode ser marcado `CORRIGIDO_HOMOLOGADO` quando:

- árvore operacional controlada estiver reconciliada com o repositório;
- dados/segredos estiverem excluídos;
- baseline reproduzir o sistema auditado;
- commit-base estiver identificado;
- todas as correções posteriores ocorrerem nessa árvore oficial.

B42 só pode ser homologado quando o pacote final apontar para esse commit, schema e manifesto, e o runtime instalado reportar a mesma identidade.
