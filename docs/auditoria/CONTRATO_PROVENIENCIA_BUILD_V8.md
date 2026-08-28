# Contrato V8 — Proveniência de build, versão e pacote

Data: 28/08/2026
Status: **achado de governança confirmado / correção obrigatória antes do pacote final**

## 1. Achado

O branch `main` atual mantém `pyproject.toml` com versão `0.1.0`, enquanto a linha operacional documentada e instalada evoluiu por versões como V5.6.14V7, V8, V8A e V8F2.

Além disso, o `main` não espelha integralmente a árvore operacional do ZIP canônico auditado.

Consequentemente, hoje não existe uma única cadeia automática capaz de responder com segurança:

- qual commit originou o pacote instalado;
- qual árvore foi testada;
- qual schema acompanha a versão;
- qual instalador corresponde ao código auditado;
- qual versão deve aparecer na UI/logs/health.

## 2. Princípio

Uma versão homologada precisa ser identificável por máquina, não apenas por nome escrito em relatório ou pasta de backup.

## 3. Identidade mínima do build

Todo pacote final deve possuir manifesto contendo:

```text
produto = Axiom Tools
versao_release
commit_sha
branch/ref de origem
data_hora_build
schema_version
python_target
plataforma_target
hash_manifesto
```

Opcionalmente:

- identificador de pipeline/build;
- conjunto de features/migrações;
- versão mínima suportada para atualização.

## 4. Fonte única da versão

A versão não deve ficar repetida manualmente em diversos arquivos.

Deve existir uma fonte canônica consumida por:

- pacote/metadata Python;
- tela de login/footer quando exibir versão;
- endpoint `/health` ou equivalente;
- logs de inicialização;
- instalador;
- relatório técnico do pacote;
- manifesto de backup/rollback.

## 5. Commit e árvore limpa

Antes de gerar pacote:

- código operacional deve estar sincronizado no repositório oficial;
- working tree utilizada no build deve estar identificada;
- alterações não commitadas precisam ser proibidas ou explicitamente registradas no manifesto;
- arquivos de dados reais, segredos, bancos e documentos não entram no commit de código.

## 6. Reprodutibilidade

Dado o commit e as instruções de build, deve ser possível reconstruir um pacote funcionalmente equivalente.

Não é necessário que ZIPs tenham hash byte a byte idêntico se timestamps do empacotamento variarem, mas o conteúdo controlado deve ser verificável por manifesto de hashes.

## 7. Manifesto de arquivos

O pacote deve listar arquivos controlados com hash SHA-256.

O instalador pode então:

- verificar integridade do payload;
- registrar quais arquivos foram substituídos;
- detectar arquivo ausente/corrompido;
- provar o conjunto exato instalado.

## 8. Banco e schema

Versão de aplicação e versão de schema são relacionadas, mas distintas.

O sistema deve conseguir informar:

```text
app_version
schema_version
ultima_migracao
```

Isso é essencial para rollback e diagnóstico.

## 9. Runtime

Ao iniciar, registrar uma linha estruturada equivalente a:

```text
Axiom Tools <versao>
commit=<sha_curto>
schema=<versao>
python=<versao>
backend_port=5201
```

Sem expor segredo.

## 10. Endpoint de saúde

O health check deve poder informar, ao menos para administrador/ambiente interno:

- produto;
- versão;
- commit/build;
- schema;
- status do banco;
- status geral.

Health não deve expor caminhos sensíveis ou credenciais.

## 11. Instalador e rollback

Manifesto do backup deve registrar:

- versão anterior;
- commit/build anterior quando conhecido;
- schema anterior;
- versão alvo;
- commit/build alvo;
- hashes essenciais.

Rollback restaura um conjunto coerente e registra retorno de versão.

## 12. Testes

Regressões obrigatórias:

1. versão mostrada no runtime coincide com manifesto do pacote;
2. commit registrado coincide com fonte usada no build;
3. payload adulterado/arquivo com hash inválido é detectado;
4. schema incompatível impede liberação operacional;
5. rollback registra corretamente versão anterior restaurada;
6. relatório técnico final cita o mesmo build do instalador;
7. nenhum banco/documento real entra no manifesto como payload versionado.

## 13. Critério de aceite

Nenhum ZIP deve ser chamado de `V8 final` se não for possível rastreá-lo inequivocamente até a árvore de código testada e a versão de schema correspondente.
