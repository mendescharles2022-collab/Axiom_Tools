# Plano de recuperação segura — Jair Ferreira Camargo — Extratos 449/450

Data: 28/08/2026
Status: **procedimento de homologação / não executar diretamente sobre banco oficial sem cópia, backup e reconciliação do runtime**

## 1. Evidência

A auditoria canônica registrou versões anteriores dos arquivos:

- `449-Extrato Mensal.pdf`;
- `450-Extrato Mensal.pdf`;

com:

- `cliente_id=826`;
- competência `08/2026`;
- status `PROCESSADO`;
- completude/confiança de 100%.

Após reprocessamento posterior, as versões vigentes ficaram em `REVISAO`, 90% e sem cliente vinculado.

## 2. Objetivo

Recuperar a interpretação válida sem:

- apagar tentativas posteriores;
- alterar o PDF físico;
- fabricar dados não existentes;
- perder o histórico da regressão;
- fechar ou retificar o cliente antes de recalcular corretamente a composição.

## 3. Pré-condições

1. reconciliar a árvore de código que será usada para a correção;
2. criar backup consistente do banco e runtime;
3. trabalhar primeiro em cópia do SQLite;
4. executar `integrity_check` e `foreign_key_check`;
5. localizar todas as versões/snapshots/históricos dos dois arquivos;
6. confirmar hashes e caminhos físicos dos PDFs;
7. confirmar cliente 826 e suas inscrições CAEPF vinculadas.

## 4. Não fazer

- não editar diretamente a linha atual para simplesmente colocar `cliente_id=826`;
- não apagar a versão `REVISAO`;
- não recalcular valores manualmente no banco;
- não substituir os PDFs;
- não marcar o cliente como FECHADA manualmente;
- não somar automaticamente os dois saldos federais.

## 5. Recuperação documental

Para cada arquivo:

1. localizar a última versão historicamente válida anterior à regressão;
2. validar identidade, competência, tipo, inscrição/matrícula e valores contra a evidência preservada;
3. registrar a tentativa regressiva posterior como versão/tentativa rejeitada, se a estrutura nova permitir;
4. tornar novamente vigente a versão válida por mecanismo de promoção/versionamento, não por apagamento;
5. preservar correlação com o reprocessamento que causou a degradação.

## 6. Valores esperados para regressão

### Extrato 449

- FGTS: R$ 129,68;
- federal consolidado: R$ 511,43.

### Extrato 450

- FGTS: R$ 259,36;
- federal consolidado: R$ 511,43.

## 7. Consolidação correta

Após ambos estarem corretamente vinculados ao mesmo cliente PF e às respectivas inscrições:

### Federal

- considerar R$ 511,43 uma única vez;
- registrar que o saldo consolidado aparece repetido nas unidades/documentos.

### FGTS

- componente 449: R$ 129,68;
- componente 450: R$ 259,36;
- total esperado: R$ 389,04.

Preservar a origem por matrícula.

## 8. Efeito no fechamento

Depois de recuperar os documentos:

1. recalcular as obrigações do cliente/competência;
2. comparar contra a versão de fechamento vigente, se existir;
3. se houver mudança material, abrir retificação candidata;
4. não alterar snapshot anterior retroativamente;
5. bloquear novas saídas durante retificação material.

## 9. Regressões

A recuperação só é aceita se provar:

1. ambos os documentos permanecem no histórico;
2. versões regressivas não desaparecem;
3. cliente correto é 826;
4. competência correta é 08/2026;
5. duas inscrições/CAEPFs continuam distintas;
6. federal não dobra para R$ 1.022,86;
7. FGTS consolida em R$ 389,04;
8. Conference usa ambos os Extratos aplicáveis;
9. nova execução idêntica é idempotente;
10. saída só é liberada pela versão de fechamento vigente após eventual retificação.

## 10. Execução no servidor

A recuperação real deve ocorrer somente depois que o reprocessamento candidato estiver implementado e testado em cópia.

O objetivo é corrigir a causa e então recuperar os dois documentos usando a mesma infraestrutura definitiva, evitando uma correção artesanal irreproduzível.
