# Axiom Tools — Cadastro, Identidade, Clientes e Integrações

Data: 23/09/2026

## 1. Cadastro como índice operacional

**CANÔNICO / DECISÃO HISTÓRICA APROVADA**

O cadastro do Tools não substitui os documentos físicos. Ele indexa pessoas/empresas, configurações e vínculos necessários à operação documental.

Campos/conceitos históricos:

- PF/PJ;
- CPF/CNPJ;
- nome legal/original;
- status;
- caminho físico/vínculo de pasta;
- classificações operacionais;
- inscrições;
- histórico de alteração;
- parâmetros por cliente;
- formas de entrega;
- regras aplicáveis ao fechamento.

Exclusão administrativa do cadastro nunca autoriza exclusão da pasta ou dos documentos.

## 2. Perfis de cliente recuperados

**DECISÃO HISTÓRICA APROVADA**

PF:

- Produtor Rural;
- Empregador Doméstico;
- Profissional Liberal/Contribuinte Individual;
- outros PF conforme cadastro.

PJ:

- Simples Nacional;
- Lucro Presumido;
- Lucro Real;
- MEI como classificação dentro do Simples;
- Produtor Rural PJ;
- associações/imunes quando existentes no universo cadastral.

Regras importantes:

- MEI é classificação do Simples, não natureza paralela sem relação;
- Funrural só se aplica quando Produtor Rural estiver marcado e conforme cenário;
- PF/PJ e enquadramento não devem ser inferidos apenas do nome da pasta.

## 3. Identificadores

**DECISÃO HISTÓRICA APROVADA**

Identificadores relevantes ao patrimônio:

- CNPJ;
- CPF;
- IE;
- IM quando aplicável;
- CAEPF;
- CEI legado;
- CNO quando aplicável;
- PIS/NIT para pessoas;
- CNAE/CBO/CID em domínios correspondentes.

A identificação documental deve priorizar documento explícito e confiável.

Regra recuperada do e-CAC:

1. CPF/CNPJ explícito no conteúdo;
2. identidade pelo arquivo/cadastro;
3. nome como apoio;
4. heurística nunca pode aceitar número de código de barras como CNPJ apenas porque possui comprimento/formato semelhante.

## 4. Matriz e filiais

**DECISÃO HISTÓRICA APROVADA**

- matriz e filial possuem identidades cadastrais próprias;
- podem compartilhar pasta física;
- motor deve distinguir valor repetido/consolidado de valor aditivo por inscrição/matrícula;
- vínculo físico compartilhado não elimina rastreabilidade por unidade.

## 5. Importação de clientes

**CANÔNICO HISTÓRICO**

A AXT-003 definiu:

- importação XLS/XLSX;
- revisão antes de consolidar alteração sensível;
- prevenção de duplicidade por documento;
- suporte a registros antigos/inativos/baixados;
- cadastro manual e edição;
- inativação/reativação;
- exclusão somente cadastral;
- busca.

Uma importação histórica chegou a classificar centenas de registros entre prontos, duplicados e pendentes, reforçando que a importação precisa de revisão e não pode ser “tudo ou nada”.

## 6. Status

**DECISÃO HISTÓRICA APROVADA**

Foram usados/recuperados estados como:

- ativo;
- inativo;
- baixado;
- transferido/saiu do escritório.

O estado cadastral permanente é diferente da situação mensal:

- cliente ativo pode estar sem movimento em uma competência;
- cliente pode estar fora de uma chamada;
- cliente transferido não deve ser apagado do histórico;
- situação mensal não deve sobrescrever classificação cadastral.

## 7. Dados de pessoas e DP

**DECISÃO HISTÓRICA APROVADA**

O cadastro de funcionários precisa preservar dados necessários à operação real. Um exemplo explicitamente lembrado foi **nome da mãe**, relevante para processos de rescisão/documentação.

O sistema deve permitir que regras futuras consumam CNAE principal/secundários e demais classificações sem duplicá-las em cada motor.

## 8. RFB / CNPJ

**DECISÃO HISTÓRICA APROVADA**

A integração cadastral deve ser desacoplada por provider.

Objetivos:

- enriquecer cadastro;
- comparar dado atual × fonte;
- registrar proveniência;
- permitir aplicação assistida;
- manter cache;
- não sobrescrever silenciosamente dado humano/legal;
- não transformar fonte de contingência em “oficial” sem identificação.

O histórico do projeto previu provider oficial quando disponível e contingência por fontes públicas/terceiras claramente identificadas.

## 9. Sintegra / SEFAZ GO

**DECISÃO HISTÓRICA APROVADA**

Fluxo desejado:

    Cadastro atual → abrir consulta → autenticação/ação humana quando necessária → capturar resultado → comparar Atual × Sintegra/SEFAZ → revisar diferenças → aplicar seletivamente → registrar fonte/evidência

Dados passíveis de comparação:

- IE;
- situação;
- razão social;
- nome fantasia;
- CNPJ/CPF;
- endereço;
- município/UF;
- CNAE/atividade;
- datas de situação/baixa;
- inscrições apresentadas pela fonte.

Nunca gravar automaticamente “às cegas”.

## 10. Complemento de navegador

**DECISÃO HISTÓRICA APROVADA / PLANEJADA**

Foi aprovada a ideia de complemento/extensão do navegador para capturar a página já aberta pelo usuário e enviá-la ao Tools.

Princípios:

- não “espionar” aba arbitrária;
- captura explícita iniciada pelo usuário;
- usar página aberta/autenticada;
- comparar antes de aplicar;
- preservar histórico;
- não burlar CAPTCHA;
- não contornar autenticação;
- Firefox/WebExtension foi uma direção técnica discutida em fase posterior.

A existência dessa decisão não prova que toda a extensão esteja preservada na main atual.

## 11. Portais externos

**CANÔNICO**

Fluxo geral:

1. Tools abre navegador/portal;
2. usuário autentica;
3. usuário cumpre CAPTCHA/MFA/confirmação;
4. documento/resultado é obtido;
5. arquivo é salvo em origem configurada;
6. Tools detecta/processa;
7. vínculo, fonte e evidência são registrados.

Esse modelo foi aplicado conceitualmente a eCAC, eSocial, Sintegra/SEFAZ e outros portais.

## 12. Central de Conexões

**IMPLEMENTAÇÃO OBSERVADA / DECISÃO HISTÓRICA**

O runtime/histórico registra conceitos como:

- Central de Conexões;
- Origens e conexões;
- vínculos de pasta;
- FolderRegistryRepository;
- FolderLinkRepository;
- FolderOriginRepository;
- ConfigClientesRepository;
- histórico de cliente;
- salvar vínculo legado;
- remover vínculo lógico;
- marcar conciliação.

Esses nomes são evidência importante de que o Tools evoluiu além de uma simples pasta-base.

## 13. Atualização assistida

**DECISÃO HISTÓRICA APROVADA**

Toda atualização externa sensível deve manter:

- valor anterior;
- valor proposto;
- fonte;
- data/hora;
- operador;
- evidência quando possível;
- decisão aplicar/ignorar;
- histórico.

“Ignorar” deve ser uma ação padronizada para casos protegidos, compartilhados, legados ou ambíguos sem eliminar a evidência.

Motivos históricos incluem:

- antigo;
- baixado;
- transferido;
- histórico;
- sem movimento;
- ambiguidade;
- outro motivo documentado.

## 14. Relação cadastro × motores

**DECISÃO HISTÓRICA APROVADA**

O cadastro é fonte importante de aplicabilidade.

Exemplos:

- MEI altera expectativa de guia;
- doméstico altera expectativa para DAE;
- produtor rural ativa regras rurais;
- chamada mensal decide se entra no processamento corrente;
- forma de entrega decide saída física/eletrônica;
- matriz/filial/matrícula altera composição por fonte.

Heurística do documento não deve se sobrepor silenciosamente ao perfil cadastral confirmado.
