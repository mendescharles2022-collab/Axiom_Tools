# Contrato V8 — Pipeline documental observável e recomposição da Conferência

Data: 28/08/2026
Status: **contrato obrigatório / V8 não homologada**

## 1. Problema confirmado

A V8F2 possui casos em que o documento existe ou foi reprocessado, mas a Conferência continua mostrando ausência/divergência.

Casos registrados incluem:

- MMT Empreendimentos — cliente não identificado após reprocessamento;
- Alex Douglas de Andrade — cliente não identificado e DARF real não alimentando a Conferência;
- Extratos 449/450 — tipo e competência 08/2026 reconhecidos, mas cliente perdido após reprocessamento;
- guias existentes em conexões que não reaparecem corretamente na composição após reprocessamento.

Portanto `documento ausente` não é diagnóstico suficiente.

## 2. Pipeline canônico

Cada arquivo deve atravessar estados explícitos e auditáveis:

1. `DESCOBERTO` — arquivo localizado na conexão/upload/repositório;
2. `INGERIDO` — registrado no processamento com hash e origem;
3. `LIDO` — leitura nativa concluída ou OCR fallback executado uma única vez quando necessário;
4. `CLASSIFICADO` — tipo documental determinado;
5. `IDENTIFICADO` — identidade do cliente/grupo/inscrição determinada;
6. `COMPETENCIA_DEFINIDA` — explícita ou inferida com proveniência;
7. `EXTRAIDO` — motor especialista produziu dados estruturados;
8. `PERSISTIDO` — resultado candidato/vigente registrado de forma íntegra;
9. `VINCULADO` — documento associado ao cliente/competência/inscrição corretos;
10. `COMPOSTO` — incluído no conjunto documental da obrigação;
11. `CONFERENCIA_RECALCULADA` — evento provocou novo cálculo da obrigação/cliente.

## 3. Falha precisa

A ocorrência deve registrar o primeiro estágio que não foi concluído.

Exemplos:

- `FALHA_IDENTIDADE`;
- `FALHA_COMPETENCIA`;
- `FALHA_EXTRACAO`;
- `FALHA_VINCULO`;
- `FALHA_COMPOSICAO`;
- `FALHA_RECALCULO`.

A UI pode traduzir para linguagem operacional, mas o código técnico deve permanecer disponível no detalhe/auditoria.

## 4. Distinção entre ausência e falha técnica

`DOCUMENTO_AUSENTE` só é válido quando:

- a obrigação é aplicável;
- o universo de busca foi percorrido;
- não existe documento candidato compatível nas conexões/repositório;
- não existe item órfão potencialmente relacionado;
- não houve falha técnica que impeça descoberta/leitura/vínculo.

Se o arquivo existe mas parou na cadeia, a ocorrência deve apontar a falha real.

## 5. Identidade

A resolução deve usar evidências com precedência controlada:

- CPF/CNPJ/CAEPF/CNO/CEI e identificadores estruturados do documento;
- vínculo cadastral de inscrições;
- chaves oficiais da fonte;
- nome/razão social normalizado;
- nome do arquivo como fallback assistido, nunca como única prova quando houver conflito.

Múltiplas inscrições podem pertencer ao mesmo cliente; preservar a inscrição de origem no documento.

## 6. Competência

A competência explícita do documento prevalece.

Inferência usa calendário configurado/versionado e precisa persistir a proveniência.

Conflito de competência vai para revisão, sem roteamento silencioso.

## 7. Reprocessamento

Reprocessar deve reiniciar somente os estágios necessários sobre um candidato separado.

A versão vigente não é apagada.

Quando o candidato é promovido:

- atualizar vínculo/composição afetados;
- disparar recálculo event-driven da Conferência;
- preservar correlation_id para rastrear todo o percurso.

## 8. Descoberta em conexões

A ação de reprocessar pendências deve diferenciar:

- reprocessar arquivo já conhecido;
- redescobrir arquivo novo/alterado em conexão;
- reconciliar arquivo físico existente sem índice no banco;
- reavaliar órfão já persistido.

Uma opção não pode fingir executar as outras.

## 9. Reconciliação banco ↔ filesystem

Precisa existir auditoria bidirecional:

- arquivo físico sem índice → ocorrência de não indexado;
- índice sem arquivo físico → ocorrência de indisponibilidade;
- hash alterado → nova evidência/candidato;
- mesmo hash em caminhos diferentes → deduplicação física sem apagar origem.

## 10. Regressões mínimas

### MMT Empreendimentos

Documento identificável deve atingir `VINCULADO` e atualizar a Conferência; se não atingir, estágio exato deve ser mostrado.

### Alex Douglas

DARF real precisa percorrer a cadeia e eliminar `DARF AUSENTE INESPERADO` quando a obrigação for explicada; FGTS mensal zero/rescisão permanece regra separada.

### Jair 449/450

Após recuperação/reprocessamento seguro:

- tipo e competência preservados;
- cliente 826 recuperado;
- cada inscrição/matrícula preservada;
- ambos chegam à composição multi-Extrato;
- Conferência recalcula federal/FGTS corretamente.

## 11. Observabilidade

Por arquivo, manter tempos e resultado de cada estágio quando útil:

- iniciado_em;
- concluido_em;
- status;
- motor/versão;
- erro_codigo;
- correlation_id.

Isso permite separar gargalo de leitura, identidade, composição ou recálculo.

## 12. Critério de homologação

A V8 só homologa a cadeia documental quando um arquivo novo, um órfão e um reprocessamento percorrem de ponta a ponta o fluxo e a Conferência muda automaticamente sem correção manual de banco ou navegação que provoque sincronização oculta.
