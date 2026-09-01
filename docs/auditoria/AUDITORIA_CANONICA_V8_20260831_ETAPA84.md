# Auditoria canônica V8 — Etapa 84

Data: 31/08/2026  
Status: **VERIFICAÇÃO INDEPENDENTE E READ-ONLY DO STAGING RECONCILIADO TESTADA / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Objetivo

A Etapa 83 passou a materializar um baseline aceito exclusivamente em staging isolado, sem escrever no runtime operacional nem na `main`.

Ainda faltava uma segunda camada que não confiasse cegamente no materializador ou em seu próprio relatório.

A Etapa 84 fecha essa lacuna com um verificador independente e read-only.

## 2. Novo verificador

Novo script:

`scripts/verify_reconciled_staging.py`

Entradas:

- diretório de staging já materializado;
- `RECONCILIATION_BASELINE_ACCEPTANCE.json` correspondente.

O verificador não precisa do runtime nem do repositório original para decidir se a árvore materializada continua fiel ao aceite.

## 3. Aceite revalidado

Antes de examinar o staging, o verificador confirma novamente:

- versão e modo do aceite;
- `review_complete = true`;
- `baseline_ready = true`;
- `automatic_write_allowed = false`;
- `execution_performed = false`;
- `v8_homologated = false`;
- `acceptance_sha256` lógico válido.

## 4. Relatório de materialização não é tratado como autoridade única

O `RECONCILED_STAGING_REPORT.json` é validado quanto a:

- versão e modo;
- vínculo ao `acceptance_sha256` informado;
- `staging_materialization_performed = true`;
- ausência de escrita no runtime e repositório;
- ausência de deploy operacional;
- ausência de escrita automática nas fontes;
- V8 não homologada;
- `report_sha256` lógico válido.

Depois disso, o conteúdo do relatório é comparado com a árvore real.

## 5. Inventário e árvore são recalculados

Para cada item em `staging_files`, o verificador confere:

- caminho relativo seguro;
- unicidade;
- tamanho;
- SHA-256;
- existência como arquivo regular;
- ausência de symlink.

Em seguida percorre o staging e exige igualdade exata entre:

- arquivos realmente existentes;
- arquivos declarados no relatório.

Assim, arquivo extra ou faltante é bloqueado.

Também são recalculados:

- `file_count`;
- `tree_sha256`.

## 6. Mapeamento de decisões é refeito de forma independente

O verificador possui seu próprio mapeamento de áreas para destinos canônicos, em vez de reutilizar diretamente a função do materializador.

Isso reduz o risco de um mesmo erro de mapeamento ser compartilhado por produtor e verificador.

Para cada decisão aceita:

- `ADOPT_RUNTIME` exige que o arquivo materializado tenha exatamente o `runtime_sha256` aceito;
- `KEEP_REPO` exige exatamente o `repo_sha256` aceito;
- `EXCLUDE_WITH_REASON` exige ausência do arquivo no staging.

Também são detectadas colisões de destino e duplicidade de decisões aplicadas.

O `applied_decisions` do relatório precisa coincidir exatamente com o que o aceite determina.

## 7. Relatório reforjado não basta para esconder fraude

As regressões incluem cenários nos quais a árvore é alterada e depois o relatório é recalculado/reassinado logicamente para tentar esconder a alteração.

O verificador continua bloqueando quando:

- o alvo de uma decisão é trocado;
- um arquivo previamente excluído reaparece;
- um segredo é inserido e o inventário é recalculado;
- `tree_sha256` é alterado com `report_sha256` válido;
- uma decisão aplicada é duplicada e o relatório é re-hashado.

Logo, a segurança não depende somente de detectar edição bruta do JSON.

## 8. Segurança e pureza da verificação

A árvore é novamente varrida para:

- symlinks;
- conteúdo proibido;
- possíveis segredos embutidos.

O staging é fotografado por hash antes e depois da verificação.

Se houver qualquer alteração produzida pelo próprio verificador, a execução falha.

O resultado válido declara:

- `staging_unchanged = true`;
- `operational_deployment_performed = false`;
- `source_write_performed = false`;
- `v8_homologated = false`;
- `verification_ok = true`.

## 9. Regressões

Novo arquivo:

`tests/test_verify_reconciled_staging.py`

Cobertura principal:

- staging válido verifica sem mutação;
- adulteração de arquivo detectada por tamanho ou hash;
- arquivo extra detectado;
- arquivo faltante detectado;
- adulteração simples do relatório detectada;
- aceite válido diferente rejeitado;
- relatório reforjado não pode mudar alvo de decisão;
- arquivo excluído não pode reaparecer mesmo com inventário reforjado;
- segredo inserido não pode ser escondido com novo inventário;
- symlink inserido é bloqueado;
- `tree_sha256` adulterado é bloqueado mesmo com hash do relatório recalculado;
- decisão aplicada duplicada é bloqueada mesmo com hash do relatório recalculado;
- saída CLI existente não é sobrescrita.

## 10. Evidência canônica

GitHub Actions:

- run: `33462473281`;
- commit auditado: `100bb40521a80e976a6d78dca8c0e30aad2eed3f`;
- Python: `3.12.14`;
- testes: `584 OK`;
- produtor: `POWERSHELL_B06_SMOKE_OK`;
- consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- plano: `POWERSHELL_B06_PLAN_SMOKE_OK`;
- esqueleto: `POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9783649332`;
- SHA-256: `8951579403ccb548511567e6f90d7c04ae3eb9ea1f97f206a5c0c32b4ca8d5b1`.

Preflight do mesmo marco:

- B homologados: `0/50`;
- C PASS: `0/28`;
- mapa causal: `28/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 11. Estado correto do B06

B06 permanece **`BLOQUEADO_POR_RUNTIME`**.

A Etapa 84 verifica fixtures de staging geradas em testes; ela não comprova que a instalação Windows física do escritório foi coletada, revisada, aceita, materializada ou verificada.

A cadeia preparada agora é:

1. handoff físico;
2. consumo seguro;
3. diff;
4. plano;
5. esqueleto `PENDING`;
6. revisão humana;
7. validação;
8. aceite imutável;
9. materialização somente em staging;
10. verificação independente read-only;
11. execução dos guardrails estáticos sobre a árvore verificada;
12. somente depois, integração/correções controladas.

## 12. Próximo avanço seguro

A próxima etapa deve executar um preflight estático consolidado sobre uma árvore de staging que passe primeiro pela verificação da Etapa 84.

Esse preflight deve:

- chamar a verificação read-only antes de qualquer auditor;
- vincular hashes das políticas canônicas utilizadas;
- executar apenas auditores estáticos aplicáveis à árvore;
- classificar cada contrato como `PASS`, `FAIL` ou `NOT_APPLICABLE`;
- nunca transformar resultado de tooling em homologação de blocker;
- escrever somente o relatório de auditoria fora do staging.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
