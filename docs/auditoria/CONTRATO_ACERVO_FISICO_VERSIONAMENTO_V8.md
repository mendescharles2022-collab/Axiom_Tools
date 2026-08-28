# Contrato V8 — Acervo físico, hash e versionamento documental

Data: 28/08/2026
Status: **princípios permanentes anteriores confirmados / implementação V8 a confrontar no runtime**

## 1. Princípios permanentes já homologados

Desde a base AXT-001/AXT-003, o Axiom Tools mantém:

- nunca excluir automaticamente arquivo original;
- nunca sobrescrever silenciosamente arquivo existente;
- nunca mover/renomear conteúdo legado sem planejamento/confirmacao;
- cadastro, pasta física e documentos são domínios diferentes;
- inativação/exclusão cadastral não apaga filesystem.

Esses princípios continuam vinculantes para o Processamento V8.

## 2. Documento físico x resultado de processamento

Separar conceitualmente:

```text
ARQUIVO FISICO
!=
REGISTRO DE PROCESSAMENTO
!=
VERSAO DA EXTRACAO
!=
EVIDENCIA DA CONFERENCIA
```

O mesmo arquivo físico pode ser processado novamente sem ser sobrescrito ou duplicado fisicamente.

Uma nova extração é nova versão de interpretação, não novo PDF por definição.

## 3. Hash

Cada arquivo ingerido/gerenciado deve possuir hash de conteúdo, preferencialmente SHA-256 ou algoritmo já padronizado no projeto.

O hash serve para:

- identificar arquivo byte a byte idêntico;
- detectar duplicidade física;
- provar que uma versão de extração pertence àquele arquivo;
- validar integridade futura.

Limite importante:

`hash diferente` não significa `obrigação diferente`.

Reemissões ou PDFs regenerados podem ter bytes diferentes e representar o mesmo fato econômico.

## 4. Identidade lógica documental

Além do hash físico, o sistema precisa de identidade lógica baseada, conforme tipo:

- cliente;
- competência/período;
- tipo documental;
- inscrição/matrícula/origem;
- natureza da obrigação;
- identificadores internos do documento;
- fingerprint de valores/fatos centrais.

Isso permite classificar:

- cópia idêntica;
- reemissão equivalente;
- versão sucessora;
- unidade/matrícula distinta;
- evidência complementar.

## 5. Ingestão

Ao encontrar arquivo novo:

1. calcular hash;
2. verificar se o conteúdo já é conhecido;
3. identificar origem/conexão;
4. registrar caminho/origem sem destruir arquivo anterior;
5. criar processamento técnico;
6. só depois classificar/associar na Conferência.

Arquivo idêntico já conhecido não deve criar duplicação econômica nem histórico inútil, mas pode registrar nova ocorrência/origem se isso for operacionalmente relevante.

## 6. Arquivo alterado/substituído na origem

Casos como 307 Looks e documentos adicionados depois exigem detectar mudança real.

Se o caminho/nome é o mesmo, mas hash mudou:

- não assumir que é o mesmo conteúdo;
- registrar nova versão/ocorrência física;
- preservar referência ao hash anterior;
- processar como candidato;
- avaliar materialidade e retificação.

Não sobrescrever a evidência histórica apenas porque o nome do arquivo permaneceu igual.

## 7. Reprocessamento do mesmo físico

Quando o usuário reprocessa um arquivo sem mudança física:

- hash permanece igual;
- versão de extração nova aponta para o mesmo arquivo;
- vigente anterior permanece até promoção;
- candidato pode ser rejeitado;
- arquivo físico não é renomeado/substituído como efeito do reprocessamento.

## 8. Documento substituído/reemitido

Quando existe novo arquivo com hash distinto e mesma obrigação lógica:

- ambos permanecem rastreáveis;
- classificar relação `SUCESSORA`/`REEMISSAO_EQUIVALENTE` conforme evidência;
- somente a versão economicamente vigente participa da composição final quando forem equivalentes;
- não apagar o documento anterior.

## 9. Múltiplas evidências legítimas

No FGTS e outros fluxos, vários PDFs podem representar componentes econômicos distintos.

Nesse caso:

- nenhum é descartado como duplicado apenas por cliente/competência;
- cada documento mantém origem/hash;
- composição decide soma/deduplicação depois da classificação.

## 10. Caminho físico

O banco deve guardar caminho/origem de forma que:

- mudança de caminho não altere hash/identidade histórica;
- arquivo indisponível seja detectável;
- não assumir existência apenas porque o caminho está salvo;
- não usar caminho como única chave do documento.

## 11. Repositório/arquivamento gerenciado

Se o Processamento copiar documentos para área gerenciada do Axiom Tools, a operação deve ser segura:

- copiar/gravar em nome temporário;
- validar hash/tamanho;
- promover para destino final atomicamente quando possível;
- colisão de nome nunca sobrescreve arquivo diferente;
- registrar origem e destino;
- falha deixa origem intacta;
- limpeza de temporário não alcança documento promovido.

A arquitetura física concreta do repositório deve ser confrontada com o ZIP/runtime antes de homologar este ponto.

## 12. Preview/impressão

Preview e impressão devem ler somente arquivos autorizados/referenciados pelo banco e validar existência.

Não construir caminho direto a partir de nome fornecido pelo navegador sem resolução segura.

## 13. Retificação

Mudança material em cliente fechado pode nascer de:

- arquivo físico novo;
- arquivo substituído;
- nova fotografia externa;
- reprocessamento que extrai fato material antes perdido.

A versão fechada anterior permanece ligada às evidências que a originaram.

A retificação candidata aponta para as novas evidências sem reescrever o snapshot antigo.

## 14. Exclusão/limpeza

Ferramentas de limpeza mensal, quando existirem, não podem apagar:

- documento usado por fechamento vigente/histórico;
- documento ligado a retificação;
- versão física necessária para auditoria;
- original cuja retenção esteja prevista.

Limpeza deve distinguir:

- temporários;
- cache regenerável;
- arquivos de entrada já promovidos e comprovadamente duplicados;
- acervo permanente.

Qualquer exclusão física produtiva futura exige contrato específico, autorização e auditoria.

## 15. Regressões obrigatórias

1. mesmo arquivo/hash reprocessado não cria segundo físico;
2. leitura pior não substitui extração vigente;
3. arquivo com mesmo nome e hash diferente é detectado como mudança;
4. reemissão equivalente não duplica valor;
5. matrícula distinta não é tratada como reemissão por engano;
6. origem desaparecida não apaga histórico;
7. colisão de nome não sobrescreve conteúdo diferente;
8. falha no arquivamento mantém origem intacta;
9. retificação antiga continua apontando para evidências da versão antiga;
10. limpeza não remove documento referenciado por fechamento;
11. hash persistido confere com arquivo em regressão de integridade;
12. preview não aceita path traversal/caminho arbitrário.

## 16. Limite da evidência atual

Nesta sessão não foi recuperado o código integral do arquivador/gerenciador documental da V8.

Portanto não foi afirmado que o runtime atual apaga ou sobrescreve fisicamente arquivos durante reprocessamento.

Classificação:

`INTEGRIDADE FISICA — CONTRATO OBRIGATORIO / INSPECAO DIRETA PENDENTE`.

## 17. Critério de homologação

O acervo V8 só será homologado quando for possível provar que a história documental não muda por baixo do banco e que cada resultado de processamento/fechamento continua ligado ao conteúdo físico correto por hash e origem.
