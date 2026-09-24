# Axiom Tools — Processamento Documental, Motores e Reprocessamento

Data: 23/09/2026

## 1. Papel do Processamento

**DECISÃO HISTÓRICA APROVADA**

Processamento de Arquivos é infraestrutura documental/técnica. Ele não substitui Conferência nem Fechamento.

Responsabilidades:

- receber arquivo;
- observar pastas de entrada;
- identificar;
- classificar;
- extrair;
- persistir metadados;
- arquivar/indexar;
- reprocessar falhas técnicas;
- emitir evidências para Conferência;
- manter fila, sessões, hash, cache e checkpoints.

Não deve:

- declarar cliente fechado;
- transformar divergência de conferência em “falha técnica”;
- alterar competência por simples abertura de tela;
- misturar histórico antigo com fila operacional atual.

## 2. Pipeline de leitura

**CANÔNICO / DECISÃO HISTÓRICA APROVADA**

Regra:

    original preservado
       ↓
    leitura textual nativa
       ↓
    se insuficiente → OCR uma única vez
       ↓
    conteúdo extraído persistido/reutilizado
       ↓
    classificação
       ↓
    identidade
       ↓
    competência
       ↓
    valores/pessoas/dados operacionais
       ↓
    validação
       ↓
    roteamento/conferência

Leitura nativa ocorre antes de OCR.

OCR é fallback, não primeira tentativa e não deve ser repetido desnecessariamente por cada especialista.

## 3. Dados persistidos por documento

**DECISÃO HISTÓRICA APROVADA**

Conforme o tipo e a fase:

- ID;
- arquivo/origem;
- SHA-256;
- tamanho;
- data de ingestão;
- tipo sugerido/confirmado;
- parser/motor;
- cliente sugerido/confirmado;
- CPF/CNPJ/CAEPF/matrícula quando aplicável;
- competência;
- evidência/proveniência da competência;
- valores;
- pessoas;
- confiança;
- texto extraído;
- status técnico;
- status de revisão;
- caminho físico/repositório;
- versão/substituição;
- sessão PROC;
- histórico.

Arquivo físico fica fora do SQLite; banco guarda índice e metadados.

## 4. Fila e sessões

**DECISÃO HISTÓRICA APROVADA**

Controle por arquivo deve usar, no mínimo:

- ID;
- hash;
- status;
- sessão/PROC.

A fila operacional é persistente, porém a tela pode limpá-la visualmente após conclusão da sessão.

Histórico não deve poluir a fila corrente; aparece quando o usuário entra em visão histórica/seleciona contexto.

Sessão agrega execução, mas cada arquivo conserva identidade própria.

## 5. Semântica técnica de progresso

**DECISÃO HISTÓRICA APROVADA**

- 0% · Processo não iniciado;
- X% · Processando;
- 100% · Processamento concluído;
- 100% · Concluído com falhas técnicas;
- X% · Interrompido.

100% significa que o motor percorreu a sessão. Não significa:

- conferido;
- correto;
- sem divergência;
- fechado.

Pendências técnicas pertencem ao Processamento. Pendências documentais/de batimento pertencem à Conferência.

## 6. Escala

**DECISÃO HISTÓRICA APROVADA**

Projetar para centenas/milhares de documentos por ciclo:

- lotes;
- assíncrono/incremental;
- paralelismo controlado;
- memória controlada;
- checkpoints;
- retry;
- idempotência;
- cache;
- hash;
- reuso do texto lido;
- cruzamento parcial assim que fontes chegam.

Volumes históricos de referência usados no projeto incluíram centenas de contracheques/recibos, centenas de relatórios Domínio, centenas de DARFs e FGTS.

## 7. Motor Domínio

**DECISÃO HISTÓRICA APROVADA / IMPLEMENTAÇÃO OBSERVADA**

Tipos reconhecidos ou planejados no motor:

- Extrato Mensal;
- recibo/contracheque;
- pró-labore;
- relatórios operacionais;
- informações relacionadas ao fechamento;
- relatórios eSocial exportados do Domínio quando utilizados no fluxo.

O Domínio é fonte oficial da folha.

O parser deve separar:

- empregados;
- contribuintes/pró-labore;
- diretores;
- valores federais;
- FGTS esperado;
- eventos relevantes;
- quantidade inicial/admissões/desligamentos.

Regra auditada: diretor/pró-labore não pode ser contado automaticamente como empregado apenas por possuir vínculo textual “Trabalhando”.

## 8. Motor eSocial

**DECISÃO HISTÓRICA APROVADA**

O eSocial complementa a camada do Domínio com evidências de transmissão/eventos.

A competência deve preferir evidência documental. Quando o documento não trouxer competência suficiente, pode usar calendário configurável.

Janela operacional padrão histórica:

- do dia 25 do mês da competência;
- até o dia 09 do mês seguinte.

Essa janela serve como evidência auxiliar, não como licença para inventar competência.

Devem existir exceções configuráveis para:

- dezembro;
- 13º salário;
- calendários especiais.

Recibos de transmissão precisam permanecer como evidência rastreável.

## 9. Motor e-CAC / DARF / DCTFWeb

**DECISÃO HISTÓRICA APROVADA**

Objetivos:

- identificar contribuinte;
- identificar competência/período;
- extrair composição federal;
- comparar com o esperado;
- registrar fonte/proveniência;
- tratar impedimento de emissão/acesso sem falsificar “zero”.

A DARF pode conter composição de múltiplos tributos/encargos:

- previdenciário;
- IRRF;
- PIS sobre folha quando aplicável;
- Funrural/SENAR conforme cenário;
- outros débitos reconhecidos.

Regra administrativa real: para certos clientes, a equipe fiscal emite a DARF consolidada com componentes fiscais e previdenciários; o DP pode ser responsável apenas pelo FGTS. A ausência de emissão do DP não significa ausência de obrigação.

## 10. Motor FGTS Digital

**DECISÃO HISTÓRICA APROVADA**

Deve distinguir:

- FGTS mensal;
- FGTS rescisório;
- recolhimento antecipado em razão de rescisão;
- multa rescisória;
- múltiplas evidências no mesmo cliente/competência;
- guia consolidada versus valores por matrícula.

Não pressupor “uma guia de FGTS por competência”.

Composição documental válida pode somar múltiplas guias para explicar o valor esperado.

## 11. DAE — MEI e doméstico

**DECISÃO HISTÓRICA APROVADA**

### MEI
Quando cadastro estiver marcado como MEI:

- não criar expectativa mensal genérica de guia FGTS Digital autônoma;
- o recolhimento do empregado segue regra específica do DAE;
- exceção extraordinária precisa ser explicitamente identificada.

### Empregador doméstico
O fluxo esperado utiliza DAE do eSocial, e não DARF/FGTS Digital autônomos como regra mensal comum.

## 12. eConsignado

**DECISÃO HISTÓRICA APROVADA**

eConsignado deve operar somente no universo da competência/chamada aplicável.

Separar:

- parcela consignada ordinária;
- tratamento em rescisão;
- valores/garantia vinculados ao FGTS;
- situações sem evidência positiva.

A ausência de consignado não pode gerar expectativa automática universal.

O motor deve ser idempotente e seguro em retry.

## 13. Especialista Identidade

**DECISÃO HISTÓRICA APROVADA**

Prioridades:

1. identificador explícito no documento;
2. matrícula/inscrição vinculada;
3. metadado do arquivo;
4. nome e matching cadastral;
5. revisão humana.

Nunca aceitar número plausível por comprimento sem validar contexto.

Documento com cliente não identificado fica em revisão, não é descartado.

## 14. Especialista Competência

**DECISÃO HISTÓRICA APROVADA**

A competência deve registrar proveniência:

- explícita no documento;
- derivada de período;
- inferida por calendário;
- herdada de ocorrência/upload contextual;
- confirmada manualmente.

Não usar apenas data de criação/modificação do arquivo.

## 15. Especialistas Valores e Pessoas

**DECISÃO HISTÓRICA APROVADA**

Valores devem ser semanticamente classificados para impedir soma indevida.

Pessoas devem distinguir papel operacional:

- empregado;
- contribuinte;
- sócio;
- diretor;
- trabalhador afastado;
- desligado.

O sistema precisa saber “o que o valor representa” e “quem a pessoa é” antes do cruzamento.

## 16. Reprocessamento

**DECISÃO HISTÓRICA APROVADA**

Existem dois conceitos diferentes:

### Reprocessar falhas técnicas
Roda novamente itens que falharam tecnicamente.

### Reprocessar competência/pendências/divergências
Recalcula utilizando documentos já existentes/vigentes e novas evidências, sem exigir novo upload.

Regras:

- nova sessão auditável;
- não duplicar originais;
- reaproveitar conteúdo/hash quando possível;
- preservar versões anteriores;
- respeitar chamada;
- não incluir cliente de chamada futura;
- recalcular Conferência ao concluir.

## 17. Vinculação sem OCR desnecessário

**DECISÃO HISTÓRICA APROVADA**

Quando arquivo já foi lido e o problema é apenas CLIENTE_NAO_IDENTIFICADO:

- usuário pode vincular cliente;
- vínculo deve persistir;
- status pode sair de revisão;
- não é necessário refazer OCR/leitura;
- associação pode ser aplicada aos documentos equivalentes conforme regra segura.

## 18. Retificação e versionamento

**DECISÃO HISTÓRICA APROVADA**

Estados conceituais históricos:

- Original;
- Retificada I;
- Retificada II;
- versões subsequentes.

Regras:

- registrar data/hora;
- não sobrescrever versão anterior;
- versão nova só se torna vigente após validação;
- documento idêntico por hash/assinatura não cria retificação;
- evidência complementar pode não exigir nova versão material;
- mudança material cria candidata;
- saídas antigas permanecem como histórico e podem ser marcadas substituídas/desatualizadas.

## 19. Repositório

**DECISÃO HISTÓRICA APROVADA**

Organização discutida em dois eixos complementares:

- por fonte/ano/competência/cliente;
- por cliente/competência/tipo.

O índice no banco deve permitir navegar sem depender exclusivamente da árvore física.

Originais preservados; artefatos consolidados de saída são derivados.

## 20. Monitor ao vivo

**DECISÃO HISTÓRICA APROVADA**

Monitor desejado exibe:

- empresa;
- arquivo;
- bloco;
- etapa;
- percentual;
- motor;
- competência;
- status de arquivamento;
- saídas/resultados.

Monitor observa o que acontece. Não altera estado apenas por ser aberto e não executa limpeza destrutiva.

## 21. Regra de ouro

Um motor “funcionando para um cliente” não é critério de qualidade.

Regras devem ser generalizáveis para a carteira inteira, cobertas por casos de regressão reais e capazes de explicar por que classificaram, somaram, ignoraram ou bloquearam determinada evidência.
