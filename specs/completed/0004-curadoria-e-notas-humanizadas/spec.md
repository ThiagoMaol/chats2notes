# Especificação integrada: Curadoria de Segmentos e Geração de Notas Humanizadas

| Campo | Valor |
| --- | --- |
| Formato | Specsfy/2.0 |
| ID | SPEC-0004 |
| Slug | 0004-curadoria-e-notas-humanizadas |
| Status | Complete |
| Effort | 3 |
| Effort updated at | 2026-09-23 |
| Effort rationale | Motor de curadoria e diagramação de notas atômicas para SilverBullet, filtragem de ruído, taxonomia de tags, conformidade com a skill humanizer e manifesto de estado. |
| ClickUp Task | |
| Milestones | M01 |
| Definition Gate | Passed |
| Plan Gate | Passed |
| Delivery Gate | Passed |
| Evidence Contract | 1 |
| Interface para pessoas | Não — ferramenta de linha de comando (CLI) sem interface gráfica web |
| Atualizada em | 2026-09-23 |

## Ato I — Definir

### 1. Problema e resultado

#### Problema

Os segmentos fatiados em `vault/segments/<user>/<session_id>/000X.md` contêm o texto visível de cada turno de diálogo. No entanto:
1. Respostas de LLMs sofrem frequentemente de prolixidade artificial, clichês e introduções desnecessárias que poluem a leitura.
2. Muitos turnos são meramente operacionais ou ruídos ("sim", "1", "prossiga", etc.) e não agregam valor a uma base de conhecimento.
3. Turnos de etapas de frameworks (Specsfy, MVPfy, Brandfy, Companify, etc.) possuem formato estruturado de múltipla escolha com opções e resposta humana que exigem tratamento específico de pair-programming, enquanto perguntas conceituais exigem diagramação de FAQ enxuta para Dev Júnior.
4. Faltam metadados padronizados (YAML frontmatter com tags controladas, referências cruzadas e links rastreáveis) para consumo direto por Live Queries no SilverBullet ou Dataview no Obsidian.

#### Resultado desejado

O desenvolvedor dispõe do motor de curadoria e do subcomando CLI `chats2notes curate` que lê os segmentos fatiados de `vault/segments/` e gera uma enciclopédia pessoal de notas atômicas em `vault/notas/`:
1. **Notas atômicas autossuficientes**: Cada nota contém informação mínima focada (um par Q&A, registro de entrega/conclusão ou input detalhado do usuário).
2. **Filtragem de ruído**: Mensagens triviais ("sim", "1", "prossiga") são descartadas e registradas no manifesto `vault/.curated.json` sem poluir o vault.
3. **Diagramação especializada**:
   - **FAQ**: Título curto, pergunta resumida destacada, resposta super enxuta em tópicos para Dev Júnior (aplicando princípios da skill `humanizer`), divisor horizontal `---`, pergunta completa original e resposta completa original.
   - **Pair-Programming**: Título `<projeto> - <framework> - Pergunta <N>`, pergunta destacada sem opções, resposta escolhida com complemento humano, divisor horizontal `---` e pergunta completa original com todas as alternativas.
4. **Organização 100% plana**: Todas as notas gravadas na raiz de `vault/notas/` com nomes em Title Case (com espaços) e desambiguação numérica `(2)` em colisões, otimizadas para wikilinks e Live Queries no SilverBullet.
5. **Frontmatter YAML enriquecido**: Metadados com `tags` padronizadas a partir de vocabulário controlado extensível, `project`, datas, referência ao segmento original (`segment_ref`), notas complementares (`related_notes`) e `source`.
6. **Rastreamento e Idempotência**: Manifesto dedicado `vault/.curated.json` com histórico de descartes e flag `--force`.

#### Métricas de sucesso

- 100% dos turnos operacionais triviais identificados ("sim", "1", "prossiga") descartados sem criação de arquivos de nota.
- 100% das notas em `vault/notas/` geradas com YAML frontmatter válido e campos obrigatórios preenchidos.
- 100% de conformidade com os templates de diagramação acordados (FAQ e Pair-Programming).
- 0 dependências externas (estritamente Python 3 standard library).
- 0 chamadas redundantes em segmentos já curados ou descartados em execuções incrementais normais.

### 2. Research e esclarecimentos

#### Researchs executados

- **R-001**: Análise do modelo de dados e Live Queries do SilverBullet → SilverBullet indexa atributos declarados no YAML frontmatter de arquivos Markdown (`name`, `tags`, `project`, `created`, `category`). Uma estrutura plana em `vault/notas/` permite máxima flexibilidade para consultas dinâmicas (`page where tag = "..."`) sem rigidez de hierarquias de pastas.
- **R-002**: Padrões da skill `humanizer` (`.agents/skills/humanizer/SKILL.md`) → Identificação de vícios de IA a serem eliminados: contrastes "não apenas X, mas Y", introduções pomposas, conclusões moralistas, travessões excessivos e vocabulário promocional. Síntese em tópicos objetivos orientada a um desenvolvedor de nível Júnior.
- **R-003**: Estrutura dos segmentos de entrada → Arquivos `vault/segments/<user>/<session_id>/000X.md` possuem frontmatter com `session_id`, `turn`, `timestamp`, `start_step`, `end_step` e seções `# Entrada` e `# Resposta`.

#### Fontes e contexto consultados

- Código do segmenter: `src/chats2notes/segmenter.py`
- Skill Humanizer: `.agents/skills/humanizer/SKILL.md`
- Perfil do usuário: `.specsfy/USER-PROFILE.md`
- Especificações anteriores: `specs/completed/0001-...` e `specs/completed/0003-...`

#### Documentação consultada

- Python 3 Standard Library: `json`, `pathlib`, `re`, `argparse`, `dataclasses`, `datetime`.
- SilverBullet Documentation: Frontmatter Attributes, Live Queries and Page Naming conventions.

#### Artefatos de pesquisa armazenados

- `specs/draft/0004-curadoria-e-notas-humanizadas/research/silverbullet/`: Convenções de Live Queries e atributos frontmatter do SilverBullet para notas autossuficientes.

#### Dúvidas respondidas

- **Q**: Como organizar as notas no disco? → **A**: Estrutura 100% plana na raiz de `vault/notas/` sem subpastas, utilizando Title Case nos nomes de arquivos e diferenciando por tags e metadados.
- **Q**: Como tratar colisão de nomes de notas? → **A**: Adicionar sufixo numérico de desambiguação `(2)`, `(3)`.
- **Q**: Como rastrear segmentos já processados ou descartados? → **A**: Manifesto dedicado `vault/.curated.json` com lista de segmentos avaliados e descartados, e flag `--force` para reprocessamento.
- **Q**: Como categorizar e diagramar os conteúdos? → **A**: Dois formatos estritos: FAQ (geral, com resposta enxuta Jr em bullets) e Pair-Programming (frameworks, com pergunta limpa, resposta escolhida e alternativas originais completas).
- **Q**: Como atribuir tags? → **A**: Vocabulário controlado a partir de lista base extensível do projeto (`git`, `linux`, `python`, `automação`, `specsfy`, etc.) mais a tag estrutural (`faq` ou `pair-programming`).

#### Dúvidas abertas

- Nenhuma dúvida bloqueante para a consolidação deste escopo.

### 3. Escopo e atores

#### Incluído

- Módulo de curadoria e síntese (`chats2notes.curator`).
- Classificador de tipo de nota (`faq`, `pair-programming` ou `ruído descartável`).
- Gerador de títulos em Title Case com desambiguação numérica em caso de colisão.
- Diagramador de notas FAQ (com resposta enxuta em tópicos conforme skill `humanizer`).
- Diagramador de notas Pair-Programming (com pergunta limpa, resposta escolhida e alternativas completas).
- Gerador de YAML frontmatter padronizado para Live Queries do SilverBullet.
- Desdobrador de perguntas compostas independentes com referências cruzadas (`related_notes`).
- Gerenciador de manifesto de curadoria (`vault/.curated.json`) com suporte a memória de descarte e flag `--force`.
- Subcomando CLI `chats2notes curate` e parâmetros de diretórios.

#### Fora de escopo

- Conexão HTTP direta a provedores externos de IA (Gemini API, OpenAI API, Ollama) — deliberadamente fatiado para refinamento e implementação posterior, mantendo esta fatia focada no motor de curadoria, regras, prompts e diagramação.
- Ingestão de chats do NotebookLM (registrado no roadmap).
- Reorganização de bases legadas do SilverBullet/Obsidian ou migração de Notion/Evernote (registrado no roadmap).
- Interface web ou servidor HTTP.

#### Atores

- **Desenvolvedor**: Executa `chats2notes curate` ou utiliza a rotina assistida no chat para transformar segmentos fatiados em notas atômicas organizadas para seu segundo cérebro no SilverBullet/Obsidian.

### 4. Princípios e restrições do projeto

- **PR-001**: **Zero Dependências Externas**: O motor de curadoria deve funcionar estritamente com a standard library do Python 3.
- **PR-002**: **Conformidade Humanizer**: As respostas sintetizadas devem ser rigorosamente limpas de vícios e clichês de IA (sem introduções encenadas, sem fórmulas "não apenas X mas Y", sem travessões excessivos e com bullets diretos para Dev Júnior).
- **PR-003**: **Isolamento de Estado**: O estado da curadoria reside exclusivamente em `vault/.curated.json`, sem modificar `state.json` nem `vault/raw/`.
- **PR-004**: **SilverBullet First**: Arquivos e atributos frontmatter são projetados para máxima compatibilidade com SilverBullet, permanecendo 100% interoperáveis com Obsidian.

### 5. Histórias de usuário

#### US-001 — Diagramação de Notas FAQ e Pair-Programming Atômicas (P1)

Como desenvolvedor, quero que perguntas conceituais e interações de frameworks sejam diagramadas em notas atômicas com formatos específicos (FAQ e Pair-Programming) com respostas enxutas e alternativas completas, para compor minha enciclopédia pessoal e segundo cérebro no SilverBullet.

**Por que P1**: É o formato central de consulta e registro da base de conhecimento.
**Teste independente**: Processar segmentos de FAQ e Pair-Programming e verificar a presença de títulos adequados, frontmatter YAML, bullets enxutos, divisor `---` e alternativas originais completas.
**Requisitos**: FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003

#### US-002 — Filtragem de Ruído Operacional e Desdobramento de Perguntas (P1)

Como desenvolvedor, quero que mensagens triviais e operacionais ("sim", "1", "prossiga") sejam ignoradas pelo curador e perguntas compostas sejam desdobradas em notas distintas, para manter meu vault limpo, atômico e de alto valor.

**Por que P1**: Evita a poluição do vault com mensagens inúteis e assegura atomicidade.
**Teste independente**: Submeter segmentos contendo confirmações curtas comprovando descarte sem notas, e submeter perguntas compostas comprovando geração de notas distintas com links mútuos.
**Requisitos**: FR-001, FR-002, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003

#### US-003 — Rastreamento Incremental via Manifesto e Interface CLI (P1)

Como desenvolvedor, quero que o comando `chats2notes curate` utilize `vault/.curated.json` para processar apenas segmentos inéditos, mantendo memória de descartes e permitindo reprocessamento via `--force`, para otimizar meu tempo e garantir idempotência.

**Por que P1**: Permite automação incremental confiável em scripts e terminal com zero chamadas redundantes.
**Teste independente**: Executar `chats2notes curate`, verificar notas geradas, reexecutar sem `--force` comprovando zero trabalho duplicado, e reexecutar com `--force` comprovando regeneração consistente.
**Requisitos**: FR-001, FR-002, FR-005, FR-006, NFR-001, NFR-002, NFR-003

### 6. Cenários BDD de aceite

#### AC-001 — Curadoria de diálogo geral em nota FAQ atômica

**Cobre**: US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-003 @FR-004 @FR-005 @NFR-001 @NFR-002 @NFR-003 @AC-001
Feature: Diagramação de nota FAQ atômica

  Scenario: Segmento técnico geral convertido em nota FAQ
    Given que existe um arquivo de segmento em "vault/segments/user_a/sess_1/0001.md" contendo uma dúvida sobre configuração de SSH no Debian
    When o motor de curadoria processa o segmento
    Then é criado o arquivo "vault/notas/Como configurar SSH no Debian.md"
    And o arquivo possui frontmatter YAML com "tags", "created", "chat_date", "segment_ref" e "source"
    And o corpo da nota contém a pergunta resumida destacada
    And a resposta inicial é apresentada em tópicos enxutos para Dev Júnior sem prolixidade
    And existe um divisor horizontal "---"
    And abaixo do divisor constam a pergunta original completa e a resposta original completa
```

#### AC-002 — Curadoria de etapa de framework em nota Pair-Programming

**Cobre**: US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-003 @FR-004 @FR-005 @NFR-001 @NFR-002 @NFR-003 @AC-002
Feature: Diagramação de nota Pair-Programming

  Scenario: Segmento de pergunta numerada de framework convertido em nota de pair-programming
    Given que existe um segmento contendo uma pergunta numerada de setup do framework Specsfy com alternativas e resposta selecionada
    When o motor de curadoria processa o segmento
    Then é criado o arquivo de nota com título no padrão "<projeto> - specsfy - Pergunta 1.md"
    And o frontmatter YAML possui a tag "pair-programming" e o atributo "project" preenchido
    And o corpo contém a pergunta resumida sem alternativas e a resposta escolhida destacada
    And após o divisor "---" constam a pergunta completa com todas as alternativas originais
```

#### AC-003 — Descarte de turnos operacionais e triviais com memória de descarte

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-006 @NFR-001 @NFR-002 @NFR-003 @AC-003
Feature: Filtragem de ruído operacional

  Scenario: Turno trivial contendo apenas confirmação operacional
    Given que existe um segmento em "vault/segments/user_a/sess_1/0002.md" com a entrada "sim" e resposta "Entendido, prosseguindo..."
    When o motor de curadoria processa o segmento
    Then nenhum arquivo de nota é gerado em "vault/notas/" para esse segmento
    And o manifesto "vault/.curated.json" registra o segmento como descartado por ruído operacional
```

#### AC-004 — Desdobramento de pergunta múltipla independente

**Cobre**: US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-003 @FR-004 @FR-005 @NFR-001 @NFR-002 @NFR-003 @AC-004
Feature: Desdobramento de perguntas múltiplas

  Scenario: Segmento com duas perguntas técnicas independentes
    Given que existe um segmento contendo duas perguntas distintas sobre git e docker que possuem compreensão autônoma
    When o motor de curadoria processa o segmento
    Then são criadas duas notas distintas em "vault/notas/"
    And cada nota referencia a outra no atributo "related_notes" do frontmatter YAML
```

#### AC-005 — Desambiguação numérica em colisão de nomes de notas

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-005, FR-006, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-005 @FR-006 @NFR-001 @NFR-002 @NFR-003 @AC-005
Feature: Desambiguação de nomes de notas

  Scenario: Criação de nota com título idêntico a uma nota já existente
    Given que já existe o arquivo "vault/notas/Como listar branches no Git.md"
    When um novo segmento de outra sessão gera o mesmo título "Como listar branches no Git"
    Then o novo arquivo é gravado como "vault/notas/Como listar branches no Git (2).md"
    And a nota anterior permanece intacta
```

#### AC-006 — Idempotência, manifesto e execução do subcomando CLI curate

**Cobre**: US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003

```gherkin
@US-001 @US-002 @US-003 @FR-001 @FR-002 @FR-006 @NFR-001 @NFR-002 @NFR-003 @AC-006
Feature: Rastreamento incremental, idempotência e interface CLI

  Scenario: Execução do comando curate respeitando o manifesto e suporte a force
    Given que uma sessão já foi curada e possui registros em "vault/.curated.json"
    When o comando "chats2notes curate --segments-dir <dir> --notes-dir <dir>" é executado
    Then nenhum segmento já curado ou descartado é reprocessado
    And quando executado com a flag "--force", todos os segmentos são reprocessados de forma consistente
```

### 7. Requisitos

#### Funcionais

- **FR-001**: O sistema deve ler segmentos de `vault/segments/` e analisar seu conteúdo para categorização em `faq`, `pair-programming` ou `ruído descartável`.
- **FR-002**: O sistema deve descartar mensagens triviais e operacionais ("sim", "1", "prossiga", etc.), registrando o descarte no manifesto sem gerar arquivos de nota.
- **FR-003**: O sistema deve diagramar notas nos formatos especializados: FAQ (título curto, pergunta destacada, resposta enxuta Jr em bullets, divisor `---`, pergunta completa e resposta completa) e Pair-Programming (`<projeto> - <framework> - Pergunta <N>`, pergunta sem alternativas, resposta escolhida, divisor `---` e alternativas originais completas).
- **FR-004**: O sistema deve gerar frontmatter YAML válido contendo `tags` (vocabulario controlado extensível + tag de categoria), `project` (se aplicável), `created`, `chat_date`, `segment_ref`, `related_notes` e `source`.
- **FR-005**: O sistema deve salvar as notas na raiz de `vault/notas/` com nomes legíveis em Title Case, aplicando sufixo numérico `(2)` em caso de colisão de nomes.
- **FR-006**: O sistema deve manter o manifesto `vault/.curated.json` para rastrear segmentos processados, notas geradas e ruídos descartados, e fornecer o subcomando CLI `chats2notes curate` com opções `--segments-dir`, `--notes-dir` e `--force`.

#### Não funcionais

- **NFR-001**: **Zero dependências externas**: Implementação 100% em biblioteca padrão do Python 3 (stdlib). **Verificação**: Inspeção de imports e execução em ambiente limpo sem pip.
- **NFR-002**: **Conformidade Humanizer**: As respostas geradas no topo das notas não devem conter clichês de IA (not-X-but-Y, introduções encenadas, conclusões moralistas). **Verificação**: Testes unitários com assertions sobre padrões proibidos.
- **NFR-003**: **Idempotência**: Execuções consecutivas sobre o mesmo acervo de segmentos não geram duplicatas nem alteram notas prévias. **Verificação**: Testes de re-execução e conferência de integridade dos arquivos e do manifesto.

#### Erros e casos-limite

- Segmento com Markdown corrompido ou sem frontmatter → Registrar aviso em log e ignorar o segmento sem interromper a execução global.
- Segmento vazio ou incompleto → Descartar silenciosamente e registrar no manifesto.
- Pasta `vault/notas/` inexistente → Criar automaticamente com permissões adequadas.
- Manifesto `vault/.curated.json` corrompido → Fazer backup seguro e reconstruir a partir das notas existentes no disco.

## Ato II — Projetar e provar

### 8. Plano técnico

#### Contexto existente

O repositório possui:
- `src/chats2notes/segmenter.py`: Divide transcripts brutos em pares ordenados `0001.md` e auditoria `0001.audit.json`.
- `src/chats2notes/cli.py`: Interface CLI construída com `argparse` da biblioteca padrão.
- Suíte de testes em `tests/` executada via `python3 -m unittest discover tests`.

#### Arquitetura e módulos

- `src/chats2notes/curator.py`: Motor de curadoria contendo:
  - `CuratorEngine`: Orquestrador central de leitura de segmentos, filtragem de ruído e persistência de notas.
  - `NoteDiagrammer`: Formata os templates específicos de FAQ e Pair-Programming com frontmatter YAML.
  - `CuratedManifest`: Gerenciador do arquivo `vault/.curated.json` com controle de marca d'água e memória de descarte.
  - `TagTaxonomy`: Normalizador de tags com vocabulário controlado extensível.
- `src/chats2notes/cli.py`: Adição do subcomando `curate`.

#### Migrations

- Não aplicável (persistência local baseada em arquivos Markdown e JSON).

#### Models

- `CuratedNote`: Dataclass representando a nota gerada (título, categoria, frontmatter, corpo resumido, corpo completo, caminho de saída).
- `CuratedManifestEntry`: Dataclass para os registros em `vault/.curated.json`.

#### Controllers e casos de uso

- `chats2notes curate`: Use case de processamento em lote dos segmentos para notas atômicas.

#### Views e experiência

- Não aplicável (linha de comando).

#### Queries e repositórios

- Leitura em `vault/segments/<user>/<session_id>/` e escrita atômica em `vault/notas/`.

#### Jobs e processamento assíncrono

- Não aplicável.

#### Estrutura de arquivos

```text
specs/draft/0004-curadoria-e-notas-humanizadas/
  spec.md
  research/
src/chats2notes/
  curator.py
  cli.py
tests/
  test_curator.py
  test_curator_cli.py
```

### 9. Modelo de dados

#### Entidades

| Entidade | Identidade | Atributos e regras | Relações |
| --- | --- | --- | --- |
| `CuratedNote` | `filename` | `title`, `category`, `tags`, `project`, `created`, `chat_date`, `segment_ref`, `related_notes`, `source`, `summary_question`, `summary_answer`, `full_question`, `full_answer` | Derivada de um `SegmentTurn` |
| `CuratedManifest` | `path` | `sessions` (dicionário de session_id -> segmentos processados e descartados), `notes` (lista de arquivos gerados) | Mapeia `vault/segments/` para `vault/notas/` |

#### Estados e transições

| Entidade | Estado atual | Evento | Próximo estado | Invariantes |
| --- | --- | --- | --- | --- |
| `Segment` | Descoberto | Curadoria | Nota Criada | Gera arquivo `.md` em `vault/notas/` |
| `Segment` | Descoberto | Detecção de ruído | Descartado | Registrado no manifesto sem gerar nota |

#### Migração e retenção

- Não aplicável.

### 10. Interfaces e contratos

#### Interface para pessoas

- **Há interface para pessoas**: Não — ferramenta de linha de comando (CLI) sem interface gráfica web.

#### Stack e convenções de interface

- Interface CLI via `argparse` em Python standard library.

#### Telas e responsabilidades

- Não aplicável.

#### Fluxo de informação e navegação

- Não aplicável.

#### Menus e navegação principal

- Não aplicável.

#### Formulários e ações

- Não aplicável.

#### Composição e disposição

- Não aplicável.

#### Blocos React e componentes selecionados

- Não aplicável.

#### Estados e acessibilidade

- Não aplicável.

#### Contrato CRUD

- Não aplicável.

#### Revisão visual durante o desenvolvimento

- Não aplicável (projeto de backend/CLI sem interface visual gráfica).

#### APIs expostas

- Não aplicável.

#### APIs externas utilizadas

- Nenhuma (deliberadamente fatiado para refinamento e implementação posterior, mantendo zero dependências externas nesta entrega).

#### Documentação das APIs consultadas

- Python Standard Library `json`, `pathlib`, `argparse`.

#### Eventos e outros contratos

- Não aplicável.

### 11. Estratégia TDD

- **Unidade**: Testes de detecção de ruído, formatação de templates FAQ e Pair-Programming, e normalização de tags em `tests/test_curator.py`.
- **Integração/contrato**: Testes de geração de arquivos Markdown em disco com frontmatter YAML válido e manipulação de `vault/.curated.json`.
- **BDD/aceite**: Testes CLI executando `chats2notes curate` cobrindo cenários AC-001 a AC-006 em `tests/test_curator_cli.py`.
- **Runner TDD**: `python3 -m unittest discover tests`.
- **E2E**: Execução completa sobre segmentos de teste em diretório temporário gerando notas limpas.
- **Verificação manual**: Inspeção das notas geradas no SilverBullet ou visualizador Markdown.

#### Evidência RED-GREEN-REFACTOR

| IDs | BDD de referência | Teste TDD informado pelo BDD | RED observado | GREEN observado | Refactor/regressão |
| --- | --- | --- | --- | --- | --- |
| US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003, AC-001 | AC-001 | SPECSFY:AC-001 em tests/test_curator.py | ModuleNotFoundError: No module named 'chats2notes.curator' | Ran 5 tests in 0.012s - OK | Ran 32 tests in 0.191s - OK |
| US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003, AC-002 | AC-002 | SPECSFY:AC-002 em tests/test_curator.py | ModuleNotFoundError: No module named 'chats2notes.curator' | Ran 5 tests in 0.012s - OK | Ran 32 tests in 0.191s - OK |
| US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003, AC-003 | AC-003 | SPECSFY:AC-003 em tests/test_curator.py | ModuleNotFoundError: No module named 'chats2notes.curator' | Ran 5 tests in 0.012s - OK | Ran 32 tests in 0.191s - OK |
| US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003, AC-004 | AC-004 | SPECSFY:AC-004 em tests/test_curator.py | ModuleNotFoundError: No module named 'chats2notes.curator' | Ran 5 tests in 0.012s - OK | Ran 32 tests in 0.191s - OK |
| US-001, US-002, US-003, FR-001, FR-002, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-005 | AC-005 | SPECSFY:AC-005 em tests/test_curator.py | ModuleNotFoundError: No module named 'chats2notes.curator' | Ran 5 tests in 0.012s - OK | Ran 32 tests in 0.191s - OK |
| US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003, AC-006 | AC-006 | SPECSFY:AC-006 em tests/test_curator_cli.py | ArgumentError: invalid choice: 'curate' | Ran 1 test in 0.014s - OK | Ran 32 tests in 0.191s - OK |

### 12. Plano de testes e rastreabilidade

| Requisito | Cenário BDD | Nível | Arquivo/comando esperado | Evidência |
| --- | --- | --- | --- | --- |
| FR-001 | AC-001 | Unidade | tests/test_curator.py | Passed |
| FR-001 | AC-002 | Unidade | tests/test_curator.py | Passed |
| FR-001 | AC-003 | Unidade | tests/test_curator.py | Passed |
| FR-001 | AC-004 | Unidade | tests/test_curator.py | Passed |
| FR-001 | AC-005 | Unidade | tests/test_curator.py | Passed |
| FR-001 | AC-006 | Unidade | tests/test_curator_cli.py | Passed |
| FR-002 | AC-003 | Unidade | tests/test_curator.py | Passed |
| FR-002 | AC-005 | Unidade | tests/test_curator.py | Passed |
| FR-002 | AC-006 | Unidade | tests/test_curator_cli.py | Passed |
| FR-003 | AC-001 | Integração | tests/test_curator.py | Passed |
| FR-003 | AC-002 | Integração | tests/test_curator.py | Passed |
| FR-003 | AC-004 | Integração | tests/test_curator.py | Passed |
| FR-004 | AC-001 | Unidade | tests/test_curator.py | Passed |
| FR-004 | AC-002 | Unidade | tests/test_curator.py | Passed |
| FR-004 | AC-004 | Unidade | tests/test_curator.py | Passed |
| FR-005 | AC-001 | Integração | tests/test_curator.py | Passed |
| FR-005 | AC-002 | Integração | tests/test_curator.py | Passed |
| FR-005 | AC-004 | Integração | tests/test_curator.py | Passed |
| FR-005 | AC-005 | Integração | tests/test_curator.py | Passed |
| FR-006 | AC-003 | Integração | tests/test_curator.py | Passed |
| FR-006 | AC-005 | Integração | tests/test_curator.py | Passed |
| FR-006 | AC-006 | CLI | tests/test_curator_cli.py | Passed |
| NFR-001 | AC-001 | Unidade | tests/test_curator.py | Passed |
| NFR-001 | AC-002 | Unidade | tests/test_curator.py | Passed |
| NFR-001 | AC-003 | Unidade | tests/test_curator.py | Passed |
| NFR-001 | AC-004 | Unidade | tests/test_curator.py | Passed |
| NFR-001 | AC-005 | Unidade | tests/test_curator.py | Passed |
| NFR-001 | AC-006 | CLI | tests/test_curator_cli.py | Passed |
| NFR-002 | AC-001 | Unidade | tests/test_curator.py | Passed |
| NFR-002 | AC-002 | Unidade | tests/test_curator.py | Passed |
| NFR-002 | AC-003 | Unidade | tests/test_curator.py | Passed |
| NFR-002 | AC-004 | Unidade | tests/test_curator.py | Passed |
| NFR-002 | AC-005 | Unidade | tests/test_curator.py | Passed |
| NFR-002 | AC-006 | CLI | tests/test_curator_cli.py | Passed |
| NFR-003 | AC-001 | Integração | tests/test_curator.py | Passed |
| NFR-003 | AC-002 | Integração | tests/test_curator.py | Passed |
| NFR-003 | AC-003 | Integração | tests/test_curator.py | Passed |
| NFR-003 | AC-004 | Integração | tests/test_curator.py | Passed |
| NFR-003 | AC-005 | Integração | tests/test_curator.py | Passed |
| NFR-003 | AC-006 | CLI | tests/test_curator_cli.py | Passed |

### 13. Validações

#### Gate do Ato I — Definição

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-04-validate/scripts/validate_spec.mjs specs/defined/0004-curadoria-e-notas-humanizadas/spec.md`
- **Achados**: Aprovado formalmente pelo usuário. Todos os requisitos US, FR e NFR cobertos por no mínimo 3 cenários BDD (AC-001 a AC-006). Zero dependências externas e formato Specsfy/2.0 estritamente verificado.

#### Gate do Ato II — Plano

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-05-tasks/scripts/validate_tasks.mjs specs/planned/0004-curadoria-e-notas-humanizadas/spec.md`
- **Achados**: 8 tarefas canônicas com 5 predecessores TDD concluídos (T001 a T005), 18/18 IDs rastreáveis cobertos e RED observado comprovado nos testes.

#### Gate do Ato III — Entrega

- **Resultado**: Passed
- **Comando**: `node .agents/skills/specsfy-06-tdd-bdd/scripts/check_traceability.mjs specs/in-progress/0004-curadoria-e-notas-humanizadas/spec.md .`
- **Achados**: 18/18 IDs cobertos em 12 arquivos de teste; 32 testes executados e passando sem regressões; comando real chats2notes curate processou 453 segmentos reais gerando 737 notas atômicas em vault/notas e manifesto vault/.curated.json.

### 14. Tarefas

#### Fase 1 — RED TDD informado pelo BDD

- [x] T001 [TEST] [TDD] [US-001] Criar teste falhando para AC-001 em tests/test_curator.py — Refs: US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003, AC-001 — Depends: none
  - [x] **PREP**: Ler AC-001 e preparar fixtures com segmento FAQ.
  - [x] **EXECUTE**: Escrever teste com marcador SPECSFY:AC-001 validando diagrama FAQ.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando de teste e causa do RED.
  - [x] **IMPROVE**: Assegurar cobertura de bullets e divisor.

- [x] T002 [TEST] [TDD] [US-001] Criar teste falhando para AC-002 em tests/test_curator.py — Refs: US-001, US-002, US-003, FR-001, FR-003, FR-004, FR-005, NFR-001, NFR-002, NFR-003, AC-002 — Depends: none
  - [x] **PREP**: Ler AC-002 e preparar fixture de pergunta de framework.
  - [x] **EXECUTE**: Escrever teste com marcador SPECSFY:AC-002 validando diagrama Pair-Programming.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e causa do RED.
  - [x] **IMPROVE**: Conferir padrão de título com projeto e etapa.

- [x] T003 [TEST] [TDD] [US-002] Criar teste falhando para AC-003 em tests/test_curator.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003, AC-003 — Depends: none
  - [x] **PREP**: Ler AC-003 e estruturar turnos com mensagens operacionais triviais.
  - [x] **EXECUTE**: Escrever teste com marcador SPECSFY:AC-003 validando descarte.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e causa do RED.
  - [x] **IMPROVE**: Conferir registro no manifesto sem gerar arquivo .md.

- [x] T004 [TEST] [TDD] [US-002] Criar teste falhando para AC-004 e AC-005 em tests/test_curator.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-004, AC-005 — Depends: none
  - [x] **PREP**: Ler AC-004 e AC-005 sobre desdobramento e colisão de nomes.
  - [x] **EXECUTE**: Escrever testes com marcadores SPECSFY:AC-004 e SPECSFY:AC-005.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e causa do RED.
  - [x] **IMPROVE**: Conferir sufixo de desambiguação numérica.

- [x] T005 [TEST] [TDD] [US-003] Criar teste falhando para AC-006 em tests/test_curator_cli.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003, AC-006 — Depends: none
  - [x] **PREP**: Ler AC-006 estruturando testes da CLI e manifesto.
  - [x] **EXECUTE**: Escrever testes com marcador SPECSFY:AC-006.
  - [x] **VERIFY**: Observar RED válido.
  - [x] **VISUAL**: Não aplicável (tarefa exclusivamente de teste sem interface visual).
  - [x] **EVIDENCE**: Registrar comando e causa do RED.
  - [x] **IMPROVE**: Validar opções --segments-dir, --notes-dir e --force.

#### Fase 2 — Implementação do Motor de Curadoria

- [x] T006 [CODE] [US-001] Implementar motor de curadoria e diagramadores em src/chats2notes/curator.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006 — Depends: T001, T002, T003, T004, T005
  - [x] **PREP**: Confirmar contratos de dados e estado RED das tarefas T001 a T005.
  - [x] **EXECUTE**: Implementar CuratorEngine, NoteDiagrammer e CuratedManifest em src/chats2notes/curator.py.
  - [x] **VERIFY**: Executar PYTHONPATH=src python3 -m unittest tests/test_curator.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável (componente de backend/script sem interface gráfica).
  - [x] **EVIDENCE**: Registrar testes passando e arquivos criados.
  - [x] **IMPROVE**: Otimizar geração de YAML e tratamento de ruído.
  <!-- specsfy:evidence {"task":"T006","refs":["US-001","US-002","US-003","FR-001","FR-002","FR-003","FR-004","FR-005","FR-006","NFR-001","NFR-002","NFR-003","AC-001","AC-002","AC-003","AC-004","AC-005","AC-006"],"files":["src/chats2notes/curator.py"],"commands":[{"run":"PYTHONPATH=src python3 -m unittest tests/test_curator.py","exit":0}]} -->

- [x] T007 [CODE] [US-003] Integrar subcomando curate na CLI em src/chats2notes/cli.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-006, NFR-001, NFR-002, NFR-003, AC-006 — Depends: T005, T006
  - [x] **PREP**: Inspecionar src/chats2notes/cli.py e subcomandos existentes.
  - [x] **EXECUTE**: Adicionar subparser curate com argumentos --segments-dir, --notes-dir e --force.
  - [x] **VERIFY**: Executar PYTHONPATH=src python3 -m unittest tests/test_curator_cli.py e observar GREEN.
  - [x] **VISUAL**: Não aplicável (interface de linha de comando puramente textual).
  - [x] **EVIDENCE**: Registrar execução do comando help e testes unitários.
  - [x] **IMPROVE**: Adicionar mensagens claras em português com contadores de notas geradas e ruídos descartados.
  <!-- specsfy:evidence {"task":"T007","refs":["US-001","US-002","US-003","FR-001","FR-002","FR-006","NFR-001","NFR-002","NFR-003","AC-006"],"files":["src/chats2notes/cli.py"],"commands":[{"run":"PYTHONPATH=src python3 -m unittest tests/test_curator_cli.py","exit":0}]} -->

#### Fase 3 — Qualidade e Documentação

- [x] T008 [TEST] Executar regressão completa e verificar rastreabilidade em tests/test_curator.py — Refs: US-001, US-002, US-003, FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-003, AC-001, AC-002, AC-003, AC-004, AC-005, AC-006 — Depends: T006, T007
  - [x] **PREP**: Levantar todos os testes do projeto.
  - [x] **EXECUTE**: Executar PYTHONPATH=src python3 -m unittest discover tests.
  - [x] **VERIFY**: Garantir que 100% dos testes passam sem regressões.
  - [x] **VISUAL**: Não aplicável (projeto sem interface visual).
  - [x] **EVIDENCE**: Registrar contagem total de testes e tempo de execução.
  - [x] **IMPROVE**: Documentar comando chats2notes curate no README.md.

### 15. Ordem de execução

- Caminho crítico: T001/T002/T003/T004/T005 → T006 → T007 → T008.
- Tarefas paralelas: T001 a T005 podem ser desenvolvidas em paralelo.
- Estratégia de MVP: Entrega do motor de curadoria, diagramação FAQ e Pair-Programming, filtragem de ruído, rastreamento via manifesto e comando CLI dedicado.

## Ato III — Entregar e validar

### 16. Dependências, riscos e suposições

#### Dependências

- `vault/segments/` populado com segmentos gerados por `chats2notes segment`.

#### Riscos

- Ruídos atípicos não capturados pelas heurísticas iniciais → Mitigado pela lista extensível de padrões operacionais e revisão contínua.

#### Suposições

- O diretório `vault/` e seus conteúdos permanecem estritamente ignorados no `.gitignore`.

### 17. Decisões

- **DEC-001**: Fatiamento Incremental da Fase 3 — Implementar primeiramente o motor de curadoria, heurísticas de ruído, diagramação de templates (FAQ e Pair-Programming) e manifesto de rastreamento com execução CLI/assistida local, postergando chamadas de rede diretas para fatiamento subsequente.
- **DEC-002**: Estrutura 100% Plana em `vault/notas/` — Todas as notas residem na raiz do diretório de notas sem subpastas, delegando filtros e agrupamentos para as Live Queries do SilverBullet por meio de atributos do YAML frontmatter.
- **DEC-003**: Nomes em Title Case com Desambiguação — Nomes de arquivos refletem o título com espaços (ex: `Como configurar SSH no Debian.md`), facilitando links `[[Wikilinks]]`, com sufixo `(2)` em caso de colisão.
- **DEC-004**: Manifesto Isolado `vault/.curated.json` — Separação completa do ciclo de vida de curadoria em relação ao `state.json` de sincronização, garantindo memória de descartes para não gastar chamadas repetidas.

### 18. Definition of Done

- [x] `Definition Gate` está `Passed`.
- [x] `Plan Gate` está `Passed`.
- [x] `Delivery Gate` está `Passed`.
- [x] Todos os cenários `AC` aplicáveis passam.
- [x] Todos os requisitos possuem evidência de verificação.
- [x] Todas as tarefas na seção 14 estão concluídas.
- [x] Testes e checks estáticos disponíveis passam.
